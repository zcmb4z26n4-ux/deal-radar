#!/usr/bin/env python3
"""
Deal Radar — collecteur de promos Steam avec historique de prix.

L'idée : Steam affiche "-50%", mais pas si c'est le meilleur prix jamais vu.
On garde l'historique nous-mêmes et on compare au plus bas observé.

Source : le moteur de recherche Steam (filtre "promotions"), qui renvoie
plusieurs milliers de jeux, contrairement à la vitrine "featured" (10 jeux).
API publique, sans clé.

Réglage principal : NB_JEUX ci-dessous.
"""
import json, urllib.request, datetime, pathlib, time, re, html as htmlmod

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
HIST_F = DATA / "historique.json"
DEALS_F = DATA / "deals.json"

# ─── RÉGLAGES ──────────────────────────────────────────────────────────────
NB_JEUX = 500        # combien de jeux suivre (100 = rapide, 1000 = ~2 min)
REMISE_MIN = 20      # ignorer les promos en dessous de X %
NOTE_MIN = 70        # ignorer les jeux sous X % d'avis positifs (0 = tout garder)
AVIS_MIN = 50        # ignorer les jeux avec moins de X avis (évite les inconnus)

# Ordre dans lequel Steam nous sert les jeux :
#   "globaltopsellers" = les plus vendus au monde → les gros titres connus
#   "topsellers"       = les plus vendus en France
#   "_ASC"             = pertinence Steam (proche des top sellers)
# ⚠️ NE PAS utiliser "Reviews_DESC" : ça trie par POURCENTAGE d'avis positifs,
#    pas par popularité. C'est ce qui faisait remonter des inconnus à 99 %.
CLASSEMENT = "globaltopsellers"

# Ne garder que les jeux disponibles en français.
# Écarte les titres asiatiques massifs (énormément d'avis grâce au marché
# chinois, mais sans intérêt pour un public francophone).
# Mets False pour revenir au catalogue mondial complet.
FRANCAIS_SEULEMENT = True

# Filtre de secours sur le titre : écarte les jeux dont le nom est
# majoritairement en caractères chinois / japonais / coréens, même s'ils
# déclarent une traduction française.
EXCLURE_TITRES_CJK = True

# Jeux surveillés en permanence, même s'ils ne sont pas dans le classement.
# Ils sont vérifiés un par un à chaque passage : dès qu'ils passent en promo,
# ils apparaissent sur le site. Ajoute les tiens (l'ID est dans l'URL Steam :
# store.steampowered.com/app/1091500/ → 1091500).
SURVEILLES = [
    1091500,   # Cyberpunk 2077
    1245620,   # ELDEN RING
    1174180,   # Red Dead Redemption 2
    3405690,   # EA SPORTS FC 26
    1085660,   # Destiny 2
    271590,    # GTA V
    292030,    # The Witcher 3
    1086940,   # Baldur's Gate 3
    1938090,   # Call of Duty
    2358720,   # Black Myth: Wukong
]
# ───────────────────────────────────────────────────────────────────────────

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
TODAY = datetime.date.today().isoformat()
BASE = ("https://store.steampowered.com/search/results/"
        "?query&start={start}&count=100&dynamic_data=&filter=" + CLASSEMENT +
        "&specials=1&infinite=1&cc=fr&l=french"
        + ("&supportedlang=french" if FRANCAIS_SEULEMENT else ""))


def titre_cjk(nom):
    """Vrai si le titre est majoritairement en chinois/japonais/coréen."""
    cjk = sum(1 for c in nom if
              '\u4e00' <= c <= '\u9fff' or      # idéogrammes chinois
              '\u3040' <= c <= '\u30ff' or      # hiragana / katakana
              '\uac00' <= c <= '\ud7af')        # hangul coréen
    lettres = sum(1 for c in nom if c.isalpha())
    return lettres > 0 and cjk / lettres > 0.3


def get_json(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def prix_en_float(txt):
    """'9,75€' → 9.75"""
    if not txt:
        return None
    t = txt.replace("\xa0", " ").replace("€", "").replace(",", ".").strip()
    t = re.sub(r"[^\d.]", "", t)
    try:
        return float(t)
    except ValueError:
        return None


def parser_page(html_txt):
    """Découpe le HTML de Steam en dictionnaires exploitables."""
    jeux = []
    # chaque résultat commence par <a href=... data-ds-appid=
    for bloc in html_txt.split('<a href=')[1:]:
        m_id = re.search(r'data-ds-appid="(\d+)"', bloc)
        if not m_id:
            continue
        appid = m_id.group(1)

        m_nom = re.search(r'<span class="title">(.*?)</span>', bloc, re.S)
        if not m_nom:
            continue
        nom = htmlmod.unescape(m_nom.group(1)).strip()

        if EXCLURE_TITRES_CJK and titre_cjk(nom):
            continue

        m_rem = re.search(r'data-discount="(\d+)"', bloc)
        remise = int(m_rem.group(1)) if m_rem else 0
        if remise < REMISE_MIN:
            continue

        m_final = re.search(r'<div class="discount_final_price">(.*?)</div>', bloc, re.S)
        m_orig = re.search(r'<div class="discount_original_price">(.*?)</div>', bloc, re.S)
        prix = prix_en_float(htmlmod.unescape(m_final.group(1))) if m_final else None
        prix_base = prix_en_float(htmlmod.unescape(m_orig.group(1))) if m_orig else None
        if prix is None or prix <= 0:
            continue  # jeux gratuits ou prix illisible

        # Note : "99 % des 6,373 évaluations ... sont positives."
        note = nb_avis = None
        m_tip = re.search(r'data-tooltip-html="(.*?)"', bloc, re.S)
        if m_tip:
            tip = htmlmod.unescape(m_tip.group(1))
            m_pct = re.search(r'(\d+)\s*%', tip)
            m_nb = re.search(r'des\s+([\d\s,\.]+)\s+évaluations', tip)
            if m_pct:
                note = int(m_pct.group(1))
            if m_nb:
                nb_avis = int(re.sub(r"[^\d]", "", m_nb.group(1)) or 0)

        if NOTE_MIN and note is not None and note < NOTE_MIN:
            continue
        if AVIS_MIN and nb_avis is not None and nb_avis < AVIS_MIN:
            continue

        m_img = re.search(r'<img src="(https://[^"]+?)"', bloc)
        m_date = re.search(r'<div class="search_released[^"]*">(.*?)</div>', bloc, re.S)

        jeux.append({
            "id": int(appid),
            "nom": nom,
            "prix": prix,
            "prix_base": prix_base,
            "remise": remise,
            "note": note,
            "avis": nb_avis,
            "sortie": htmlmod.unescape(m_date.group(1)).strip() if m_date else "",
            "image": m_img.group(1) if m_img else "",
        })
    return jeux


def collecter():
    tous, start, vus = [], 0, set()
    while len(tous) < NB_JEUX and start < 3000:
        d = get_json(BASE.format(start=start))
        page = parser_page(d.get("results_html", ""))
        if not page:
            break
        for j in page:
            if j["id"] not in vus:
                vus.add(j["id"])
                tous.append(j)
        total = d.get("total_count", "?")
        print(f"  page {start//100 + 1:>2} → {len(tous)} jeux retenus (sur {total} en promo)")
        start += 100
        time.sleep(1.0)   # on reste poli avec Steam
    return tous[:NB_JEUX]


def verifier_surveilles(deja_vus):
    """Interroge un par un les jeux de la liste SURVEILLES.

    Le classement des meilleures ventes ne contient que ~2000 jeux : un gros
    titre peut être en promo sans y figurer. Ce filet de sécurité garantit
    qu'on ne rate jamais une promo sur les jeux qui comptent pour toi.
    """
    trouves = []
    for appid in SURVEILLES:
        if appid in deja_vus:
            continue    # déjà récupéré par le classement
        try:
            url = (f"https://store.steampowered.com/api/appdetails?appids={appid}"
                   f"&cc=fr&l=french")
            d = get_json(url)
            bloc = d.get(str(appid), {})
            if not bloc.get("success"):
                continue
            g = bloc["data"]
            p = g.get("price_overview")
            if not p or p.get("discount_percent", 0) < REMISE_MIN:
                continue    # pas en promo (ou promo trop faible)

            trouves.append({
                "id": appid,
                "nom": g["name"],
                "prix": p["final"] / 100,
                "prix_base": p["initial"] / 100,
                "remise": p["discount_percent"],
                "note": None,
                "avis": None,
                "sortie": g.get("release_date", {}).get("date", ""),
                "image": g.get("header_image", ""),
            })
            print(f"  ★ surveillé en promo : {g['name']} -{p['discount_percent']}%")
        except Exception:
            pass
        time.sleep(1.0)
    return trouves


def main():
    hist = json.loads(HIST_F.read_text(encoding="utf-8")) if HIST_F.exists() else {}

    print(f"Collecte des promos Steam (objectif {NB_JEUX} jeux)...")
    jeux = collecter()

    print(f"\nVérification des {len(SURVEILLES)} jeux surveillés...")
    extras = verifier_surveilles({j["id"] for j in jeux})
    if extras:
        jeux = extras + jeux
    else:
        print("  (aucun en promo actuellement)")
    print()

    resultats = []
    for j in jeux:
        aid = str(j["id"])
        h = hist.setdefault(aid, {"nom": j["nom"], "prix": {}})
        h["prix"][TODAY] = j["prix"]

        valeurs = list(h["prix"].values())
        plus_bas = min(valeurs)
        releves = len(valeurs)

        if j["prix"] <= plus_bas:
            verdict, couleur = ("Plus bas historique", "#16a34a")
        elif j["prix"] <= plus_bas * 1.15:
            verdict, couleur = ("Proche du minimum", "#65a30d")
        elif j["remise"] >= 60:
            verdict, couleur = ("Grosse remise", "#0284c7")
        else:
            verdict, couleur = ("Promo classique", "#64748b")

        resultats.append({**j, "plus_bas": plus_bas, "releves": releves,
                          "verdict": verdict, "couleur": couleur})

    # Tri d'affichage : d'abord les vraies bonnes affaires, et à verdict égal
    # les jeux les plus connus (nombre d'avis) plutôt que la plus grosse remise.
    # Sans ça, un inconnu à -90% passe devant un AAA à -60%.
    ordre = {"Plus bas historique": 0, "Proche du minimum": 1,
             "Grosse remise": 2, "Promo classique": 3}
    resultats.sort(key=lambda x: (ordre[x["verdict"]], -(x.get("avis") or 0)))

    HIST_F.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")
    DEALS_F.write_text(json.dumps({
        "maj": datetime.datetime.now().isoformat(timespec="seconds"),
        "jeux": resultats,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"✓ {len(resultats)} jeux → data/deals.json")
    print(f"✓ historique : {len(hist)} jeux suivis au total")


if __name__ == "__main__":
    main()


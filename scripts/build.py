#!/usr/bin/env python3
"""Génère le site statique Deal Radar."""
import json, pathlib, datetime

# ─── RÉGLAGE ───────────────────────────────────────────────────────────────
SEUIL_POPULAIRE = 5000   # à partir de X avis, le jeu passe dans "Jeux populaires"
# ───────────────────────────────────────────────────────────────────────────

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data" / "deals.json").read_text(encoding="utf-8"))
SITE = ROOT / "site"
SITE.mkdir(exist_ok=True)

jeux = D["jeux"]
maj = datetime.datetime.fromisoformat(D["maj"])
maj_txt = maj.strftime("%d/%m/%Y à %Hh%M")

populaires = [j for j in jeux if (j.get("avis") or 0) >= SEUIL_POPULAIRE]
autres = [j for j in jeux if (j.get("avis") or 0) < SEUIL_POPULAIRE]

# Statistiques d'en-tête
remise_max = max((j["remise"] for j in jeux), default=0)
economie = round(sum((j.get("prix_base") or j["prix"]) - j["prix"] for j in jeux))
nb_verif = sum(1 for j in jeux if j["releves"] >= 3)


def espace_milliers(n):
    return f"{n:,}".replace(",", " ")


def carte(j, vedette=False):
    prix_base = j.get("prix_base")
    base = f"<s>{prix_base:.2f}€</s>" if prix_base else ""
    eco = f"<span class='eco'>−{prix_base - j['prix']:.2f}€</span>" if prix_base else ""

    releves = j["releves"]
    plein = min(releves, 5)
    points = "".join(f"<i class='{'on' if k < plein else ''}'></i>" for k in range(5))

    note = j.get("note")
    avis = j.get("avis")
    if note is not None:
        cls = "bon" if note >= 80 else ("moyen" if note >= 60 else "bof")
        av = f"<span class='av'>{espace_milliers(avis)} avis</span>" if avis else ""
        bloc_note = f"<div class='note {cls}'><b>{note}%</b>{av}</div>"
    else:
        bloc_note = "<div class='note vide'>Pas encore d'avis</div>"

    visuel = (f"<img src='{j['image']}' alt='' loading='lazy' decoding='async'>"
              if j.get("image") else "<div class='noimg'></div>")

    star = "<div class='star' title='Jeu populaire'>★</div>" if vedette else ""

    return f"""
  <article class="jeu{' vedette' if vedette else ''}" data-nom="{j['nom'].lower()}"
           data-prix="{j['prix']}" data-remise="{j['remise']}"
           data-note="{note or 0}" data-avis="{avis or 0}">
    <a class="visuel" href="https://store.steampowered.com/app/{j['id']}/" target="_blank" rel="noopener">
      {visuel}
      <span class="rem">−{j['remise']}%</span>
      {star}
    </a>
    <div class="corps">
      <h2 title="{j['nom']}">{j['nom']}</h2>
      {bloc_note}
      <div class="tarif">
        <div class="prix"><b>{j['prix']:.2f}€</b> {base}</div>
        {eco}
      </div>
      <div class="verdict" style="--c:{j['couleur']}">
        <span class="pastille"></span>{j['verdict']}
      </div>
      <div class="pied">
        <span class="bas-prix">Mini vu <b>{j['plus_bas']:.2f}€</b></span>
        <span class="jauge" title="{releves} relevé(s) de prix">{points}</span>
      </div>
    </div>
  </article>"""


html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Deal Radar — les vraies promos Steam en français</title>
<meta name="description" content="Suivi quotidien des prix Steam. On garde l'historique pour dire si une promo est réellement la meilleure offre, ou juste du marketing.">
<meta name="theme-color" content="#0a0e1a">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎯</text></svg>">
<style>
  :root{{
    --bg:#0a0e1a; --bg2:#111827; --card:#151d2e; --card2:#1a2437;
    --bord:#25314a; --txt:#e8edf7; --gris:#8b9ab5; --gris2:#5d6b87;
    --bleu:#3b9dff; --vert:#22c55e; --or:#fbbf24;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  html{{scroll-behavior:smooth}}
  body{{
    font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;
    background:var(--bg);color:var(--txt);
    -webkit-font-smoothing:antialiased;
    background-image:
      radial-gradient(900px 400px at 12% -8%, rgba(59,157,255,.13), transparent 60%),
      radial-gradient(700px 350px at 88% -12%, rgba(34,197,94,.09), transparent 60%);
    background-repeat:no-repeat;
  }}
  .wrap{{max-width:1340px;margin:0 auto;padding:0 20px}}

  /* ── EN-TÊTE ── */
  header{{padding:52px 0 30px}}
  .logo{{display:flex;align-items:center;gap:11px;margin-bottom:16px}}
  .logo .dot{{
    width:11px;height:11px;border-radius:50%;background:var(--vert);
    box-shadow:0 0 0 4px rgba(34,197,94,.16);animation:pulse 2.4s infinite;
  }}
  @keyframes pulse{{
    0%,100%{{box-shadow:0 0 0 4px rgba(34,197,94,.16)}}
    50%{{box-shadow:0 0 0 9px rgba(34,197,94,0)}}
  }}
  h1{{
    font-size:clamp(30px,5vw,46px);font-weight:800;letter-spacing:-1.4px;line-height:1.05;
    background:linear-gradient(102deg,#fff 20%,#7dc0ff 92%);
    -webkit-background-clip:text;background-clip:text;color:transparent;
  }}
  .accroche{{color:var(--gris);font-size:16.5px;max-width:620px;margin-top:12px}}
  .accroche b{{color:var(--txt);font-weight:600}}

  .stats{{display:flex;flex-wrap:wrap;gap:11px;margin-top:26px}}
  .stat{{
    background:linear-gradient(160deg,var(--card),var(--bg2));
    border:1px solid var(--bord);border-radius:13px;padding:13px 18px;min-width:118px;
  }}
  .stat b{{display:block;font-size:22px;font-weight:700;letter-spacing:-.6px;line-height:1.2}}
  .stat span{{font-size:11.5px;color:var(--gris2);text-transform:uppercase;letter-spacing:.7px}}
  .stat.v b{{color:var(--vert)}} .stat.b b{{color:var(--bleu)}} .stat.o b{{color:var(--or)}}

  /* ── ENCART EXPLICATIF ── */
  .info{{
    display:flex;gap:14px;align-items:flex-start;
    background:linear-gradient(102deg,rgba(59,157,255,.09),transparent 72%);
    border:1px solid var(--bord);border-left:3px solid var(--bleu);
    border-radius:0 14px 14px 0;padding:16px 20px;margin:30px 0 8px;
    font-size:14px;color:#c3cfe4;line-height:1.65;
  }}
  .info .ic{{font-size:19px;line-height:1.2}}
  .info b{{color:var(--txt)}}

  /* ── BARRE DE FILTRES ── */
  .barre{{
    position:sticky;top:0;z-index:50;display:flex;gap:9px;flex-wrap:wrap;
    padding:14px 0;margin:18px 0 6px;
    background:rgba(10,14,26,.88);backdrop-filter:blur(14px);
    border-bottom:1px solid var(--bord);
  }}
  .champ{{position:relative;flex:1;min-width:210px}}
  .champ .loupe{{position:absolute;left:13px;top:50%;transform:translateY(-50%);
                 color:var(--gris2);font-size:14px;pointer-events:none}}
  input,select{{
    background:var(--card);border:1px solid var(--bord);color:var(--txt);
    padding:10px 14px;border-radius:11px;font-size:14px;font-family:inherit;
    transition:border-color .16s,box-shadow .16s;
  }}
  input{{width:100%;padding-left:36px}}
  select{{cursor:pointer;padding-right:32px;appearance:none;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='11' height='7'%3E%3Cpath d='M1 1l4.5 4.5L10 1' stroke='%238b9ab5' stroke-width='1.6' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat:no-repeat;background-position:right 12px center}}
  input:focus,select:focus{{outline:none;border-color:var(--bleu);
    box-shadow:0 0 0 3px rgba(59,157,255,.16)}}
  input::placeholder{{color:var(--gris2)}}

  #compteur{{color:var(--gris2);font-size:13px;margin:12px 0 4px}}
  #compteur b{{color:var(--gris)}}

  /* ── SECTIONS ── */
  .section{{display:flex;align-items:center;gap:12px;margin:40px 0 18px}}
  .section h3{{font-size:19px;font-weight:700;letter-spacing:-.4px;white-space:nowrap}}
  .section .cpt{{
    background:var(--card);border:1px solid var(--bord);color:var(--gris);
    font-size:12px;padding:3px 10px;border-radius:20px;white-space:nowrap;
  }}
  .section .trait{{flex:1;height:1px;background:linear-gradient(90deg,var(--bord),transparent)}}

  /* ── GRILLE ── */
  .grid{{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(250px,1fr))}}
  .jeu{{
    background:var(--card);border:1px solid var(--bord);border-radius:15px;
    overflow:hidden;display:flex;flex-direction:column;
    transition:transform .16s ease,border-color .16s,box-shadow .16s;
  }}
  .jeu:hover{{transform:translateY(-3px);border-color:#3a4a6b;
              box-shadow:0 12px 32px -12px rgba(0,0,0,.7)}}
  .jeu.vedette{{
    border-color:rgba(59,157,255,.42);
    background:linear-gradient(168deg,var(--card2),var(--card));
  }}
  .jeu.vedette:hover{{border-color:var(--bleu);
    box-shadow:0 14px 38px -12px rgba(59,157,255,.32)}}

  .visuel{{position:relative;display:block;line-height:0;background:var(--bg2)}}
  .visuel img,.noimg{{width:100%;height:112px;object-fit:cover;display:block}}
  .vedette .visuel img{{height:142px}}
  .noimg{{background:linear-gradient(135deg,var(--bg2),var(--card2))}}
  .visuel::after{{content:"";position:absolute;inset:0;
    background:linear-gradient(to top,rgba(21,29,46,.92),transparent 46%)}}
  .rem{{
    position:absolute;left:10px;bottom:10px;z-index:2;
    background:linear-gradient(135deg,#16a34a,#22c55e);color:#fff;
    font-size:13.5px;font-weight:800;padding:3px 9px;border-radius:7px;
    box-shadow:0 3px 10px rgba(0,0,0,.4);letter-spacing:-.3px;
  }}
  .star{{
    position:absolute;right:9px;top:9px;z-index:2;
    background:rgba(10,14,26,.82);backdrop-filter:blur(6px);
    color:var(--or);font-size:13px;width:26px;height:26px;border-radius:50%;
    display:grid;place-items:center;border:1px solid rgba(251,191,36,.32);
  }}

  .corps{{padding:13px 14px 14px;display:flex;flex-direction:column;flex:1}}
  h2{{
    font-size:14.5px;font-weight:650;line-height:1.32;margin-bottom:9px;
    display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
    overflow:hidden;min-height:2.64em;
  }}
  .vedette h2{{font-size:15.5px}}

  .note{{display:flex;align-items:baseline;gap:7px;font-size:12.5px;margin-bottom:11px}}
  .note b{{font-size:13px;font-weight:700}}
  .note.bon b{{color:#4ade80}} .note.moyen b{{color:var(--or)}} .note.bof b{{color:#f87171}}
  .note .av{{color:var(--gris2);font-size:11.5px}}
  .note.vide{{color:var(--gris2);font-size:11.5px}}

  .tarif{{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin-bottom:11px}}
  .prix b{{font-size:21px;font-weight:750;letter-spacing:-.7px}}
  .prix s{{color:var(--gris2);font-size:12.5px;margin-left:5px}}
  .eco{{color:var(--vert);font-size:12px;font-weight:600;white-space:nowrap}}

  .verdict{{
    display:inline-flex;align-items:center;gap:6px;align-self:flex-start;
    font-size:11.5px;font-weight:600;color:var(--c);
    background:color-mix(in srgb,var(--c) 13%,transparent);
    border:1px solid color-mix(in srgb,var(--c) 32%,transparent);
    padding:3px 9px;border-radius:20px;margin-bottom:12px;
  }}
  .pastille{{width:6px;height:6px;border-radius:50%;background:var(--c);flex-shrink:0}}

  .pied{{
    margin-top:auto;padding-top:10px;border-top:1px solid var(--bord);
    display:flex;align-items:center;justify-content:space-between;gap:8px;
    font-size:11.5px;color:var(--gris2);
  }}
  .bas-prix b{{color:var(--bleu);font-weight:650}}
  .jauge{{display:flex;gap:3px;cursor:help;flex-shrink:0}}
  .jauge i{{width:5px;height:5px;border-radius:50%;background:#2c3a56}}
  .jauge i.on{{background:var(--bleu)}}

  .vide-msg{{color:var(--gris2);font-size:14px;padding:26px 0;text-align:center;
             border:1px dashed var(--bord);border-radius:13px}}

  footer{{
    margin-top:56px;padding:26px 0 44px;border-top:1px solid var(--bord);
    color:var(--gris2);font-size:12.5px;line-height:1.85;
  }}
  a{{color:var(--bleu);text-decoration:none}}
  a:hover{{text-decoration:underline}}

  @media(max-width:620px){{
    header{{padding:34px 0 20px}}
    .grid{{grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:11px}}
    .corps{{padding:11px}}
    h2{{font-size:13px}} .prix b{{font-size:18px}}
    .visuel img,.noimg,.vedette .visuel img{{height:88px}}
    .stat{{flex:1;min-width:calc(50% - 6px);padding:11px 14px}}
    .stat b{{font-size:19px}}
  }}
</style>
</head>
<body>
<div class="wrap">

  <header>
    <div class="logo"><span class="dot"></span><span style="font-size:12.5px;color:var(--gris);
      text-transform:uppercase;letter-spacing:1.6px;font-weight:600">Mis à jour chaque jour</span></div>
    <h1>Deal&nbsp;Radar</h1>
    <p class="accroche">
      Steam affiche « −50&nbsp;% », mais jamais si c'est <b>vraiment</b> le meilleur prix.
      On relève les prix tous les jours pour te le dire.
    </p>
    <div class="stats">
      <div class="stat"><b>{len(jeux)}</b><span>jeux suivis</span></div>
      <div class="stat v"><b>−{remise_max}%</b><span>meilleure remise</span></div>
      <div class="stat b"><b>{len(populaires)}</b><span>gros titres</span></div>
      <div class="stat o"><b>{espace_milliers(economie)}€</b><span>d'économies</span></div>
    </div>
  </header>

  <div class="info">
    <span class="ic">💡</span>
    <div>
      Les points bleus sous chaque jeu indiquent <b>le nombre de relevés de prix</b>.
      Plus il y en a, plus le verdict est fiable. Le site est jeune&nbsp;: l'historique
      se construit un jour après l'autre — <b>{nb_verif} jeu{'x' if nb_verif > 1 else ''}</b>
      {'ont' if nb_verif > 1 else 'a'} déjà 3 relevés ou plus.
    </div>
  </div>

  <div class="barre">
    <div class="champ">
      <span class="loupe">⌕</span>
      <input id="q" type="search" placeholder="Rechercher un jeu…" autocomplete="off">
    </div>
    <select id="tri">
      <option value="defaut">Meilleures affaires</option>
      <option value="avis">Les plus connus</option>
      <option value="remise">Plus grosse remise</option>
      <option value="prix">Prix croissant</option>
      <option value="note">Mieux notés</option>
    </select>
    <select id="pmax">
      <option value="999">Tous les prix</option>
      <option value="5">Moins de 5€</option>
      <option value="10">Moins de 10€</option>
      <option value="20">Moins de 20€</option>
    </select>
    <select id="pop">
      <option value="tout">Tous les jeux</option>
      <option value="pop">Gros titres seulement</option>
    </select>
  </div>
  <p id="compteur"></p>

  <div class="section" id="t-pop">
    <h3>★ Gros titres</h3>
    <span class="cpt">plus de {espace_milliers(SEUIL_POPULAIRE)} avis</span>
    <span class="trait"></span>
  </div>
  <div class="grid" id="g-pop">{''.join(carte(j, True) for j in populaires)}</div>
  <p class="vide-msg" id="v-pop" style="display:none">Aucun gros titre ne correspond.</p>

  <div class="section" id="t-autres">
    <h3>Toutes les promos</h3>
    <span class="cpt">{len(autres)} jeux</span>
    <span class="trait"></span>
  </div>
  <div class="grid" id="g-autres">{''.join(carte(j) for j in autres)}</div>
  <p class="vide-msg" id="v-autres" style="display:none">Aucun jeu ne correspond.</p>

  <footer>
    Dernier relevé le {maj_txt} · Données issues du moteur de recherche public Steam,
    prix en euros, boutique France.<br>
    Seuls les jeux disponibles en français sont affichés.
    Projet indépendant, sans lien avec Valve Corporation.
  </footer>
</div>

<script>
const gPop = document.getElementById('g-pop');
const gAutres = document.getElementById('g-autres');
const q = document.getElementById('q');
const tri = document.getElementById('tri');
const pmax = document.getElementById('pmax');
const pop = document.getElementById('pop');
const compteur = document.getElementById('compteur');

const cartesPop = Array.from(gPop.children);
const cartesAutres = Array.from(gAutres.children);
const ordrePop = cartesPop.slice();
const ordreAutres = cartesAutres.slice();

const num = (el, a) => parseFloat(el.dataset[a]) || 0;

function trier(liste, mode) {{
  const l = liste.slice();
  if (mode === 'avis')   l.sort((a,b) => num(b,'avis')   - num(a,'avis'));
  if (mode === 'remise') l.sort((a,b) => num(b,'remise') - num(a,'remise'));
  if (mode === 'prix')   l.sort((a,b) => num(a,'prix')   - num(b,'prix'));
  if (mode === 'note')   l.sort((a,b) => num(b,'note')   - num(a,'note'));
  return l;
}}

function appliquer() {{
  const texte = q.value.trim().toLowerCase();
  const limite = parseFloat(pmax.value);
  const popOnly = pop.value === 'pop';
  let nPop = 0, nAutres = 0;

  cartesPop.forEach(c => {{
    const ok = c.dataset.nom.includes(texte) && num(c,'prix') <= limite;
    c.style.display = ok ? '' : 'none';
    if (ok) nPop++;
  }});
  cartesAutres.forEach(c => {{
    const ok = !popOnly && c.dataset.nom.includes(texte) && num(c,'prix') <= limite;
    c.style.display = ok ? '' : 'none';
    if (ok) nAutres++;
  }});

  trier(ordrePop, tri.value).forEach(c => gPop.appendChild(c));
  trier(ordreAutres, tri.value).forEach(c => gAutres.appendChild(c));

  document.getElementById('v-pop').style.display = nPop ? 'none' : '';
  document.getElementById('t-autres').style.display = popOnly ? 'none' : '';
  gAutres.style.display = popOnly ? 'none' : '';
  document.getElementById('v-autres').style.display = (!popOnly && !nAutres) ? '' : 'none';

  const t = nPop + nAutres;
  compteur.innerHTML = '<b>' + t + '</b> jeu' + (t > 1 ? 'x' : '') + ' affiché'
                     + (t > 1 ? 's' : '') + ' · dont <b>' + nPop + '</b> gros titre'
                     + (nPop > 1 ? 's' : '');
}}

[q, tri, pmax, pop].forEach(el => el.addEventListener('input', appliquer));
appliquer();
</script>
</body>
</html>"""

(SITE / "index.html").write_text(html, encoding="utf-8")
print(f"✓ site/index.html — {len(populaires)} gros titres + {len(autres)} autres jeux")


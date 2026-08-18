#!/usr/bin/env python3
"""Génère le site statique Deal Radar (avec recherche et filtres côté navigateur)."""
import json, pathlib, datetime

# ─── RÉGLAGE ───────────────────────────────────────────────────────────────
SEUIL_POPULAIRE = 5000   # à partir de X avis, le jeu passe dans "Jeux populaires"
# ───────────────────────────────────────────────────────────────────────────

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data" / "deals.json").read_text(encoding="utf-8"))
SITE = ROOT / "site"
SITE.mkdir(exist_ok=True)

jeux = D["jeux"]
maj = datetime.datetime.fromisoformat(D["maj"]).strftime("%d/%m/%Y à %H:%M")

populaires = [j for j in jeux if (j.get("avis") or 0) >= SEUIL_POPULAIRE]
autres = [j for j in jeux if (j.get("avis") or 0) < SEUIL_POPULAIRE]


def carte(j, vedette=False):
    base = f"<s>{j['prix_base']:.2f}€</s> " if j.get("prix_base") else ""
    releves = j["releves"]
    fiab = "◆" * min(releves, 5) + "◇" * max(0, 5 - min(releves, 5))
    note = j.get("note")
    avis = j.get("avis")
    if note is not None:
        c = "#4ade80" if note >= 80 else ("#facc15" if note >= 60 else "#f87171")
        av = (" · " + f"{avis:,}".replace(",", " ") + " avis") if avis else ""
        bloc_note = f"<p class='note' style='color:{c}'>👍 {note}%{av}</p>"
    else:
        bloc_note = "<p class='note'>—</p>"
    visuel = (f"<img src='{j['image']}' alt='' loading='lazy'>" if j.get("image")
              else "<div class='noimg'></div>")
    cls = "jeu vedette" if vedette else "jeu"

    return f"""
  <article class="{cls}" data-nom="{j['nom'].lower()}" data-prix="{j['prix']}"
           data-remise="{j['remise']}" data-note="{note or 0}" data-avis="{avis or 0}">
    {visuel}
    <div class="corps">
      <div class="haut">
        <h2>{j['nom']}</h2>
        <span class="rem">-{j['remise']}%</span>
      </div>
      {bloc_note}
      <div class="bas">
        <div class="prix">{base}<b>{j['prix']:.2f}€</b></div>
        <span class="badge" style="background:{j['couleur']}">{j['verdict']}</span>
      </div>
      <p class="hist">Plus bas vu : <b>{j['plus_bas']:.2f}€</b>
         <span class="fiab" title="{releves} relevé(s)">{fiab}</span></p>
      <a class="lien" href="https://store.steampowered.com/app/{j['id']}/" target="_blank" rel="noopener">Voir sur Steam →</a>
    </div>
  </article>"""


html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Deal Radar — les vraies promos Steam</title>
<meta name="description" content="Suivi de prix Steam : on garde l'historique pour dire si une promo est réellement la meilleure offre.">
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
        background:#0b1120;color:#e2e8f0;padding:28px 16px 70px}}
  .wrap{{max-width:1280px;margin:0 auto}}
  h1{{font-size:32px;letter-spacing:-.6px}}
  .sub{{color:#94a3b8;margin:6px 0 18px}}
  .note-info{{background:#1e293b;border-left:3px solid #38bdf8;padding:11px 14px;
         border-radius:0 8px 8px 0;font-size:13.5px;color:#cbd5e1;margin-bottom:20px}}
  .barre{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px;position:sticky;top:0;
          background:#0b1120;padding:12px 0;z-index:10;border-bottom:1px solid #1e293b}}
  input,select{{background:#1e293b;border:1px solid #334155;color:#e2e8f0;
                padding:9px 12px;border-radius:9px;font-size:14px;font-family:inherit}}
  input{{flex:1;min-width:190px}}
  input:focus,select:focus{{outline:none;border-color:#38bdf8}}
  #compteur{{color:#64748b;font-size:13px;margin-bottom:16px}}
  .titre-section{{display:flex;align-items:baseline;gap:10px;margin:26px 0 14px}}
  .titre-section h3{{font-size:15px;text-transform:uppercase;letter-spacing:1.2px;color:#e2e8f0}}
  .titre-section span{{font-size:12.5px;color:#64748b}}
  .grid{{display:grid;gap:15px;grid-template-columns:repeat(auto-fill,minmax(275px,1fr))}}
  .jeu{{background:#1e293b;border:1px solid #334155;border-radius:13px;overflow:hidden;
        display:flex;flex-direction:column}}
  .jeu.vedette{{border-color:#38bdf8;box-shadow:0 0 0 1px rgba(56,189,248,.18)}}
  .jeu img,.noimg{{width:100%;height:105px;object-fit:cover;display:block;background:#0f172a}}
  .vedette img{{height:135px}}
  .corps{{padding:13px;display:flex;flex-direction:column;flex:1}}
  .haut{{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}}
  h2{{font-size:14.5px;line-height:1.3}}
  .vedette h2{{font-size:16px}}
  .rem{{background:#166534;color:#bbf7d0;border-radius:6px;padding:2px 7px;
        font-size:13px;font-weight:700;flex-shrink:0}}
  .note{{font-size:12px;margin:6px 0 9px;color:#64748b}}
  .bas{{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}}
  .prix b{{font-size:19px;color:#fff}}
  .prix s{{color:#64748b;font-size:13px}}
  .badge{{font-size:10.5px;padding:3px 8px;border-radius:20px;color:#fff;white-space:nowrap}}
  .hist{{font-size:12px;color:#94a3b8;margin:9px 0 11px}}
  .hist b{{color:#38bdf8}}
  .fiab{{color:#475569;letter-spacing:1px;float:right}}
  .lien{{margin-top:auto;color:#38bdf8;font-size:13px;text-decoration:none;font-weight:500}}
  .lien:hover{{text-decoration:underline}}
  .vide{{color:#64748b;font-size:14px;padding:10px 0}}
  footer{{margin-top:38px;color:#64748b;font-size:13px;line-height:1.75}}
  a{{color:#38bdf8}}
</style>
</head>
<body>
<div class="wrap">
  <h1>Deal Radar</h1>
  <p class="sub">{len(jeux)} jeux en promo suivis · maj {maj}</p>

  <div class="note-info">
    <b>Comment lire :</b> Steam affiche « -50 % » mais jamais si c'est le meilleur prix jamais pratiqué.
    Ce site relève les prix chaque jour et construit son propre historique.
    Les losanges ◆ indiquent le nombre de relevés — plus il y en a, plus le verdict est fiable.
    <b>Un site jeune a peu de recul : c'est normal, ça se construit avec le temps.</b>
  </div>

  <div class="barre">
    <input id="q" type="search" placeholder="Rechercher un jeu…">
    <select id="tri">
      <option value="defaut">Trier : meilleures affaires</option>
      <option value="avis">Les plus connus</option>
      <option value="remise">Remise la plus forte</option>
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
      <option value="pop">Jeux populaires seulement</option>
    </select>
  </div>
  <p id="compteur"></p>

  <div class="titre-section" id="t-pop">
    <h3>★ Jeux populaires</h3>
    <span>plus de {SEUIL_POPULAIRE:,} avis</span>
  </div>
  <div class="grid" id="g-pop">{''.join(carte(j, True) for j in populaires)}</div>
  <p class="vide" id="v-pop" style="display:none">Aucun jeu populaire ne correspond.</p>

  <div class="titre-section" id="t-autres">
    <h3>Toutes les autres promos</h3>
    <span>{len(autres)} jeux</span>
  </div>
  <div class="grid" id="g-autres">{''.join(carte(j) for j in autres)}</div>
  <p class="vide" id="v-autres" style="display:none">Aucun jeu ne correspond.</p>

  <footer>
    Données : moteur de recherche public Steam · prix en EUR, boutique France.<br>
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

function num(el, attr) {{ return parseFloat(el.dataset[attr]) || 0; }}

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

  const total = nPop + nAutres;
  compteur.textContent = total + ' jeu' + (total > 1 ? 'x' : '') + ' affiché' + (total > 1 ? 's' : '')
                       + ' · dont ' + nPop + ' populaire' + (nPop > 1 ? 's' : '');
}}

[q, tri, pmax, pop].forEach(el => el.addEventListener('input', appliquer));
appliquer();
</script>
</body>
</html>"""

(SITE / "index.html").write_text(html, encoding="utf-8")
print(f"✓ site/index.html — {len(populaires)} jeux populaires (≥{SEUIL_POPULAIRE} avis) + {len(autres)} autres")


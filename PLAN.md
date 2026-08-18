# Deal Radar — plan honnête

## Ce qui tourne déjà

```
deal-radar/
├── scripts/collect.py    → récupère les promos Steam + construit l'historique de prix
├── scripts/build.py      → génère le site statique
├── data/historique.json  → TON actif réel : l'historique des prix jour après jour
├── data/deals.json       → les deals du jour
└── site/index.html       → le site
```

Lancer : `python3 scripts/collect.py && python3 scripts/build.py`

**38 jeux collectés au premier run, en français, en euros, API Steam publique sans clé.**

---

## L'idée en une phrase

Steam affiche « -50 % », mais ne dit jamais si c'est le meilleur prix jamais pratiqué ou une remise cosmétique sur un prix gonflé. Deal Radar relève les prix tous les jours, construit son propre historique, et tranche.

---

## Le truc que tu dois comprendre avant tout le reste

**Au premier lancement, les 38 jeux sont marqués « plus bas historique ».** C'est mécaniquement vrai et totalement inutile : avec un seul relevé, le minimum observé *est* le prix du jour. Ce n'est pas un bug, c'est la nature du produit.

Ça a une conséquence stratégique majeure :

> **Ton actif, ce n'est pas le code. C'est le fichier `historique.json`.**

Le code, n'importe qui le réécrit en un week-end. Six mois de relevés quotidiens, personne ne peut les rattraper sans attendre six mois. C'est précisément le genre d'actif qui correspond à ce que tu cherchais : **il prend de la valeur pendant que tu ne fais rien**, à condition que la collecte tourne automatiquement.

D'où la priorité absolue de la semaine 1 : automatiser la collecte. Tant que ça dépend de toi qui lances un script, le projet meurt le jour où tu as trois contrôles.

Les losanges ◆ affichés sur le site sont là pour ça : ils montrent honnêtement le nombre de relevés. Un jeu avec ◆◇◇◇◇ dit clairement « je n'ai qu'un relevé, ne me fais pas confiance ». C'est ce qui te distingue des sites qui affirment sans nuance.

---

## La concurrence — à connaître avant de te lancer

Autant être direct : **IsThereAnyDeal** et **SteamDB** font déjà du suivi de prix Steam, et ils le font bien. Tu ne vas pas les battre frontalement.

Trois angles où il reste réellement de la place :

1. **Le français.** IsThereAnyDeal et SteamDB sont anglophones et très techniques. Un site clair en français, orienté « est-ce que j'achète maintenant ou j'attends ? », ça n'existe pas vraiment.
2. **Le verdict tranché.** Les concurrents affichent des graphiques. Toi tu affiches une réponse. C'est un produit différent, pas une copie moins bonne.
3. **La niche.** Plutôt que « tous les jeux Steam », vise un segment : les jeux coop à jouer entre potes, les indés à moins de 10 €, les jeux qui tournent sur PC portable modeste. Une niche étroite bien servie bat un généraliste médiocre.

Si tu ne choisis pas un angle, le projet n'a aucune raison d'exister. Choisis-en un cette semaine.

---

## Les 4 semaines

**Semaine 1 — Automatiser (le plus important)**
- GitHub Actions : un workflow qui lance `collect.py` + `build.py` tous les jours à 12 h, commit le résultat. Gratuit, illimité sur dépôt public.
- Déploiement GitHub Pages ou Cloudflare Pages. Gratuit, HTTPS inclus.
- **À la fin de cette semaine, le site doit se mettre à jour sans toi.** Si tu ne fais qu'une chose, fais celle-là.

**Semaine 2 — Choisir l'angle**
- Décide ta niche (voir plus haut) et filtre la collecte en conséquence
- Ajoute un tri/filtre par genre et par prix max
- Écris une vraie page « comment ça marche » — la transparence sur la méthode, c'est ton argument

**Semaine 3 — Les premiers utilisateurs**
- Montre-le à tes potes. Regarde-les l'utiliser sans rien dire. Note ce qui les bloque.
- Poste sur r/gamingfr, r/FrenchGaming, les serveurs Discord gaming FR
- Attention : poste comme quelqu'un qui a fait un truc, pas comme quelqu'un qui fait de la pub. La différence se sent immédiatement.

**Semaine 4 — Mesurer**
- Cloudflare Analytics ou Plausible (gratuits)
- La seule métrique qui compte : **est-ce que des gens reviennent la semaine suivante ?**
- Si oui → continue. Si non → le produit ne sert à rien en l'état, change l'angle plutôt que d'insister.

Après : tu ne touches plus qu'une heure par mois. Le reste, c'est l'historique qui s'épaissit.

---

## Monétisation — et ses limites réelles

Sois lucide, ce type de site rapporte peu et lentement :

| Levier | Réaliste ? | Ordre de grandeur |
|---|---|---|
| Affiliation clés de jeux (Instant Gaming, Kinguin) | Oui, c'est le standard du secteur | 20-150 €/mois à ~5 000 visiteurs |
| Dons (Ko-fi, Buy Me a Coffee) | Marginal mais réel si le site est utile | 0-30 €/mois |
| Version pro / API | Non, pas sur ce marché | — |
| Publicité display | Non avant 50 000 vues/mois | — |

⚠️ **Ne mets pas d'affiliation avant d'avoir des utilisateurs réguliers.** Un site vide couvert de liens sponsorisés ne convertit pas et détruit la confiance, qui est ton seul actif au début.

**Statut légal :** rien à faire tant que tu ne gagnes rien. Dès le premier euro d'affiliation, il faut un cadre — et à ton âge, ça passe par tes parents (voir le point suivant).

---

## Le point mineur, sans détour

Tu es lycéen, donc :
- **Tant que le site est gratuit et ne rapporte rien : aucune formalité.** Tu peux le lancer aujourd'hui, publiquement, sans rien déclarer. C'est le cas de 100 % des projets à ce stade.
- **Dès que ça génère de l'argent** (même 15 € d'affiliation) : un mineur non émancipé ne peut pas ouvrir de micro-entreprise. Les revenus doivent passer par un compte parental, ou attendre tes 18 ans.
- **Les programmes d'affiliation exigent presque tous 18 ans.** Ne monte pas un business plan là-dessus avant ta majorité.

Concrètement : construis l'audience et l'historique maintenant, monétise à 18 ans. C'est frustrant mais c'est le seul chemin propre — et sur ce projet précis, ça tombe bien, puisque la valeur vient justement de l'accumulation dans le temps.

---

## Pourquoi ce projet plutôt qu'un autre, pour toi

- **Tu es dans la cible.** Tu sais ce qui manque à un lycéen qui veut acheter un jeu, parce que c'est toi. Cet avantage-là ne s'achète pas.
- **Charge réelle après automatisation : ~1 h/mois.** Compatible avec une terminale.
- **Coût : 0 €.** Domaine optionnel à 12 €/an.
- **Compétence acquise : réelle.** API, scraping, données, automatisation CI, déploiement. C'est exactement ce qu'on demande à un dev junior. Même si le site ne rapporte jamais un centime, tu ressors avec un projet montrable en entretien ou en dossier post-bac — et ça, c'est loin d'être rien.

---

## Le vrai risque

Ce n'est pas technique. C'est que tu lances la collecte trois jours puis que tu oublies. Un historique interrompu ne vaut rien.

**Automatise en semaine 1. Ensuite, laisse le temps travailler.**

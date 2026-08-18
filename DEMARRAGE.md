# Deal Radar — guide de démarrage

---

# Partie 1 — L'idée, simplement

## Le problème

Tu es sur Steam. Un jeu affiche **-50 %**. Tu te demandes : c'est une bonne affaire, ou j'attends ?

Steam ne te le dira jamais. Il affiche la remise, mais pas si le jeu a déjà été moins cher le mois dernier. Résultat : soit tu achètes trop cher, soit tu attends une promo qui ne reviendra pas avant un an.

## La solution

Un site qui **note les prix tous les jours**, sans rien oublier.

Au bout de quelques mois, quand Steam affiche -50 %, ton site peut dire :

> « Ce jeu est déjà descendu à 8 € en novembre. Là il est à 12 €. **Attends.** »

ou

> « Jamais vu moins cher que maintenant. **Achète.** »

C'est tout. Une info que Steam a mais ne montre pas.

## Pourquoi c'est un bon projet pour toi

Voici le point important, et il vaut la peine de bien le comprendre :

**Ce qui a de la valeur ici, ce n'est pas le site. C'est le fichier d'historique.**

Le code du site, quelqu'un le refait en un week-end. Mais **six mois de relevés de prix, personne ne peut les copier** — il faut avoir attendu six mois.

Concrètement : chaque jour où le robot tourne, ton projet vaut un peu plus. Même les jours où tu ne fais rien. Même pendant les vacances. Même en période de bac.

C'est exactement ce que tu cherchais : quelque chose qui se construit tout seul.

**La conséquence :** la seule chose vraiment urgente, c'est de faire tourner la collecte automatiquement. Le design, les filtres, la niche — tout ça peut attendre. Un jour de collecte manqué est perdu pour toujours.

## Ce qu'il y a déjà dans le dossier

| Fichier | À quoi ça sert |
|---|---|
| `scripts/collect.py` | Va chercher les promos Steam et note les prix du jour |
| `scripts/build.py` | Fabrique la page web à partir des données |
| `data/historique.json` | **Le trésor.** Tous les prix relevés, jour par jour |
| `data/deals.json` | Les promos du jour, prêtes à afficher |
| `site/index.html` | Le site |
| `lancer.sh` | Raccourci pour tout lancer d'un coup |
| `.github/workflows/update.yml` | Le robot qui fera tout ça sans toi |

## Une précision sur ce que tu vois aujourd'hui

Tous les jeux affichent « Plus bas historique ». C'est **normal et attendu** : il n'y a qu'un seul relevé, donc le prix du jour *est* forcément le minimum connu.

Les petits losanges ◆◇◇◇◇ sur chaque carte indiquent le nombre de relevés. Aujourd'hui : un seul. Dans un mois : cinq, et les verdicts commencent à vraiment vouloir dire quelque chose.

Ne juge pas le produit sur son état du jour 1. Juge-le sur ce qu'il sera au jour 90.

---

# Partie 2 — Le plan concret

## Vue d'ensemble

| Étape | Durée | Objectif |
|---|---|---|
| A | 30 min | Le faire tourner sur ton Mac |
| B | 45 min | Mettre en ligne |
| C | 20 min | Automatiser (**l'étape qui compte**) |
| D | 2 h | Choisir ta niche |
| E | 1 h | Premiers utilisateurs |
| F | ~1 h/mois | Entretien |

Total pour être opérationnel : **environ 3 heures**, étalables sur deux week-ends.

---

## ÉTAPE A — Le faire tourner sur ton Mac (30 min)

### A1. Récupérer le dossier

Copie le dossier `deal-radar` de cet espace de travail vers ton Mac (par exemple dans `Documents`).

### A2. Vérifier Python

Ouvre l'app **Terminal** (Cmd+Espace, tape « Terminal »). Colle :

```bash
python3 --version
```

Si tu vois `Python 3.x.x`, c'est bon. Sinon, macOS te proposera d'installer les outils développeur : accepte.

### A3. Lancer

```bash
cd ~/Documents/deal-radar
./lancer.sh
```

Tu dois voir défiler la liste des jeux. Ça prend environ une minute (le script attend 1,5 s entre chaque jeu pour ne pas surcharger l'API Steam — c'est volontaire, ne le réduis pas).

### A4. Regarder le résultat

```bash
open site/index.html
```

Le site s'ouvre dans ton navigateur.

**✅ Étape A validée quand :** le site s'affiche avec des jeux dedans.

---

## ÉTAPE B — Mettre en ligne gratuitement (45 min)

On utilise GitHub : gratuit, et c'est aussi lui qui fera tourner le robot.

### B1. Créer un compte GitHub

Sur [github.com](https://github.com) → *Sign up*.

> ⚠️ **Tu es mineur** : GitHub demande 13 ans minimum, donc c'est bon. Utilise une adresse mail que tu contrôles. Préviens tes parents que tu publies un projet en ligne — c'est plus sain, et tu auras besoin d'eux plus tard si le site rapporte de l'argent.

### B2. Installer Git

Dans le Terminal :

```bash
git --version
```

S'il n'est pas installé, macOS propose de le faire. Accepte.

### B3. Créer le dépôt

Sur GitHub : bouton **+** en haut à droite → **New repository**.

- **Name :** `deal-radar`
- **Public** (obligatoire pour que l'automatisation soit gratuite)
- Ne coche **rien** d'autre
- **Create repository**

### B4. Envoyer ton code

GitHub affiche des commandes. Utilise celles-ci, dans le Terminal, en remplaçant `TONPSEUDO` :

```bash
cd ~/Documents/deal-radar
git init
git add .
git commit -m "Premier envoi"
git branch -M main
git remote add origin https://github.com/TONPSEUDO/deal-radar.git
git push -u origin main
```

GitHub demandera de t'identifier. Si le mot de passe est refusé, il faut créer un **token** : Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token → coche `repo` et `workflow` → copie le token et utilise-le comme mot de passe.

### B5. Activer le site

Sur ton dépôt GitHub : **Settings** → **Pages** (menu de gauche) → sous *Source*, choisis **GitHub Actions**.

**✅ Étape B validée quand :** ton code est visible sur github.com.

---

## ÉTAPE C — Automatiser ⭐ (20 min)

**C'est l'étape la plus importante du projet.** Sans elle, tu as un script. Avec elle, tu as un actif.

Le fichier `.github/workflows/update.yml` est déjà écrit et prêt. Il a été envoyé avec ton code à l'étape B4.

### C1. Autoriser le robot à écrire

Sur ton dépôt : **Settings** → **Actions** → **General** → tout en bas, section *Workflow permissions* :

- Coche **Read and write permissions**
- **Save**

Sans ça, le robot ne pourra pas sauvegarder l'historique.

### C2. Premier lancement manuel

Onglet **Actions** en haut du dépôt → clique sur **Mise à jour quotidienne** dans la colonne de gauche → bouton **Run workflow** → **Run workflow**.

Attends 2-3 minutes, rafraîchis. Une coche verte ✅ = tout fonctionne.

En cas de croix rouge ❌ : clique dessus, lis la ligne en rouge. Neuf fois sur dix c'est l'étape C1 qui a été oubliée.

### C3. Vérifier

Ton site est en ligne à :

```
https://TONPSEUDO.github.io/deal-radar/
```

(Comptez 2-3 minutes après le premier déploiement.)

**✅ Étape C validée quand :** le site est accessible depuis ton téléphone.

À partir de maintenant, **le robot tourne tous les jours à 13 h, tout seul, gratuitement, même si ton Mac est éteint.**

Tu peux ne plus rien faire pendant trois mois : l'historique se construira quand même. C'est ça, l'actif.

---

## ÉTAPE D — Choisir ta niche (2 h, le week-end suivant)

Il faut être lucide : **IsThereAnyDeal** et **SteamDB** font déjà du suivi de prix Steam, en mieux et depuis des années. Tu ne les bats pas de face.

Ce que tu peux faire : **servir un public précis qu'ils servent mal.**

### Trois pistes

**1. Le français, orienté décision**
Eux sont anglophones, avec des graphiques techniques. Toi tu réponds à une seule question, en français : *j'achète ou j'attends ?*

**2. Une catégorie précise**
- « Jeux coop à jouer entre potes » — avec le nombre de joueurs, le crossplay, si un seul doit acheter
- « Bons jeux à moins de 10 € »
- « Jeux qui tournent sur PC portable pourri » — filtre par config requise

**3. Un usage précis**
« Quoi acheter ce week-end » : trois recommandations, pas trois cents. Le tri, c'est le service.

### Comment décider

Pose la question à cinq potes qui jouent : **« quand tu vois une promo Steam, tu te demandes quoi exactement ? »**

Leur réponse te donne ta niche. Ne devine pas, demande.

Pour changer les jeux collectés, c'est dans `scripts/collect.py`, fonction `collecter_promos()`.

**✅ Étape D validée quand :** tu peux décrire ton site en une phrase du type « c'est le site qui dit à [QUI] si [QUOI] ».

---

## ÉTAPE E — Tes premiers utilisateurs (1 h)

### E1. Le test qui compte

Montre le site à trois potes. **Ne dis rien, regarde-les.** Note où ils hésitent, ce qu'ils ne comprennent pas, ce qu'ils cherchent et ne trouvent pas.

C'est plus utile que cent heures de développement.

### E2. Où en parler

- Serveurs Discord gaming francophones
- r/gamingfr, r/jeuxvideo
- Le forum de ton lycée, tes groupes de classe

**Comment poster :** « j'ai fait un truc qui compare les prix Steam dans le temps, dites-moi si c'est utile ». Pas : « DÉCOUVREZ MON SITE ». La différence se sent immédiatement, et le second se fait supprimer.

### E3. Mesurer

Ajoute [Cloudflare Web Analytics](https://www.cloudflare.com/web-analytics/) (gratuit, sans cookies, une ligne à coller dans `build.py`).

**La seule métrique qui compte :** est-ce que des gens **reviennent** la semaine suivante ?

- Oui → tu tiens quelque chose, continue
- Non → le produit ne sert pas encore, change l'angle (étape D) plutôt que d'ajouter des fonctionnalités

---

## ÉTAPE F — Entretien (~1 h/mois)

Une fois automatisé, il n'y a presque plus rien à faire :

- **Une fois par mois :** vérifier que l'onglet Actions est toujours vert
- **Si ça casse :** Steam a changé son API, ce qui arrive une à deux fois par an. Une heure de correction.
- **Quand tu as une idée :** un filtre, une page, une amélioration. Sans obligation.

Le reste du temps, l'historique s'épaissit tout seul.

---

# Partie 3 — Argent et cadre légal

## Combien ça peut rapporter

Sois réaliste, ce type de site ne rend riche personne :

| Source | Réaliste ? | Ordre de grandeur |
|---|---|---|
| Affiliation clés de jeux | Oui, c'est le standard | 20-150 €/mois à ~5 000 visiteurs |
| Dons (Ko-fi) | Marginal mais réel | 0-30 €/mois |
| Publicité | Pas avant 50 000 vues/mois | — |

**Ne mets aucun lien d'affiliation avant d'avoir des visiteurs réguliers.** Un site vide couvert de pub ne convertit pas et grille la confiance — qui est ton seul capital au début.

## Le point mineur, clairement

- **Tant que le site est gratuit et ne rapporte rien : aucune démarche.** Tu peux le lancer aujourd'hui. C'est le cas de tous les projets à ce stade.
- **Dès le premier euro** (même 15 € d'affiliation) : un mineur non émancipé ne peut pas ouvrir de micro-entreprise. Il faut passer par tes parents, ou attendre 18 ans.
- **La plupart des programmes d'affiliation exigent 18 ans** de toute façon.

Donc le plan est simple : **construis l'audience et l'historique maintenant, monétise à 18 ans.** Sur ce projet précis, ça tombe parfaitement, puisque toute la valeur vient de l'accumulation dans le temps. Le jour de tes 18 ans, tu auras deux ans d'historique que personne ne peut rattraper.

## Ce que tu gagnes même si ça ne rapporte jamais

API, traitement de données, automatisation CI/CD, déploiement, Git. C'est très exactement ce qu'on demande à un développeur junior.

Un projet public, en ligne, qui tourne depuis deux ans sans interruption, ça pèse lourd dans un dossier post-bac ou un premier entretien. Beaucoup plus qu'un stage de troisième.

---

# Le seul vrai risque

Ce n'est pas technique. C'est que tu lances la collecte trois jours, puis que tu oublies. **Un historique interrompu ne vaut rien.**

D'où l'ordre de priorité :

1. **Étapes A, B, C ce week-end** (3 h) → le robot tourne, tu es tranquille
2. Le reste quand tu veux, sans pression

Si tu ne fais que les étapes A à C et rien d'autre pendant six mois, tu auras quand même **six mois de données que personne d'autre n'a**. C'est déjà gagné.

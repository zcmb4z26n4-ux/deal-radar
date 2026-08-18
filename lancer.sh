#!/bin/bash
# Double-clique ce fichier (ou lance ./lancer.sh) pour tout mettre à jour en local.
cd "$(dirname "$0")"
echo "→ Collecte des prix Steam..."
python3 scripts/collect.py || exit 1
echo ""
echo "→ Construction du site..."
python3 scripts/build.py || exit 1
echo ""
echo "✓ Terminé. Ouvre site/index.html dans ton navigateur."

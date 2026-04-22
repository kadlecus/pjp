#!/bin/bash

# Vytvoření virtuálního prostředí, pokud neexistuje
if [ ! -d ".venv" ]; then
    echo "Vytvářím virtuální prostředí..."
    python3 -m venv .venv
fi

# Aktivace a instalace závislostí
source .venv/bin/activate
echo "Instaluji knihovny z requirements.txt..."
pip install -r requirements.txt

echo "------------------------------------------------"
echo "Vše je připraveno!"
echo "Pro aktivaci prostředí napiš: source .venv/bin/activate"
echo "------------------------------------------------"

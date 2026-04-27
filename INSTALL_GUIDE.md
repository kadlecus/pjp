# Příručka pro instalaci a spuštění (Windows & Linux)

## 1. Instalace Javy (nutné pro ANTLR)

### Windows (PowerShell / CMD)
```powershell
winget install Microsoft.OpenJDK.17
# PO INSTALACI RESTARTOVAT TERMINÁL!
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install default-jdk
```

---

## 2. Nastavení Python prostředí (venv)

### Windows
```powershell
# Vytvoření prostředí
python -m venv .venv

# Aktivace (PowerShell)
.\.venv\Scripts\Activate.ps1

# Instalace knihoven
pip install -r requirements.txt
```

### Linux
```bash
# Vytvoření prostředí
python3 -m venv .venv

# Aktivace
source .venv/bin/activate

# Instalace knihoven
pip install -r requirements.txt
```

---

## 3. Generování Parseru (ANTLR)
Pokud změníš gramatiku `.g4`, musíš spustit:
```bash
java -jar antlr-4.13.2-complete.jar -Dlanguage=Python3 -visitor -o . PLC_Lab7_expr.g4
```

---

## 4. Spuštění programu
```bash
# Windows
python main.py pr.txt

# Linux / Git Bash
python3 main.py pr.txt
```

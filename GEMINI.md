# PLC Projekt — Dokumentace změn a rozšíření

Tento soubor slouží jako příručka pro implementaci nových funkcí do kompilátoru a interpreteru.

## 1. Práce se soubory (`fopen`, `fclose`)
Implementováno jako vestavěné funkce (výrazy/příkazy).

### Gramatika (`PLC_Lab7_expr.g4`)
```antlr
stat : ... | 'fclose' '(' expr ')' ';' # FcloseStat ;
expr : ... | 'fopen' '(' filename=expr ',' mode=expr ')' # FopenExpr ;
```

### Interpreter (`interpreter.py`)
- V `__init__` přidat `self.open_files = {}` a `self.file_counter = 0`.
- **fopen:** Pop `mode`, pop `filename`, zavolat Python `open()`, uložit do `self.open_files`, push `handle`.
- **fclose:** Pop `handle`, zavolat `.close()`, smazat ze slovníku.

---

## 2. Řídicí struktura `switch`
Implementováno pomocí skoků a dočasné proměnné.

### Gramatika
```antlr
stat : 'switch' '(' expr ')' '{' case_item+ default_item? '}' # SwitchStat ;
case_item : 'case' expr ':' stat* ;
default_item : 'default' ':' stat* ;
```

### Code Generator
1. Vyhodnotit `expr`, `save $switch_tmp`.
2. Pro každý `case`:
   - `load $switch_tmp`, vyhodnotit `case_expr`, `eq T`.
   - `fjmp next_case_label`.
   - Kód těla, pak `jmp end_label`.
   - `label next_case_label`.
3. `label end_label`.

---

## 3. Cyklus `for`
Implementováno jako rozšíření `while` cyklu.

### Gramatika
```antlr
stat : 'for' '(' init=expr ';' cond=expr ';' step=expr ')' stat # ForStat ;
```

### Code Generator
1. `init=expr`, pak `pop` (zahodit výsledek přiřazení).
2. `label start_label`.
3. `cond=expr`, `fjmp end_label`.
4. `stat` (tělo).
5. `step=expr`, pak `pop`.
6. `jmp start_label`.
7. `label end_label`.

---

## 4. `break` a `continue`
Vyžaduje zásobník návěstí (label stack) v Code Generátoru.

### Implementace
- `self.break_stack = []`
- `self.continue_stack = []`
- V `visitWhile` / `visitFor`: Před tělem `push` labelu konce/začátku, po těle `pop`.
- **break:** Vygeneruje `jmp self.break_stack[-1]`.
- **continue:** Vygeneruje `jmp self.continue_stack[-1]`.

---

## Obecný postup pro nové funkce
1. **Gramatika (.g4):** Definovat syntaxi a metodu (`# Jmeno`).
2. **Regenerace:** `java -jar antlr-4.13.2-complete.jar ...`
3. **Type Checker:** Kontrola typů v `visitJmeno`.
4. **Code Generator:** Překlad na instrukce v `visitJmeno`.
5. **Interpreter:** (Volitelné) Přidání nových instrukcí do `_execute`.

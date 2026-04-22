# PLC Projekt — Kompilátor + Interpreter

## Co jsme udělali
4-fázový kompilátor pro vlastní imperativní jazyk (školní projekt PLC).

## Spuštění
```bash
source .venv/bin/activate
python main.py pr.txt        # spustí celý pipeline
python interpreter.py out.txt  # spustí jen interpreter ze souboru
```

## Soubory
| Soubor | Popis |
|---|---|
| `PLC_Lab7_expr.g4` | Gramatika jazyka — **jediný zdroj pravdy pro lexer/parser** |
| `PLC_Lab7_exprLexer.py` | Auto-generovaný ANTLR — **nesahat** |
| `PLC_Lab7_exprParser.py` | Auto-generovaný ANTLR — **nesahat** |
| `PLC_Lab7_exprVisitor.py` | Auto-generovaný ANTLR — **nesahat** |
| `PLC_Lab7_exprListener.py` | Auto-generovaný ANTLR — **nesahat** |
| `main.py` | Pipeline: parser → type check → codegen → interpreter |
| `type_checker.py` | Visitor — kontrola typů, sbírá všechny chyby |
| `code_generator.py` | Visitor — generuje stack-based instrukce |
| `interpreter.py` | Vykonává stack-based instrukce |

## Regenerace lexeru/parseru po změně gramatiky
```bash
java -jar antlr-4.13.2-complete.jar -Dlanguage=Python3 -visitor -o . PLC_Lab7_expr.g4
```

## Jazyk
- Typy: `int`, `float`, `bool`, `string`
- Příkazy: deklarace, `if/else`, `while`, `read`, `write`, bloky `{}`
- Operátory: `+ - * / % . < > == != && || ! = (unární -)`
- Auto-cast `int → float`
- Komentáře: `// ...`

## Instrukční sada (stack-based)
`push T x`, `pop`, `load id`, `save id`, `add/sub/mul/div T`, `mod`, `uminus T`,
`concat`, `and`, `or`, `gt/lt/eq T`, `not`, `itof`, `label n`, `jmp n`, `fjmp n`,
`print n`, `read T`

## Přidání nové funkce (např. for)
1. Uprav `PLC_Lab7_expr.g4` — přidej keyword + pravidlo
2. Regeneruj ANTLR
3. Přidej `visitForStat` do `type_checker.py`
4. Přidej `visitForStat` do `code_generator.py`
5. Interpreter nepotřebuje změny (používá existující instrukce)

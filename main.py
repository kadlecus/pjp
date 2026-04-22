import sys
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from PLC_Lab7_exprLexer import PLC_Lab7_exprLexer
from PLC_Lab7_exprParser import PLC_Lab7_exprParser
from type_checker import TypeChecker
from code_generator import CodeGenerator
from interpreter import Interpreter

class SyntaxErrorCollector(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"Syntax error at line {line}:{column} - {msg}")

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            input_text = f.read()
    else:
        input_text = sys.stdin.read()

    if not input_text.strip():
        return

    input_stream = InputStream(input_text)

    # ── Lexer + Parser ───────────────────────────────────────────────────────
    lexer = PLC_Lab7_exprLexer(input_stream)
    lexer.removeErrorListeners()
    token_stream = CommonTokenStream(lexer)

    parser = PLC_Lab7_exprParser(token_stream)
    parser.removeErrorListeners()
    error_listener = SyntaxErrorCollector()
    parser.addErrorListener(error_listener)

    tree = parser.prog()

    if error_listener.errors:
        for e in error_listener.errors:
            print(e, file=sys.stderr)
        sys.exit(1)

    # ── Type Checker ─────────────────────────────────────────────────────────
    checker = TypeChecker()
    checker.visit(tree)

    if checker.has_errors():
        for e in checker.errors:
            print(e, file=sys.stderr)
        sys.exit(1)

    # ── Code Generator ───────────────────────────────────────────────────────
    gen = CodeGenerator()
    gen.visit(tree)

    # ── Interpreter ──────────────────────────────────────────────────────────
    interp = Interpreter()
    interp.load(gen.get_code())
    interp.run()

if __name__ == '__main__':
    main()

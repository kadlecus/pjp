from antlr4 import *
from PLC_Lab7_exprParser import PLC_Lab7_exprParser

class TypeChecker(ParseTreeVisitor):

    def __init__(self):
        self.symbols = {}   # name -> type ('int','float','bool','string')
        self.errors = []

    def error(self, ctx, msg):
        line = ctx.start.line
        self.errors.append(f"Type error at line {line}: {msg}")

    def has_errors(self):
        return len(self.errors) > 0

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _type_str(self, ctx):
        """Returns the type keyword string from a type rule context."""
        parser = PLC_Lab7_exprParser
        tok = ctx.start.type
        if tok == parser.INT_TYPE:    return 'int'
        if tok == parser.FLOAT_TYPE:  return 'float'
        if tok == parser.BOOL_TYPE:   return 'bool'
        if tok == parser.STRING_TYPE: return 'string'
        if tok == parser.FILE_TYPE:   return 'file'

    def _compatible(self, t1, t2):
        """Returns the result type if t1 op t2 is valid (with int->float cast), else None."""
        if t1 == t2:
            return t1
        if {t1, t2} == {'int', 'float'}:
            return 'float'
        return None

    # ── Program ──────────────────────────────────────────────────────────────

    def visitProg(self, ctx):
        for stat in ctx.stat():
            self.visit(stat)

    # ── Statements ───────────────────────────────────────────────────────────

    def visitEmptyStat(self, ctx):
        pass

    def visitDeclStat(self, ctx):
        typ = self._type_str(ctx.type_())
        for id_token in ctx.ID():
            name = id_token.getText()
            if name in self.symbols:
                self.error(ctx, f"variable '{name}' already declared")
            else:
                self.symbols[name] = typ

    def visitExprStat(self, ctx):
        self.visit(ctx.expr())

    def visitReadStat(self, ctx):
        for id_token in ctx.ID():
            name = id_token.getText()
            if name not in self.symbols:
                self.error(ctx, f"variable '{name}' not declared")

    def visitWriteStat(self, ctx):
        for expr in ctx.expr():
            self.visit(expr)

    

    def visitBlockStat(self, ctx):
        for stat in ctx.stat():
            self.visit(stat)

    def visitIfStat(self, ctx):
        cond_type = self.visit(ctx.expr())
        if cond_type != 'bool':
            self.error(ctx, f"'if' condition must be bool, got '{cond_type}'")
        for stat in ctx.stat():
            self.visit(stat)

    def visitWhileStat(self, ctx):
        cond_type = self.visit(ctx.expr())
        if cond_type != 'bool':
            self.error(ctx, f"'while' condition must be bool, got '{cond_type}'")
        self.visit(ctx.stat())
   
    def visitFopenStat(self, ctx):
        file_id = ctx.ID().getText()
        if file_id not in self.symbols:
            self.error(ctx, f"variable '{file_id}' not declared")
            return
        file = self.symbols[file_id]

        if file != 'file':
            self.error(ctx, f"'fopen' target must be file variable, got '{file}'")

        filename = self.visit(ctx.filename)
        if filename != 'string':
            self.error(ctx, f"'fopen' filename must be string, got '{filename}'")
    
  


    def visitFwriteStat(self, ctx):
        handle = self.visit(ctx.handle)
        if handle != 'file':
            self.error(ctx, f"'fwrite' handle must be file, got '{handle}'")
        
        for expr in ctx.expr():
            self.visit(expr)

    # ── Expressions (return type string) ─────────────────────────────────────

    def visitWriteFile(self, ctx):
        handle = self.visit(ctx.expr(0))
        if handle != 'file':
            self.error(ctx, f"'write' target time to write must be file, got '{handle}'")
        self.visit(ctx.expr(1))
        return 'file'

    def visitIntLit(self, ctx):
        return 'int'

    def visitFloatLit(self, ctx):
        return 'float'

    def visitBoolTrue(self, ctx):
        return 'bool'

    def visitBoolFalse(self, ctx):
        return 'bool'

    def visitStringLit(self, ctx):
        return 'string'

    def visitVar(self, ctx):
        name = ctx.ID().getText()
        if name not in self.symbols:
            self.error(ctx, f"variable '{name}' not declared")
            return None
        return self.symbols[name]

    def visitParens(self, ctx):
        return self.visit(ctx.expr())

    def visitUnaryMinus(self, ctx):
        t = self.visit(ctx.expr())
        if t not in ('int', 'float'):
            self.error(ctx, f"unary '-' requires int or float, got '{t}'")
            return None
        return t

    def visitNot(self, ctx):
        t = self.visit(ctx.expr())
        if t != 'bool':
            self.error(ctx, f"'!' requires bool, got '{t}'")
            return None
        return 'bool'

    def visitMulDivMod(self, ctx):
        t1 = self.visit(ctx.expr(0))
        t2 = self.visit(ctx.expr(1))
        op = ctx.op.text
        if op == '%':
            if t1 != 'int' or t2 != 'int':
                self.error(ctx, f"'%' requires int × int, got '{t1}' × '{t2}'")
                return None
            return 'int'
        result = self._compatible(t1, t2)
        if result not in ('int', 'float'):
            self.error(ctx, f"'{op}' requires int or float operands, got '{t1}' × '{t2}'")
            return None
        return result

    def visitAddSubConcat(self, ctx):
        t1 = self.visit(ctx.expr(0))
        t2 = self.visit(ctx.expr(1))
        op = ctx.op.text
        if op == '.':
            if t1 != 'string' or t2 != 'string':
                self.error(ctx, f"'.' requires string × string, got '{t1}' × '{t2}'")
                return None
            return 'string'
        result = self._compatible(t1, t2)
        if result not in ('int', 'float'):
            self.error(ctx, f"'{op}' requires int or float operands, got '{t1}' × '{t2}'")
            return None
        return result

    def visitRelOp(self, ctx):
        t1 = self.visit(ctx.expr(0))
        t2 = self.visit(ctx.expr(1))
        op = ctx.op.text
        result = self._compatible(t1, t2)
        if result not in ('int', 'float'):
            self.error(ctx, f"'{op}' requires int or float operands, got '{t1}' × '{t2}'")
            return None
        return 'bool'

    def visitEqOp(self, ctx):
        t1 = self.visit(ctx.expr(0))
        t2 = self.visit(ctx.expr(1))
        op = ctx.op.text
        result = self._compatible(t1, t2)
        if result not in ('int', 'float', 'string'):
            self.error(ctx, f"'{op}' requires matching types (int/float/string), got '{t1}' × '{t2}'")
            return None
        return 'bool'

    def visitAndOp(self, ctx):
        t1 = self.visit(ctx.expr(0))
        t2 = self.visit(ctx.expr(1))
        if t1 != 'bool' or t2 != 'bool':
            self.error(ctx, f"'&&' requires bool × bool, got '{t1}' × '{t2}'")
            return None
        return 'bool'

    def visitOrOp(self, ctx):
        t1 = self.visit(ctx.expr(0))
        t2 = self.visit(ctx.expr(1))
        if t1 != 'bool' or t2 != 'bool':
            self.error(ctx, f"'||' requires bool × bool, got '{t1}' × '{t2}'")
            return None
        return 'bool'

    def visitAssign(self, ctx):
        name = ctx.ID().getText()
        if name not in self.symbols:
            self.error(ctx, f"variable '{name}' not declared")
            return None
        var_type = self.symbols[name]
        val_type = self.visit(ctx.expr())
        if val_type == var_type:
            return var_type
        # int -> float auto-cast is allowed only if variable is float
        if var_type == 'float' and val_type == 'int':
            return 'float'
        self.error(ctx, f"cannot assign '{val_type}' to variable '{name}' of type '{var_type}'")
        return var_type

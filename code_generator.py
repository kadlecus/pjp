from antlr4 import *
from PLC_Lab7_exprParser import PLC_Lab7_exprParser

class CodeGenerator(ParseTreeVisitor):

    def __init__(self):
        self.code = []
        self._label_count = 0
        self.symbols = {}  # name -> type

    def new_label(self):
        self._label_count += 1
        return self._label_count

    def emit(self, instr):
        self.code.append(instr)

    def get_code(self):
        return '\n'.join(self.code)

    # ── Type helpers ─────────────────────────────────────────────────────────

    def _type_str(self, ctx):
        p = PLC_Lab7_exprParser
        tok = ctx.start.type
        if tok == p.INT_TYPE:    return 'int'
        if tok == p.FLOAT_TYPE:  return 'float'
        if tok == p.BOOL_TYPE:   return 'bool'
        if tok == p.STRING_TYPE: return 'string'
        if tok == p.FILE_TYPE:   return 'file'

    def _type_letter(self, t):
        return {'int': 'I', 'float': 'F', 'bool': 'B', 'string': 'S', 'file': 'H'}[t]

    def _default_value(self, t):
        return {'int': '0', 'float': '0.0', 'bool': 'false', 'string': '""', 'file': '-1'}[t]

    def _type_of(self, ctx):
        """Derive the type of an already type-checked expression."""
        p = PLC_Lab7_exprParser
        if isinstance(ctx, p.IntLitContext):     return 'int'
        if isinstance(ctx, p.FloatLitContext):   return 'float'
        if isinstance(ctx, p.BoolTrueContext):   return 'bool'
        if isinstance(ctx, p.BoolFalseContext):  return 'bool'
        if isinstance(ctx, p.StringLitContext):  return 'string'
        if isinstance(ctx, p.VarContext):        return self.symbols[ctx.ID().getText()]
        if isinstance(ctx, p.ParensContext):     return self._type_of(ctx.expr())
        if isinstance(ctx, p.AssignContext):     return self.symbols[ctx.ID().getText()]
        if isinstance(ctx, p.NotContext):        return 'bool'
        if isinstance(ctx, p.AndOpContext):      return 'bool'
        if isinstance(ctx, p.OrOpContext):       return 'bool'
        if isinstance(ctx, p.RelOpContext):      return 'bool'
        if isinstance(ctx, p.EqOpContext):       return 'bool'
        if isinstance(ctx, p.UnaryMinusContext): return self._type_of(ctx.expr())
        if isinstance(ctx, p.MulDivModContext):
            if ctx.op.text == '%': return 'int'
            return self._numeric_result(ctx.expr(0), ctx.expr(1))
        if isinstance(ctx, p.AddSubConcatContext):
            if ctx.op.text == '.': return 'string'
            return self._numeric_result(ctx.expr(0), ctx.expr(1))
        return None

    def _numeric_result(self, e1, e2):
        """int+int→int, anything with float→float."""
        t1 = self._type_of(e1)
        t2 = self._type_of(e2)
        return 'float' if (t1 == 'float' or t2 == 'float') else 'int'

    def _visit_and_cast(self, expr_ctx, target_type):
        """Visit expression and emit itof if int→float cast is needed."""
        self.visit(expr_ctx)
        if self._type_of(expr_ctx) == 'int' and target_type == 'float':
            self.emit('itof')

    def _visit_binary_numeric(self, ctx):
        """Visit both operands of a numeric binary op, casting if needed. Returns result type."""
        t1 = self._type_of(ctx.expr(0))
        t2 = self._type_of(ctx.expr(1))
        result = 'float' if (t1 == 'float' or t2 == 'float') else 'int'
        self._visit_and_cast(ctx.expr(0), result)
        self._visit_and_cast(ctx.expr(1), result)
        return result

    # ── Program ──────────────────────────────────────────────────────────────

    def visitProg(self, ctx):
        for stat in ctx.stat():
            self.visit(stat)

    # ── Statements ───────────────────────────────────────────────────────────

    def visitEmptyStat(self, ctx):
        pass

    def visitDeclStat(self, ctx):
        t = self._type_str(ctx.type_())
        tl = self._type_letter(t)
        default = self._default_value(t)
        for id_tok in ctx.ID():
            name = id_tok.getText()
            self.symbols[name] = t
            self.emit(f'push {tl} {default}')
            self.emit(f'save {name}')

    def visitExprStat(self, ctx):
        self.visit(ctx.expr())
        self.emit('pop')

    def visitReadStat(self, ctx):
        for id_tok in ctx.ID():
            name = id_tok.getText()
            tl = self._type_letter(self.symbols[name])
            self.emit(f'read {tl}')
            self.emit(f'save {name}')

    def visitWriteStat(self, ctx):
        exprs = ctx.expr()
        for expr in exprs:
            self.visit(expr)
        self.emit(f'print {len(exprs)}')

    def visitBlockStat(self, ctx):
        for stat in ctx.stat():
            self.visit(stat)

    def visitIfStat(self, ctx):
        self.visit(ctx.expr())
        stmts = ctx.stat()
        if len(stmts) == 1:
            l1 = self.new_label()
            self.emit(f'fjmp {l1}')
            self.visit(stmts[0])
            self.emit(f'label {l1}')
        else:
            l1 = self.new_label()
            l2 = self.new_label()
            self.emit(f'fjmp {l1}')
            self.visit(stmts[0])
            self.emit(f'jmp {l2}')
            self.emit(f'label {l1}')
            self.visit(stmts[1])
            self.emit(f'label {l2}')

    def visitWhileStat(self, ctx):
        l1 = self.new_label()
        l2 = self.new_label()
        self.emit(f'label {l1}')
        self.visit(ctx.expr())
        self.emit(f'fjmp {l2}')
        self.visit(ctx.stat())
        self.emit(f'jmp {l1}')
        self.emit(f'label {l2}')

    def visitFopenStat(self, ctx):
    
        self.visit(ctx.filename)
        self.emit(f'open')
        self.emit(f'save {ctx.ID().getText()}')

    def visitFwriteStat(self, ctx):
        for expr in ctx.expr():
            self.visit(ctx.handle)
            self.visit(expr)
            self.emit(f'fwrite') 

    

    # ── Expressions ──────────────────────────────────────────────────────────

    def visitWriteFile(self, ctx):
        self.visit(ctx.expr(0))
        self.visit(ctx.expr(1))
        self.emit(f'fwrite2')

    def visitIntLit(self, ctx):
        self.emit(f'push I {ctx.INT_LIT().getText()}')

    def visitFloatLit(self, ctx):
        self.emit(f'push F {ctx.FLOAT_LIT().getText()}')

    def visitBoolTrue(self, ctx):
        self.emit('push B true')

    def visitBoolFalse(self, ctx):
        self.emit('push B false')

    def visitStringLit(self, ctx):
        self.emit(f'push S {ctx.STRING_LIT().getText()}')

    def visitVar(self, ctx):
        self.emit(f'load {ctx.ID().getText()}')

    def visitParens(self, ctx):
        self.visit(ctx.expr())

    def visitUnaryMinus(self, ctx):
        self.visit(ctx.expr())
        tl = self._type_letter(self._type_of(ctx.expr()))
        self.emit(f'uminus {tl}')

    def visitNot(self, ctx):
        self.visit(ctx.expr())
        self.emit('not')

    def visitMulDivMod(self, ctx):
        op = ctx.op.text
        if op == '%':
            self.visit(ctx.expr(0))
            self.visit(ctx.expr(1))
            self.emit('mod')
            return
        result = self._visit_binary_numeric(ctx)
        self.emit(f"{'mul' if op == '*' else 'div'} {self._type_letter(result)}")

    def visitAddSubConcat(self, ctx):
        op = ctx.op.text
        if op == '.':
            self.visit(ctx.expr(0))
            self.visit(ctx.expr(1))
            self.emit('concat')
            return
        result = self._visit_binary_numeric(ctx)
        self.emit(f"{'add' if op == '+' else 'sub'} {self._type_letter(result)}")

    def visitRelOp(self, ctx):
        result = self._visit_binary_numeric(ctx)
        tl = self._type_letter(result)
        self.emit(f"{'lt' if ctx.op.text == '<' else 'gt'} {tl}")

    def visitEqOp(self, ctx):
        t1 = self._type_of(ctx.expr(0))
        t2 = self._type_of(ctx.expr(1))
        result = 'float' if (t1 == 'float' or t2 == 'float') else t1
        self._visit_and_cast(ctx.expr(0), result)
        self._visit_and_cast(ctx.expr(1), result)
        self.emit(f'eq {self._type_letter(result)}')
        if ctx.op.text == '!=':
            self.emit('not')

    def visitAndOp(self, ctx):
        self.visit(ctx.expr(0))
        self.visit(ctx.expr(1))
        self.emit('and')

    def visitOrOp(self, ctx):
        self.visit(ctx.expr(0))
        self.visit(ctx.expr(1))
        self.emit('or')

    def visitAssign(self, ctx):
        name = ctx.ID().getText()
        var_type = self.symbols[name]
        self._visit_and_cast(ctx.expr(), var_type)
        self.emit(f'save {name}')
        self.emit(f'load {name}')

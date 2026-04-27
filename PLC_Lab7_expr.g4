grammar PLC_Lab7_expr;

// ─── Parser Rules ────────────────────────────────────────────────────────────

prog: stat* EOF;

stat
    : ';'                                       # EmptyStat
    | type ID (',' ID)* ';'                     # DeclStat
    | READ ID (',' ID)* ';'                     # ReadStat
    | WRITE expr (',' expr)* ';'                # WriteStat
    | FWRITE '(' handle=expr ',' data=expr ')' ';' #FwriteStat
    | '{' stat* '}'                             # BlockStat
    | IF '(' expr ')' stat (ELSE stat)?         # IfStat
    | SWITCH '(' condition=expr ')' '{' case_item* default_item? '}' #SwitchStat
    | FOR '(' init=expr';' condition=expr';' step=expr')' stat #ForStat
    | WHILE '(' expr ')' stat                   # WhileStat
    | CONTINUE ';'                              # ContinueStat
    | BREAK ';'                                 # BreakStat
    | FCLOSE '(' handle=expr ')' ';'            # FcloseStat
    | expr ';'                                  # ExprStat
    ;

case_item
    : CASE expr ':' stat*
    ;

default_item
    : DEFAULT ':' stat*
    ;

type
    : INT_TYPE
    | FLOAT_TYPE
    | BOOL_TYPE
    | STRING_TYPE
    | FILE_TYPE
    ;

// Operators listed highest to lowest precedence (ANTLR4 convention)
expr
    : '-' expr                                  # UnaryMinus
    | '!' expr                                  # Not
    | expr op=('*'|'/'|'%') expr               # MulDivMod
    | expr op=('+'|'-'|'.') expr               # AddSubConcat
    | expr op=('<'|'>') expr                    # RelOp
    | expr op=('=='|'!=') expr                  # EqOp
    | expr '&&' expr                            # AndOp
    | expr '||' expr                            # OrOp
    | <assoc=right> ID '=' expr                 # Assign
    | '(' expr ')'                              # Parens
    | FLOAT_LIT                                 # FloatLit
    | FOPEN '(' filename=expr ',' fmode=expr ')' # FopenExpr
    | FREAD '(' handle=expr ')'                 #FreadExpr
    | INT_LIT                                   # IntLit
    | TRUE                                      # BoolTrue
    | FALSE                                     # BoolFalse
    | STRING_LIT                                # StringLit
    | ID                                        # Var
    ;

// ─── Lexer Rules ─────────────────────────────────────────────────────────────

// Keywords (must be defined before ID so they take priority)
IF          : 'if';
ELSE        : 'else';
WHILE       : 'while';
FOR         : 'for';
READ        : 'read';
WRITE       : 'write';
FWRITE      : 'fwrite';
FREAD       : 'fread';
TRUE        : 'true';
BREAK       : 'break';
CONTINUE    : 'continue';
SWITCH      : 'switch';
DEFAULT     : 'default';
CASE        : 'case';
FOPEN       : 'fopen';
FCLOSE      : 'fclose';
FALSE       : 'false';
INT_TYPE    : 'int';
FLOAT_TYPE  : 'float';
BOOL_TYPE   : 'bool';
FILE_TYPE   : 'file';
STRING_TYPE : 'string';

// Literals — FLOAT_LIT before INT_LIT so "3.14" doesn't tokenize as "3" + ".14"
FLOAT_LIT   : [0-9]+ '.' [0-9]* | '.' [0-9]+;
INT_LIT     : [0-9]+;
STRING_LIT  : '"' (~["\r\n])* '"';

// Identifier: starts with letter, followed by letters/digits
ID          : [a-zA-Z][a-zA-Z0-9]*;

// Ignored
LINE_COMMENT: '//' ~[\r\n]* -> skip;
WS          : [ \t\r\n]+    -> skip;

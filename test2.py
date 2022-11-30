'''
RECURSIVE DECENT ALGORITHM ( RDA )
Used to code out top down parsers, and LL Gramars which have two restrictions:
- Must be pairwise disjoint
- No left hand recursion

int y = 0, x = 7 < y ? 4 : 80 * 7; 

<stmt> --> <if_stmt> | <while_stmt> | <declare_stmt> | <assign_stmt> | <block> 
<block> --> `{` { <stmt>`;` } `}`
<if_stmt> -->  `check``(`<bool_expr>`)` <stmt> [ `psych` <stmt> ]  //put two seperate lines in parser 
<while_loop> -->  `span``(`<bool_expr>`)` <stmt> 
<declare_stmt> --> `data_type` {`id` `;` | <assign_stmt>}
<assign_stmt>  --> `id` `=` <expr> `;`
<expr> --> <term> { (`*`|`\`|`%`)  <term> }
<term> --> <factor> { (`+`|`-`) <factor> }
<factor> --> `id` | `int_lit` | `float_lit` | `(` <expr> `)`



<bool_expr> --> <band> { `OR` <band> }
<band> --> <beq> { `AND` <beq> }
<beq> --> <brel> { (`!=`|`==`) <brel> }
<brel> --> <expr> { (`<=`|`>=` | `<` | `>`) <expr> }
<bexpr> --> <bterm> { (`+`|`-`) <bterm> }
<bterm> --> <bnot> { (`*`|`\`|`%`) <bnot> }
<bnot> -> [!]<bfactor>
<factor> --> `id` | `int_lit` | `float_lit` | `bool_lit` | `(` <bexpr> `)`

'''
from _typeshed import Self
import re

#######################################
# TOKENS
#######################################

KEYWORD = 1
IDENTIFIER = 2
SHODAI = 'SHODAI' # 1 BYTE INT LITERAL
NIDAIME = 'NIDAIME' # 2 BYTE INT LITERAL
YONDAIME = 'YONDAIME' # 4 BYTE INT LITERAL
HATIDAIME = 'HATIDAIME' # 8 BYTE INT LITERAL
INT = 3
FLOAT = 4
PLUS = 5
MINUS = 6
MUL = 7
DIV = 8
MOD = 9
EQ = 10
LT = 11 # Less Than Token Constant
GT = 12 # Greater Than Token Constant
LTE = 13 # Less Than or Equal Token Constant
GTE = 14 # Greater Than or Equal Token Constant
EE = 15
NE = 16
LPRN = 17 # Left Parenthesis
RPRN = 18 # Right Parenthesis
EOF = 19
CHECK = 20
SPAN = 21
SEMI = 22
DT = 23
LBR = 24
RBR = 25

DIGITS = re.compile("^[0-9]+$")
LETTERS = re.compile("^[a-zA-Z]+$")
VARNAME = re.compile("^[a-z][A-Z]_{6-8}")

KEYWORDS = [
            'SHODAI',
            'NIDAIME',
            'YONDAIME',
            'HATIDAIME',
            'CHECK',
            'SPAN',
            'PSYCH'
        ]

class Error:
    def __init__(self, pos, errorName, details):
        self.pos = pos
        self.errorName = errorName
        self.details = details

    def __str__(self):
        result = f'{self.errorName}: {self.details}\n File {self.pos.fn}'
        return result

class IllegalCharError(Error):
	def __init__(self, pos, details):
		super().__init__(pos, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos, details):
        super().__init__(pos, 'Invalid Syntax', details)

# Token class to store token object with type and value
class Token:
    def __init__(self, type_, value = None):
        self.type = type_
        self.value = value

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    # Token to String method
    def __str__(self):
        if self.value: return f'Next token is: {self.type}, Next Lexeme is {self.value}'

class Lexer:
    def __init__(self, fn ,str):
        self.fn = fn
        self.str = str
        self.position = -1
        self.currentChar = None
        self.advance()


    def advance(self):
        self.position += 1
        self.currentChar = self.text[self.position] if self.position < len(self.text) else None
    
    def lex(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t\n':
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.createNumber())
            elif self.currentChar in LETTERS:
                tokens.append(self.createIdentifier())
            elif self.currentChar == '+':
                tokens.append(Token(PLUS, '+'))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(MINUS, '-'))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(MUL, '-'))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(DIV, '/'))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(LPRN)
                self.advance()
            elif self.currentChar == ')':
                tokens.append(RPRN)
                self.advance()
            else:
                pos = self.position
                char = self.currentChar
                self.advance()
                return [], IllegalCharError(pos, "'" + char + "'")
                pass

        tokens.append(Token(EOF, 'EOF'))
        return tokens, None

    def createNumber(self):
            numStr = ''
            dotCount = 0
            startPos = self.position
            while self.currentChar != None and self.currentChar in DIGITS + '.':
                if self.currentChar == '.':
                    if dotCount == 1: break
                    dotCount += 1
                numStr += self.currentChar
                self.advance()
            if dotCount == 0:
                return Token(INT, int(numStr), startPos, self.pos)
            else:
                return Token(FLOAT, float(numStr), startPos, self.pos)
    
    def createIdentifier(self):
        pass


class Parser:
    def __init__(self, fn ,tokens:list(Token)) -> None:
        self.fn = fn
        self.tokens = tokens
        self.currentToken = 0
        self.currentToken = tokens[self.currentToken]
    
    def getNextToken(self):
        if self.currentToken < len(self.tokens):
            self.currentToken += 1

        self.currentToken = self.tokens[self.currentToken]

    def parse(self):
        res = self.stmt()
        if not res.error and self.currentToken.type != EOF:
            return res.failure(InvalidSyntaxError(
                self.currentToken.startPos, self.currentToken.endPos,
                "Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'AND' or 'OR'"
            ))
        return res

    def stmt(self):
        if self.currentToken.type == CHECK:
            self.if_stmt()
        elif self.currentToken.type == SPAN:
            self.while_stmt()
        elif self.currentToken.type == DT:
            self.declare_stmt()
        elif self.currentToken.type == IDENTIFIER:
            self.assign_stmt()
        elif self.currentToken.type == LBR:
            self.block()
        else:
            self.error()

    # Parses strings in the language generated by the rule
    # <block> --> `{` { <stmt>`;` } `}`
    def block(self):
        if self.currentToken == '{':
            while self.currentToken.type == CHECK or self.currentToken.type == SPAN or self.currentToken.type == IDENTIFIER or self.currentToken.type == SEMI:
                self.stmt() 
                if self.currentToken == ';':
                    self.getNextToken()
                else:
                    self.error()

            if self.currentToken == '}':
                self.getNextToken()
            else:
                self.error()
        else:
            self.error()

    def if_stmt():
        pass

    # Parses strings in the language generated by the rule:
    # <while_loop> --> `span``(`<bool_expr>`)` <stmt> 
    def while_stmt(self):
        if self.currentToken == 'span':
            self.getNextToken()
            if self.currentToken == '(':
                self.getNextToken()
                self.expr()
                if self.currentToken == ')':
                    self.getNextToken()
                    self.stmt()
                else:
                    self.error()
            else:
                self.error()
        else:
            self.error()
    
    # Parses strings in the language generated by the rule:
    # <assign_stmt> --> `id` `=` <expr>
    def assign_stmt(self):
        if self.currentToken.type == IDENTIFIER:
            self.getNextToken()
            if self.currentToken.type == EQ:
                self.getNextToken()
                self.expr()
            else: 
                self.error()
        else:
            self.error()
    
    # Parses strings in the language generated by the rule:
    # <declare_stmt> --> `data_type` `id` `;`
    def declare_stmt(self):
        if self.currentToken.type == DT:
            self.getNextToken()
            if self.currentToken.type == IDENTIFIER:
                self.getNextToken()
                if self.currentToken.type == SEMI:
                    self.getNextToken()
                elif self.currentToken.type == EQ:
                    self.assign_stmt()
            else:
                self.error()
        else:
            self.error()



    # Parses strings in the language generated by the rule:
    # <expr> --> <term> { (`*`|`\`|`%`)  <term> }
    def expr(self):
        self.term()
        while self.currentToken.type == PLUS  or self.currentToken.type == MINUS:
            self.getNextToken()
            self.term()
    
    # Parses strings in the language generated by the rule:
    # <term> --> <factor> { (`+`|`-`) <factor> }
    def term(self):
        self.factor()
        while self.currentToken.type == MUL or self.currentToken.type == DIV or self.currentToken.type == MOD:
            self.getNextToken()
            self.factor()
    
    # Parses strings in the language generated by the rule:
    # <factor> --> `id` | `int_lit` | `float_lit` | `(` <expr> `)`
    def factor(self):
        if self.currentToken.currentToken.type == IDENTIFIER or self.currentToken.currentToken.type == INT or self.currentToken.currentToken.type == FLOAT :
            self.getNextToken()
        elif self.currentToken.type == LPRN:
            self.getNextToken()
            self.expr()
            if self.currentToken.type == RPRN:
                self.getNextToken()
            else:
                self.error()
        else:
            self.error

    def error(self):
        pass

def run(fn):
    text = fn.read().split()

	# Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.lex()
    if error: return None, error
	
	# Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error
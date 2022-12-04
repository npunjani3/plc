import re

# TOKENS

KEYWORD = 1
IDENTIFIER = 2
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
AND = 26
OR = 27
PSYCH = 28
NOT = 29
BOOL = 30

DIGITS = re.compile("^[0-9]+$")
FLOAT = re.compile("^[0-9]+.[0-9]+$")
LETTERS = re.compile("^[a-zA-Z]+$")
VARNAME = re.compile("^[a-zA-Z_]{6,8}$")
BLOCKS = re.compile("{(});")

KEYWORDS = [
            'SHODAI',
            'NIDAIME',
            'YONDAIME',
            'HATIDAIME',
            'CHECK',
            'SPAN',
            'PSYCH',
            '&&',
            '||',
            '!!'
        ]

DATATYPES = [KEYWORDS[0], KEYWORDS[1], KEYWORDS[2], KEYWORDS[3]]

class Error:
    def __init__(self, pos, errorName, details, fn, ln):
        self.pos = pos
        self.errorName = errorName
        self.details = details
        self.fn = fn
        self.ln = ln

    def __repr__(self):
        result = f'{self.errorName}: {self.details}\nFile: {self.fn} Line: {self.ln} at {self.pos}'
        return result

# Token class to store token object with type and value
class Token:
    def __init__(self, type_, pos, value = None):
        self.type = type_
        self.pos = pos
        self.value = value

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    # Token to String method
    def __repr__(self):
        if self.value: return f'Next token is: {self.type}, Next Lexeme is {self.value}'

class Lexer:
    def __init__(self, fn ,text):
        self.fn = fn
        self.text = text
        self.ln = 1
        self.position = -1
        self.currentChar = None
        self.advance()

    # Method to move index position of text array
    def advance(self):
        self.position += 1
        self.currentChar = self.text[self.position] if self.position < len(self.text) else None

    # Method to increment ln variable which keeps track of line of text
    def lnAdvance(self):
        self.ln += 1

    # Method to convert strings into tokens or errors
    # Returns an array of tokens or a single error
    def lex(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t\n':
                if self.currentChar in '\n':
                    self.lnAdvance()
                self.advance()
            elif re.search(DIGITS, self.currentChar):
                tokens.append(self.createNumber())
            elif re.search(LETTERS, self.currentChar):
                tokens.append(self.createIdentifier())
            elif self.currentChar == '+':
                tokens.append(Token(PLUS, self.position, '+'))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(MINUS, self.position, '-'))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(MUL, self.position, '*'))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(DIV, self.position, '/'))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(Token(LPRN, self.position, '('))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(RPRN, self.position, ')'))
                self.advance()
            elif self.currentChar == '=':
                tokens.append(self.createEquals())
                self.advance()
            elif self.currentChar == ';':
                tokens.append(Token(SEMI, self.position, ';'))
                self.advance()
            elif self.currentChar == '{':
                tokens.append(Token(LBR, self.position, '{'))
                self.advance()
            elif self.currentChar == '}':
                tokens.append(Token(RBR, self.position, '}'))
                self.advance()
            elif self.currentChar == '!':
                tokens.append(self.createEquals())
                self.advance()
            elif self.currentChar == '<':
                tokens.append(self.createLts())
                self.advance()
            elif self.currentChar == '>':
                tokens.append(self.createGts())
                self.advance()
            elif self.currentChar == '&':
                tokens.append(self.createBoolOps())
                self.advance()
            elif self.currentChar == '|':
                tokens.append(self.createBoolOps())
                self.advance()
            elif not re.search(DIGITS, self.currentChar) or not re.search(LETTERS, self.currentChar):
                pos= self.position
                eName = "IllegalCharError" 
                detail = "'"+self.currentChar+"'"
                self.advance()
                return tokens, Error(pos, details=detail, errorName=eName,fn = self.fn, ln = self.ln)
            else:
                pos = self.position
                char = self.currentChar.split(":")
                eName = char[0]
                detail = "'"+char[1]+"'"
                self.advance()
                return tokens, Error(pos, details=detail, errorName=eName,fn = self.fn, ln = self.ln)

        tokens.append(Token(EOF, self.position, 'EOF'))
        return tokens, None

    # Method to create Int or Float token returns error if not a match
    def createNumber(self):
            numStr = ''
            dotCount = 0
            
            while self.currentChar != None and self.currentChar != ' ' and self.currentChar != ';' and self.currentChar != ')':
                if self.currentChar == '.':
                    if dotCount == 1: break
                    dotCount += 1
                numStr += self.currentChar
                self.advance()
                if not re.search(DIGITS, numStr):
                    break

            if not re.search(DIGITS, numStr):
                self.currentChar = "IllegalCharError:"+ numStr[-1]
                return
            if dotCount == 0:
                if re.search(DIGITS, numStr):
                    return Token(INT, self.position, int(numStr))
            else:
                return Token(FLOAT, self.position, float(numStr))
    
    # Method to create Identifier, Keyword, Data Type token returns error if not a match
    def createIdentifier(self):
        idStr = ''

        while self.currentChar != None and self.currentChar != ' ' and self.currentChar != ')':
            idStr += self.currentChar
            self.advance()
            if not re.search(LETTERS, self.currentChar):
                break
            

        if not re.search(LETTERS, idStr):
            self.currentChar = "IllegalCharError:"+ idStr[-1]
            return

        if idStr in KEYWORDS:
            if idStr in DATATYPES:
                tokenType = DT
            elif idStr == 'CHECK':
                tokenType = CHECK
            elif idStr == 'SPAN':
                tokenType = SPAN
            else: tokenType = KEYWORD
        else:
            tokenType = IDENTIFIER

        if tokenType == IDENTIFIER:
            if not re.search(VARNAME, idStr):
                print(idStr)
                self.currentChar = "Error:Illegal Variable Name"
                return
            else: return Token(tokenType, self.position, idStr)
        else:
            return Token(tokenType, self.position, idStr)

    # Creates tokens for =, == , !=, and !! returns error if not a match
    def createEquals(self):
        idStr = ''

        while self.currentChar != None and self.currentChar != ' ':
            idStr += self.currentChar
            self.advance()
        
        if idStr == '=':
            return Token(EQ, self.position, '=')
        elif idStr == '==':
            return Token(EE, self.position, '==')
        elif idStr == '!=':
            return Token(EE, self.position, '!=')
        elif idStr == '!!':
            return Token(NOT, self.position, '!!')
        else:
            self.currentChar = "IllegalCharError:"+ idStr[-1]
            return

    # Creates tokens for <, and <= returns error if not a match
    def createLts(self):
        idStr = ''

        while self.currentChar != None and self.currentChar != ' ':
            idStr += self.currentChar
            self.advance()

        if idStr == '<':
            return Token(LT, self.position, '<')
        elif idStr == '==':
            return Token(LTE, self.position, '<=')
        else:
            self.currentChar = "IllegalCharError:"+ idStr[-1]
            return

    # Creates tokens for >, and >= returns error if not a match
    def createGts(self):
        idStr = ''

        while self.currentChar != None and self.currentChar != ' ':
            idStr += self.currentChar
            self.advance()

        if idStr == '>':
            return Token(GT, self.position, '>')
        elif idStr == '==':
            return Token(GTE, self.position, '>=')
        else:
            self.currentChar = "IllegalCharError:"+ idStr[-1]
            return

    # Creates tokens for AND, and OR returns error if not a match
    def createBoolOps(self):
        idStr = ''

        while self.currentChar != None and self.currentChar != ' ':
            idStr += self.currentChar
            self.advance()

        if idStr == '&&':
            return Token(AND, self.position, '&&')
        elif idStr == '||':
            return Token(OR, self.position, '||')
        else:
            self.currentChar = "IllegalCharError:"+ idStr[-1]
            return



class Parser:
    def __init__(self, fn ,tokens) -> None:
        self.fn = fn
        self.tokens = tokens
        self.idx = -1
        self.currentToken = tokens[self.idx]
        self.getNextToken()
    
    # Method to advance to next token
    def getNextToken(self):
        if self.idx < len(self.tokens):
            self.idx += 1

        self.currentToken = self.tokens[self.idx]
        print(self.currentToken)

    # Method to parse through list of tokens
    def parse(self):
        res = self.start()
        if not res and self.currentToken.type != EOF:
            return Error(
                self.currentToken.pos, "InvalidSyntaxError: ",
                "Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', '&&' or '||'", self.fn, 1
            )
        return res

    # Parses strings in the language gnerated by the rule
    # <start --> <stmt> 
    def start(self):
        while self.currentToken.type != EOF:
            self.stmt()
            if self.idx < len(self.tokens):
                self.getNextToken()

    # Parses strings in the language gnerated by the rule
    # <stmt> --> <if_stmt> | <while_stmt> | <declare_stmt> | <assign_stmt> | <block> 
    def stmt(self):
        print("Enter <stmt>")
        # self.getNextToken()
        # while self.idx < len(self.tokens):
        if self.currentToken.type == KEYWORD:
            self.if_stmt()
        elif self.currentToken.type == SPAN:
            self.while_stmt()
        elif self.currentToken.type == DT:
            self.declare_stmt()
        elif self.currentToken.type == IDENTIFIER:
            self.assign_stmt()
        elif self.currentToken.type == LBR:
            self.block()
        elif self.currentToken.type == EOF:
            return
        else:
            self.error("Inside stmt")
        print("Exit <stmt>")

    # Parses strings in the language generated by the rule
    # <block> --> `{` { <stmt>`;` } `}`
    def block(self):
        print("Enter <block_stmt>")
        if self.currentToken.type != LBR:
            self.error("Expected {")
        else:
            self.getNextToken()
            self.stmt() 
            # if self.currentToken.type != SEMI:
            #     self.error("Expected ; from inside block")
            # else:
            self.getNextToken()
            if self.currentToken.type != RBR:
                self.error("Expected }")

        print("Exit <block_stmt>")

    # Parses the string in the language generated by the rule
    # <if_stmt> -->  `check``(`<bool_expr>`)` <block> [ `psych` <block> ] 
    def if_stmt(self):
        print("Enter <if_stmt>")
        if not self.currentToken.matches(KEYWORD, 'CHECK'):
            self.error("Expected CHECK")
        else:
            self.getNextToken()
            if self.currentToken.type != LPRN:
                self.error("Expected LPRN")
            else:
                self.getNextToken()
                self.bool_expr()
                if self.currentToken.type != RPRN:
                    self.error("Expected RPRN")
                else:
                    self.getNextToken()
                    self.block()
                    if self.currentToken.type!= RBR:
                        self.error("Expected RBR")
                    else:
                        self.getNextToken()
                        if self.currentToken.matches(KEYWORD, 'PSYCH'):
                            self.getNextToken()
                            self.block()
                        else:
                            self.error("Expected PSYCH")
    print("Exit <if_stmt>")

    # Parses the string in the language generated by the rule
    # <bool_expr> --> <band> { `OR` <band> } 
    def bool_expr(self):
        print("Enter <bool_expr>")
        self.band()
        while self.currentToken.type == OR:
            self.getNextToken()
            self.band()
        print("Exit <bool_expr>")

    # Parses the string in the language generated by the rule
    # <beq> { `AND` <beq> }
    def band(self):
        print("Enter <band>")
        self.beq()
        while self.currentToken.type == AND:
            self.getNextToken()
            self.beq()

        print("Exit <band>")

    # Parses the string in the language generated by the rule
    # <brel> { (`!=`|`==`) <brel> }
    def beq(self):
        print("Enter <beq>")
        self.brel()
        while self.currentToken.type == EE or self.currentToken.type == NE:
            self.getNextToken()
            self.brel()
        print("Exit <beq>")

    # Parses the string in the language generated by the rule
    # <expr> { (`<=`|`>=` | `<` | `>`) <expr> }
    def brel(self):
        print("Enter <brel>")
        self.bexpr()
        while self.currentToken.type == LT or self.currentToken.type == GT or self.currentToken.type == LTE or self.currentToken.type == GTE:
            self.getNextToken()
            self.bexpr()
        print("Exit <brel>")


    # Parses the string in the language generated by the rule
    # <bterm> { (`+`|`-`) <bterm> }
    def bexpr(self):
        print("Enter <bexpr>")
        self.bterm()
        while self.currentToken.type == PLUS or self.currentToken.type == MINUS:
            self.getNextToken()
            self.bterm()
        print("Exit <bexpr>")

    # Parses the string in the language generated by the rule
    # <bnot> { (`*`|`\`|`%`) <bnot> }
    def bterm(self):
        print("Enter <bterm>")
        self.bnot()
        while self.currentToken.type == MUL or self.currentToken.type == DIV or self.currentToken.type == MOD:
            self.getNextToken()
            self.bnot()
        print("Exit <bterm>")

    # Parses the string in the language generated by the rule
    # [!!]<bfactor>
    def bnot(self):
        print("Enter <bnot>")
        self.bfactor()
        while self.currentToken.type == NOT:
            self.getNextToken()
            self.bfactor()
        print("Exit <bnot>")
        pass

    # Parses the string in the language generated by the rule
    # <bfactor> --> `id` | `int_lit` | `float_lit` | `bool_lit` | `(` <bexpr> `)`
    def bfactor(self):
        print("Enter <bfactor>")
        if self.currentToken.type == IDENTIFIER or self.currentToken.type == INT or self.currentToken.type == FLOAT or self.currentToken.type == BOOL:
            self.getNextToken()
        elif self.currentToken.type == LPRN:
            self.getNextToken()
            self.bexpr()
            if self.currentToken.type == RPRN:
                self.getNextToken()
            else:
                self.error()
        else:
            self.error

        print("Exit <bfactor>")

    # Parses strings in the language generated by the rule:
    # <while_stmt> --> `span``(`<bool_expr>`)` <block> 
    def while_stmt(self):
        print("Enter <while_stmt>")
        if self.currentToken.type == SPAN:
            self.getNextToken()
            if self.currentToken.type == LPRN:
                self.getNextToken()
                self.bexpr()
                if self.currentToken.type == RPRN:
                    self.getNextToken()
                    self.block()
                else:
                    self.error("Expected )")
            else:
                self.error("Expected (")
        else:
            self.error("Expected SPAN")

        print("Exit <while_stmt>")
    
    # Parses strings in the language generated by the rule:
    # <assign_stmt> --> `id` `=` <expr> 
    def assign_stmt(self):
        print("Enter <assign_stmt>")
        if self.currentToken.type == IDENTIFIER:
            self.getNextToken()
            if self.currentToken.type == SEMI:
                self.getNextToken()
            else:
                if self.currentToken.type != EQ:
                    self.error("Expected =")
                else:
                    self.getNextToken()
                    self.expr()
                    if self.currentToken.type != SEMI:
                        self.error("Expected ;")
        else:
            self.error("Error from assign_stmt")
        
        print("Exit <assign_stmt>")
    
    # Parses strings in the language generated by the rule:
    # <declare_stmt> --> `data_type` <assign_stmt> 
    def declare_stmt(self):
        if self.currentToken.type == DT:
            print("Enter <declare_stmt>")
            self.getNextToken()
            self.assign_stmt()
        else:
            self.error("Expected DT token")

        print("Exit <declare_stmt>")



    # Parses strings in the language generated by the rule:
    # <expr> --> <term> { (`*`|`\`|`%`)  <term> }
    def expr(self):
        print("Enter <expr>")
        self.term()
        while self.currentToken.type == MUL or self.currentToken.type == DIV or self.currentToken.type == MOD:
            self.getNextToken()
            self.term()
        print("Exit <expr>")
    
    # Parses strings in the language generated by the rule:
    # <term> --> <factor> { (`+`|`-`) <factor> }
    def term(self):
        print("Enter <term>")
        self.factor()
        while self.currentToken.type == PLUS  or self.currentToken.type == MINUS:
            self.getNextToken()
            self.factor()
        print("Exit <term>")
    
    # Parses strings in the language generated by the rule:
    # <factor> --> `id` | `int_lit` | `float_lit` | `(` <expr> `)`
    def factor(self):
        print("Enter <factor>")
        if self.currentToken.type == IDENTIFIER or self.currentToken.type == INT or self.currentToken.type == FLOAT:
            self.getNextToken()
        elif self.currentToken.type == LPRN:
            self.getNextToken()
            self.expr()
            if self.currentToken.type == RPRN:
                self.getNextToken()
            else:
                self.error("Expected }")
        else:
            self.error("From factor")

        print("Exit <factor>")

    def error(self, details):
        print("Error stoopid: "+details)
        return

# Method to execute lexer and parser on text file.
def run(fn):
    print("\nRunning file: "+fn+'\n')
    fileObj = open(fn, "r")
    text = fileObj.read()

	# Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.lex()
    if error: print(error)
    else: 
        print(*tokens, sep="\n")
        print("Lexeme count: "+ str(len(tokens))+'\n')
        
        # Generate Parse Trace
        Parser(fn, tokens).parse()

run('sample1.txt')
# run('sample2.txt')
# run('sample3.txt')
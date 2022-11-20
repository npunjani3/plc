#######################################
# IMPORTS
#######################################

import string

#######################################
# CONSTANTS
#######################################

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

#######################################
# ERRORS
#######################################

class Error:
	def __init__(self, startPos, endPos, errorName, details):
		self.startPos = startPos
		self.endPos = endPos
		self.errorName = errorName
		self.details = details
	
	def asString(self):
		result  = f'{self.errorName}: {self.details}\n'
		result += f'File {self.startPos.fn}, line {self.startPos.ln + 1}'
		# result += '\n\n' + string_with_arrows(self.startPos.ftxt, self.startPos, self.endPos)
		return result

class IllegalCharError(Error):
	def __init__(self, startPos, endPos, details):
		super().__init__(startPos, endPos, 'Illegal Character', details)

class ExpectedCharError(Error):
	def __init__(self, startPos, endPos, details):
		super().__init__(startPos, endPos, 'Expected Character', details)

class InvalidSyntaxError(Error):
	def __init__(self, startPos, endPos, details=''):
		super().__init__(startPos, endPos, 'Invalid Syntax', details)

class RTError(Error):
	def __init__(self, startPos, endPos, details, context):
		super().__init__(startPos, endPos, 'Runtime Error', details)
		self.context = context

	def asString(self):
		result  = self.generateTraceback()
		result += f'{self.errorName}: {self.details}'
		# result += '\n\n' + string_with_arrows(self.startPos.ftxt, self.startPos, self.endPos)
		return result

	def generateTraceback(self):
		result = ''
		pos = self.startPos
		ctx = self.context

		while ctx:
			result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.displayName}\n' + result
			pos = ctx.parentEntryPos
			ctx = ctx.parent

		return 'Traceback (most recent call last):\n' + result

#######################################
# POSITION
#######################################

class Position:
	def __init__(self, idx, ln, col, fn, ftxt):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.fn = fn
		self.ftxt = ftxt

	def advance(self, currentChar=None):
		self.idx += 1
		self.col += 1

		if currentChar == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copy(self):
		return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
#######################################

TK_KEYWORD = 1
TK_IDENTIFIER = 2
TK_TINY = 'TINY' # 1 BYTE INT LITERAL
TK_SMALLINT = 'SMALLINT' # 2 BYTE INT LITERAL
TK_BIGINT = 'BIGINT' # 4 BYTE INT LITERAL
TK_LONGINT = 'LONGINT' # 8 BYTE INT LITERAL
TK_INT = 3
TK_FLOAT = 4
TK_PLUS = 5
TK_MINUS = 6
TK_MUL = 7
TK_DIV = 8
TK_MOD = 9
TK_POW = 20
TK_EQ = 10
TK_LT = 11 # Less Than Token Constant
TK_GT = 12 # Greater Than Token Constant
TK_LTE = 13 # Less Than or Equal Token Constant
TK_GTE = 14 # Greater Than or Equal Token Constant
TK_EE = 15
TK_NE = 16
TK_LPRN = 17 # Left Parenthesis
TK_RPRN = 18 # Right Parenthesis
TK_EOF = 19


KEYWORDS = [
	'VAR',
	'AND', #
	'OR', #
	'NOT' #
]

class Token:
	def __init__(self, type_, value=None, startPos=None, endPos=None):
		self.type = type_
		self.value = value

		if startPos:
			self.startPos = startPos.copy()
			self.endPos = startPos.copy()
			self.endPos.advance()

		if endPos:
			self.endPos = endPos.copy()

	def matches(self, type_, value):
		return self.type == type_ and self.value == value
	
	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'

#######################################
# LEXER
#######################################

class Lexer:
	def __init__(self, fn, text):
		self.fn = fn
		self.text = text
		self.pos = Position(-1, 0, -1, fn, text)
		self.currentChar = None
		self.advance()
	
	def advance(self):
		self.pos.advance(self.currentChar)
		self.currentChar = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

	def makeTokens(self):
		tokens = []

		while self.currentChar != None:
			if self.currentChar in ' \t':
				self.advance()
			elif self.currentChar in DIGITS:
				tokens.append(self.makeNumber())
			elif self.currentChar in LETTERS:
				tokens.append(self.makeIdentifier())
			elif self.currentChar == '+':
				tokens.append(Token(TK_PLUS, startPos=self.pos))
				self.advance()
			elif self.currentChar == '-':
				tokens.append(Token(TK_MINUS, startPos=self.pos))
				self.advance()
			elif self.currentChar == '*':
				tokens.append(Token(TK_MUL, startPos=self.pos))
				self.advance()
			elif self.currentChar == '/':
				tokens.append(Token(TK_DIV, startPos=self.pos))
				self.advance()
			elif self.currentChar == '^':
				tokens.append(Token(TK_POW, startPos=self.pos))
				self.advance()
			elif self.currentChar == '(':
				tokens.append(Token(TK_LPRN, startPos=self.pos))
				self.advance()
			elif self.currentChar == ')':
				tokens.append(Token(TK_RPRN, startPos=self.pos))
				self.advance()
			elif self.currentChar == '!':
				token, error = self.makeNotEquals()
				if error: return [], error
				tokens.append(token)
			elif self.currentChar == '=':
				tokens.append(self.makeEquals())
			elif self.currentChar == '<':
				tokens.append(self.makeLessThan())
			elif self.currentChar == '>':
				tokens.append(self.makeGreaterThan())
			else:
				startPos = self.pos.copy()
				char = self.currentChar
				self.advance()
				return [], IllegalCharError(startPos, self.pos, "'" + char + "'")

		tokens.append(Token(TK_EOF, startPos=self.pos))
		return tokens, None

	def makeNumber(self):
		numStr = ''
		dotCount = 0
		startPos = self.pos.copy()

		while self.currentChar != None and self.currentChar in DIGITS + '.':
			if self.currentChar == '.':
				if dotCount == 1: break
				dotCount += 1
			numStr += self.currentChar
			self.advance()

		if dotCount == 0:
			return Token(TK_INT, int(numStr), startPos, self.pos)
		else:
			return Token(TK_FLOAT, float(numStr), startPos, self.pos)

	def makeIdentifier(self):
		idStr = ''
		startPos = self.pos.copy()

		while self.currentChar != None and self.currentChar in LETTERS_DIGITS + '_':
			idStr += self.currentChar
			self.advance()

		tokenType = TK_KEYWORD if idStr in KEYWORDS else TK_IDENTIFIER
		return Token(tokenType, idStr, startPos, self.pos)

	def makeNotEquals(self):
		startPos = self.pos.copy()
		self.advance()

		if self.currentChar == '=':
			self.advance()
			return Token(TK_NE, startPos=startPos, endPos=self.pos), None

		self.advance()
		return None, ExpectedCharError(startPos, self.pos, "'=' (after '!')")
	
	def makeEquals(self):
		tokenType = TK_EQ
		startPos = self.pos.copy()
		self.advance()

		if self.currentChar == '=':
			self.advance()
			tokenType = TK_EE

		return Token(tokenType, startPos=startPos, endPos=self.pos)

	def makeLessThan(self):
		tokenType = TK_LT
		startPos = self.pos.copy()
		self.advance()

		if self.currentChar == '=':
			self.advance()
			tokenType = TK_LTE

		return Token(tokenType, startPos=startPos, endPos=self.pos)

	def makeGreaterThan(self):
		tokenType = TK_GT
		startPos = self.pos.copy()
		self.advance()

		if self.currentChar == '=':
			self.advance()
			tokenType = TK_GTE

		return Token(tokenType, startPos=startPos, endPos=self.pos)

#######################################
# NODES
#######################################

class NumberNode:
	def __init__(self, token):
		self.token = token

		self.startPos = self.token.startPos
		self.endPos = self.token.endPos

	def __repr__(self):
		return f'{self.token}'

class VarAccessNode:
	def __init__(self, varNameToken):
		self.varNameToken = varNameToken

		self.startPos = self.varNameToken.startPos
		self.endPos = self.varNameToken.endPos

class VarAssignNode:
	def __init__(self, varNameToken, nodeValue):
		self.varNameToken = varNameToken
		self.nodeValue = nodeValue

		self.startPos = self.varNameToken.startPos
		self.endPos = self.nodeValue.endPos

class BinOpNode:
	def __init__(self, leftNode, opTkn, rightNode):
		self.leftNode = leftNode
		self.opTkn = opTkn
		self.rightNode = rightNode

		self.startPos = self.leftNode.startPos
		self.endPos = self.rightNode.endPos

	def __repr__(self):
		return f'({self.leftNode}, {self.opTkn}, {self.rightNode})'

class UnaryOpNode:
	def __init__(self, opTkn, node):
		self.opTkn = opTkn
		self.node = node

		self.startPos = self.opTkn.startPos
		self.endPos = node.endPos

	def __repr__(self):
		return f'({self.opTkn}, {self.node})'

#######################################
# PARSE RESULT
#######################################

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None
		self.advanceCount = 0

	def registerAdvance(self):
		self.advanceCount += 1

	def register(self, res):
		self.advanceCount += res.advanceCount
		if res.error: self.error = res.error
		return res.node

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		if not self.error or self.advanceCount == 0:
			self.error = error
		return self

#######################################
# PARSER
#######################################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tokenIdx = -1
		self.advance()

	def advance(self, ):
		self.tokenIdx += 1
		if self.tokenIdx < len(self.tokens):
			self.currentToken = self.tokens[self.tokenIdx]
		return self.currentToken

	def parse(self):
		res = self.expr()
		if not res.error and self.currentToken.type != TK_EOF:
			return res.failure(InvalidSyntaxError(
				self.currentToken.startPos, self.currentToken.endPos,
				"Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'AND' or 'OR'"
			))
		return res

	###################################

	def atom(self):
		res = ParseResult()
		token = self.currentToken

		if token.type in (TK_INT, TK_FLOAT):
			res.registerAdvance()
			self.advance()
			return res.success(NumberNode(token))

		elif token.type == TK_IDENTIFIER:
			res.registerAdvance()
			self.advance()
			return res.success(VarAccessNode(token))

		elif token.type == TK_LPRN:
			res.registerAdvance()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			if self.currentToken.type == TK_RPRN:
				res.registerAdvance()
				self.advance()
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.currentToken.startPos, self.currentToken.endPos,
					"Expected ')'"
				))

		return res.failure(InvalidSyntaxError(
			token.startPos, token.endPos,
			"Expected int, float, identifier, '+', '-', '('"
		))

	def power(self):
		return self.bin_op(self.atom, (TK_POW, ), self.factor)

	def factor(self):
		res = ParseResult()
		token = self.currentToken

		if token.type in (TK_PLUS, TK_MINUS):
			res.registerAdvance()
			self.advance()
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(token, factor))

		return self.power()

	def term(self):
		return self.bin_op(self.factor, (TK_MUL, TK_DIV))

	def arith_expr(self):
		return self.bin_op(self.term, (TK_PLUS, TK_MINUS))

	def comp_expr(self):
		res = ParseResult()

		if self.currentToken.matches(TK_KEYWORD, 'NOT'):
			opTkn = self.currentToken
			res.registerAdvance()
			self.advance()

			node = res.register(self.comp_expr())
			if res.error: return res
			return res.success(UnaryOpNode(opTkn, node))
		
		node = res.register(self.bin_op(self.arith_expr, (TK_EE, TK_NE, TK_LT, TK_GT, TK_LTE, TK_GTE)))
		
		if res.error:
			return res.failure(InvalidSyntaxError(
				self.currentToken.startPos, self.currentToken.endPos,
				"Expected int, float, identifier, '+', '-', '(' or 'NOT'"
			))

		return res.success(node)

	def expr(self):
		res = ParseResult()

		if self.currentToken.matches(TK_KEYWORD, 'VAR'):
			res.registerAdvance()
			self.advance()

			if self.currentToken.type != TK_IDENTIFIER:
				return res.failure(InvalidSyntaxError(
					self.currentToken.startPos, self.currentToken.endPos,
					"Expected identifier"
				))

			if len(self.currentToken.value) < 6 or len(self.currentToken.value) > 8:
				return res.failure(InvalidSyntaxError(
					self.currentToken.startPos, self.currentToken.endPos,
					"Identifiers must be 6-8 characters"
				))

			varName = self.currentToken
			res.registerAdvance()
			self.advance()

			if self.currentToken.type != TK_EQ:
				return res.failure(InvalidSyntaxError(
					self.currentToken.startPos, self.currentToken.endPos,
					"Expected '='"
				))

			res.registerAdvance()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			return res.success(VarAssignNode(varName, expr))

		node = res.register(self.bin_op(self.comp_expr, ((TK_KEYWORD, 'AND'), (TK_KEYWORD, 'OR'))))

		if res.error:
			return res.failure(InvalidSyntaxError(
				self.currentToken.startPos, self.currentToken.endPos,
				"Expected 'VAR', int, float, identifier, '+', '-', '(' or 'NOT'"
			))

		return res.success(node)

	###################################

	def bin_op(self, funcA, ops, funcB=None):
		if funcB == None:
			funcB = funcA
		
		res = ParseResult()
		left = res.register(funcA())
		if res.error: return res

		while self.currentToken.type in ops or (self.currentToken.type, self.currentToken.value) in ops:
			opTkn = self.currentToken
			res.registerAdvance()
			self.advance()
			right = res.register(funcB())
			if res.error: return res
			left = BinOpNode(left, opTkn, right)

		return res.success(left)

#######################################
# RUNTIME RESULT
#######################################

class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self

#######################################
# VALUES
#######################################

class Number:
	def __init__(self, value):
		self.value = value
		self.setPos()
		self.setContext()

	def setPos(self, startPos=None, endPos=None):
		self.startPos = startPos
		self.endPos = endPos
		return self

	def setContext(self, context=None):
		self.context = context
		return self

	def addedTo(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).setContext(self.context), None

	def subbedBy(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).setContext(self.context), None

	def multedBy(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).setContext(self.context), None

	def divedBy(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RTError(
					other.startPos, other.endPos,
					'Division by zero',
					self.context
				)

			return Number(self.value / other.value).setContext(self.context), None

	def powedBy(self, other):
		if isinstance(other, Number):
			return Number(self.value ** other.value).setContext(self.context), None

	def getComparisonEq(self, other):
		if isinstance(other, Number):
			return Number(int(self.value == other.value)).setContext(self.context), None

	def getComparisonNe(self, other):
		if isinstance(other, Number):
			return Number(int(self.value != other.value)).setContext(self.context), None

	def getComparisonLt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value < other.value)).setContext(self.context), None

	def getComparisonGt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value > other.value)).setContext(self.context), None

	def getComparisonLTE(self, other):
		if isinstance(other, Number):
			return Number(int(self.value <= other.value)).setContext(self.context), None

	def getComparisonGTE(self, other):
		if isinstance(other, Number):
			return Number(int(self.value >= other.value)).setContext(self.context), None

	def andedBy(self, other):
		if isinstance(other, Number):
			return Number(int(self.value and other.value)).setContext(self.context), None

	def oredBy(self, other):
		if isinstance(other, Number):
			return Number(int(self.value or other.value)).setContext(self.context), None

	def notted(self):
		return Number(1 if self.value == 0 else 0).setContext(self.context), None

	def copy(self):
		copy = Number(self.value)
		copy.setPos(self.startPos, self.endPos)
		copy.setContext(self.context)
		return copy
	
	def __repr__(self):
		return str(self.value)

#######################################
# CONTEXT
#######################################

class Context:
	def __init__(self, displayName, parent=None, parentEntryPos=None):
		self.displayName = displayName
		self.parent = parent
		self.parentEntryPos = parentEntryPos
		self.symbolTable = None

#######################################
# SYMBOL TABLE
#######################################

class SymbolTable:
	def __init__(self):
		self.symbols = {}
		self.parent = None

	def get(self, name):
		value = self.symbols.get(name, None)
		if value == None and self.parent:
			return self.parent.get(name)
		return value

	def set(self, name, value):
		self.symbols[name] = value

	def remove(self, name):
		del self.symbols[name]

#######################################
# INTERPRETER
#######################################

class Interpreter:
	def visit(self, node, context):
		method_name = f'visit{type(node).__name__}'
		method = getattr(self, method_name, self.noVisitMethod)
		return method(node, context)

	def noVisitMethod(self, node, context):
		raise Exception(f'No visit{type(node).__name__} method defined')

	###################################

	def visitNumberNode(self, node, context):
		return RTResult().success(
			Number(node.token.value).setContext(context).setPos(node.startPos, node.endPos)
		)

	def visitVarAccessNode(self, node, context):
		res = RTResult()
		varName = node.varNameToken.value
		value = context.symbolTable.get(varName)

		if not value:
			return res.failure(RTError(
				node.startPos, node.endPos,
				f"'{varName}' is not defined",
				context
			))

		value = value.copy().setPos(node.startPos, node.endPos)
		return res.success(value)

	def visitVarAssignNode(self, node, context):
		res = RTResult()
		varName = node.varNameToken.value
		value = res.register(self.visit(node.nodeValue, context))
		if res.error: return res

		context.symbolTable.set(varName, value)
		return res.success(value)

	def visitBinOpNode(self, node, context):
		res = RTResult()
		left = res.register(self.visit(node.leftNode, context))
		if res.error: return res
		right = res.register(self.visit(node.rightNode, context))
		if res.error: return res

		if node.opTkn.type == TK_PLUS:
			result, error = left.addedTo(right)
		elif node.opTkn.type == TK_MINUS:
			result, error = left.subbedBy(right)
		elif node.opTkn.type == TK_MUL:
			result, error = left.multedBy(right)
		elif node.opTkn.type == TK_DIV:
			result, error = left.divedBy(right)
		elif node.opTkn.type == TK_POW:
			result, error = left.powedBy(right)
		elif node.opTkn.type == TK_EE:
			result, error = left.getComparisonEq(right)
		elif node.opTkn.type == TK_NE:
			result, error = left.getComparisonNe(right)
		elif node.opTkn.type == TK_LT:
			result, error = left.getComparisonLt(right)
		elif node.opTkn.type == TK_GT:
			result, error = left.getComparisonGt(right)
		elif node.opTkn.type == TK_LTE:
			result, error = left.getComparisonLTE(right)
		elif node.opTkn.type == TK_GTE:
			result, error = left.getComparisonGTE(right)
		elif node.opTkn.matches(TK_KEYWORD, 'AND'):
			result, error = left.andedBy(right)
		elif node.opTkn.matches(TK_KEYWORD, 'OR'):
			result, error = left.oredBy(right)

		if error:
			return res.failure(error)
		else:
			return res.success(result.setPos(node.startPos, node.endPos))

	def visitUnaryOpNode(self, node, context):
		res = RTResult()
		number = res.register(self.visit(node.node, context))
		if res.error: return res

		error = None

		if node.opTkn.type == TK_MINUS:
			number, error = number.multedBy(Number(-1))
		elif node.opTkn.matches(TK_KEYWORD, 'NOT'):
			number, error = number.notted()

		if error:
			return res.failure(error)
		else:
			return res.success(number.setPos(node.startPos, node.endPos))

#######################################
# RUN
#######################################

globalSymbolTable = SymbolTable()
globalSymbolTable.set("NULL", Number(0))
globalSymbolTable.set("FALSE", Number(0))
globalSymbolTable.set("TRUE", Number(1))

def run(fn, text):
	# Generate tokens
	lexer = Lexer(fn, text)
	tokens, error = lexer.makeTokens()
	if error: return None, error
	
	# Generate AST
	parser = Parser(tokens)
	ast = parser.parse()
	if ast.error: return None, ast.error

	# Run program
	interpreter = Interpreter()
	context = Context('<program>')
	context.symbolTable = globalSymbolTable
	result = interpreter.visit(ast.node, context)

	return result.value, result.error
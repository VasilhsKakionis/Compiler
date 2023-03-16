from enum import Enum
import collections
import sys

EOF = -1	 	   # telos arxeiou
WORD = -2          #desmeumenh leksh
NUM = -3 	       #akeraia stathera    
ERROR1 = -4 	   #gramma meta apo arithmo 
ERROR2 = -5		   #stoixeio pou den uparxei sthn grammatikh
ERROR3 = -6		   #termatismos sxoliwn  


ADD = 10      	   # +
MINUS = 11    	   # -
MUL = 12 	 	   # *
DIV = 13		   # /
EQ = 14		       # =
LESS = 15	 	   # <
DIFF = 16	 	   # <>
LESSEQ = 17	 	   # <=
MORE = 18 	 	   # >
MOREEQ = 19	 	   # >=
TWODOTS = 20 	   # :
ASSIGN = 21	       # :=
SCOLON = 22		   # ;
COMMA = 23		   # ,
PER = 24		   # %
LPAR = 25	       # (
RPAR = 26		   # )
LBRA = 27		   # [
RBRA = 28		   # ]
ID = 29		 	   # anagnwristiko id



PROGRAMTK = 32     # program
ENDPROGRAMTK = 33  # endofprogram
DECLARATIONSTK = 34# declaration
IFTK = 35          # if
THENTK = 36		   # then
ELSETK = 37		   # else
ENDIFTK = 38	   # endif
DOWHILETK = 39		   # do
WHILETK = 40	   # while
ENDWHILETK = 41	   # endwhile
LOOPTK = 42	   # loop
ENDLOOPTK = 43	   # endloop
EXITTK = 44		   # exit
FORCASETK = 45	   # forcase
ENDFORCASETK = 46  # endforcase
INCASETK = 47	   # incase
ENDINCASETK = 48   # endincase
WHENTK = 49		   # when
DEFAULTTK = 50	   # default
ENDDEFAULTTK = 51  # enddefault
FUNCTIONTK = 52	   # function
ENDFUNCTIONTK = 53 # endfunction
RETURNTK = 54	   # return
INTK = 55		   # in
INOUTTK = 56	   # inout
INANDOUTTK = 57	   # inandout
ANDTK = 58		   # and
ORTK =59		   # or
NOTTK = 50		   # not
INPUTTK = 61	   # input
PRINTTK = 62	   # print
ENDDOWHILE = 63 #enddowhile


tk=""
token=""
str1=""
count_lines=1
a=0

quadList = list()
labelID = 0
countNewTemp = 0
listOfTemps = list()
returnDict = list()

loops = 0
exitStats = collections.OrderedDict()
exitQuads = list()

scopesList = list()
mainframe = 0
symtablefile = open("symbolTable.txt","w")

parametersEncountered = 0  
asmfile = open("finalCode.asm","w")
haltLabel = -1

class SymbolType(Enum):
	FUNCTION	= 0
	VARIABLE	= 1
	PARAMETER 	= 2
	TEMPVARIABLE= 3
	
symbolsForFile = {
	SymbolType.VARIABLE		: "Variable",
	SymbolType.FUNCTION		: "Function",
	SymbolType.PARAMETER	: "Parameter",
	SymbolType.TEMPVARIABLE	: "Temp Variable"
}

class Scope:
	# Constructor
	# nestingLevel: scope's nesting level
	# entities: list of scope's entities
	# previousScope: pointer to the immediate above Scope object
	# tempFrameLength: holds the frame length value of it's enclosed Scope
	def __init__(self, nestingLevel, previousScope):
		self.nestingLevel = nestingLevel
		self.entities = list()
		self.previousScope = previousScope
		self.tempFrameLength = 12 # Default value

	def __str__(self):
		return str(self.nestingLevel)

	def addEntity(self, newEntity):
		self.entities.append(newEntity)

	def setTempFrameLength(self):
		self.tempFrameLength += 4

	def getTempFrameLength(self):
		return self.tempFrameLength

	
class Entity:
	# Constructor
	# id: entity's identifier returned from lex
	# type: entity's type
	def __init__(self, id, typeOf):
		self.id = id
		self.typeOf = typeOf

	def __str__(self):
		return str(symbols.get(self.typeOf)) + ": " + self.id

	def toString(self):
		return str(symbolsForFile.get(self.typeOf)) + ": " + self.id

class Variable(Entity):
	# Constructor
	# offset: variable's offset
	def __init__(self, id, offset):
		super().__init__(id, SymbolType.VARIABLE)
		self.offset = offset

	def __str__(self):
		return super().__str__() + " || Offset = " + str(self.offset)

	def toString(self):
		return super().toString() + " || Offset = " + str(self.offset)

class Function(Entity):
	# Constructor
	# type: function 
	# startQuad: first label of function
	# frameLength: frame length of function
	def __init__(self, id, startQuad):
		super().__init__(id, SymbolType.FUNCTION)
		self.startQuad = startQuad
		self.args = list()
		self.frameLength = -1

	def __str__(self):
		return super().__str__() + " || Start Quad = " +\
			   str(self.startQuad) + " || Frame Length = " + str(self.frameLength)

	def toString(self):
		return super().toString() + " || Start Quad = " +\
			   str(self.startQuad) + " || Frame Length = " + str(self.frameLength)

	def setStartQuad(self, startQuad):
		self.startQuad = startQuad

	def setFrameLegth(self, frameLength):
		self.frameLength = frameLength

	def addArg(self, newArg):
		self.args.append(newArg)

class Parameter(Entity):
	# Constructor
	# offset: offset of parameter
	# parMode: CV = in || REF = inout || REV = inandout
	def __init__(self, id, offset, parMode):
		super().__init__(id, SymbolType.PARAMETER)
		self.offset = offset
		self.parMode = parMode

	def __str__(self):
		return super().__str__() + " || Offset = " + str(self.offset) + " || parMode = " +\
			   self.parMode

	def toString(self):
		return super().toString() + " || Offset = " + str(self.offset) + " || parMode = " +\
			   self.parMode
		
class TempVariable(Entity):
	# Constructor
	# offset:  offset of tempVar
	def __init__(self, id, offset):
		super().__init__(id, SymbolType.TEMPVARIABLE)
		self.offset = offset

	def __str__(self):
		return super().__str__() + " || Offset = " + str(self.offset)

	def toString(self):
		return super().toString() + " || Offset = " + str(self.offset)

class Argument():
	# Constructor
	# parMode: CV = call by value || REF = call by reference || REV = call by copy
	def __init__(self, parMode):
		self.parMode = parMode

	def __str__(self):
		return "ParMode = " + self.parMode

#
#
############## LEKTIKOS ANALYTHS ####################
#
#

def lex():
	array= [[0,1,2,ADD,MINUS,MUL,EQ,3,4,5,SCOLON,COMMA,LPAR,RPAR,LBRA,RBRA,6,EOF,ERROR2,0],
		    [WORD,1,1,WORD,WORD,WORD,WORD,WORD,WORD,WORD,WORD,WORD,WORD,WORD,WORD,WORD,WORD,EOF,WORD,WORD],
			[NUM,ERROR1,2,NUM,NUM,NUM,NUM,NUM,NUM,NUM,NUM,NUM,NUM,NUM,NUM,NUM,NUM,EOF,NUM,NUM],
			[LESS,LESS,LESS,LESS,LESS,LESS,LESSEQ,LESS,DIFF,LESS,LESS,LESS,LESS,LESS,LESS,LESS,LESS,LESS,LESS,LESS],
			[MORE,MORE,MORE,MORE,MORE,MORE,MOREEQ,MORE,MORE,MORE,MORE,MORE,MORE,MORE,MORE,MORE,MORE,MORE,MORE,MORE],
			[TWODOTS,TWODOTS,TWODOTS,TWODOTS,TWODOTS,TWODOTS,ASSIGN,TWODOTS,TWODOTS,TWODOTS,TWODOTS,TWODOTS,TWODOTS,TWODOTS,TWODOTS,TWODOTS,TWODOTS,TWODOTS,TWODOTS,TWODOTS],
			[DIV,DIV,DIV,DIV,DIV,8,DIV,DIV,DIV,DIV,DIV,DIV,DIV,DIV,DIV,DIV,7,DIV,DIV,DIV],
			[0,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,EOF,7,0],
			[8,8,8,8,8,9,8,8,8,8,8,8,8,8,8,8,8,ERROR3,8,8],
			[8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,0,ERROR3,8,8]]

	state = 0
	input1 = 0
	MAXLEN = 31  	   #xarakthres kai keno
	i=0
	pos = 0
	global tk 
	global token
	global count_lines
	while (state>=0 and state<10):
		c = f.read(1)
		if(c=="\n"):
			input1=19
		elif(c.isspace()):
			input1=0
		elif(c.isalpha()):
			input1=1
		elif(c.isdigit()):
			input1=2
		elif(c=="+"):
			input1=3
		elif(c=="-"):
			input1=4
		elif(c=="*"):
			input1=5
		elif(c=="="):
			input1=6
		elif(c=="<"):
			input1=7
		elif(c==">"):
			input1=8
		elif(c==":"):
			input1=9
		elif(c==";"):
			input1=10
		elif(c==","):
			input1=11
		elif(c=="("):
			input1=12
		elif(c==")"):
			input1=13
		elif(c=="["):
			input1=14
		elif(c=="]"):
			input1=15
		elif(c=="/"):
			input1=16
		elif(c==''):
			input1=17
			raise SystemExit()
		
		else:
			input1=18
			raise SystemExit()
		state = array[state][input1]
		if(token=="endprogra"):
			if(c == "m"):
				token=token+c
				MAXLEN-=1
				break
		if(MAXLEN>0 ):
			token=token+c
			MAXLEN-=1
		if(state==0):
			token=""
		if(state==0 and input1==19):
			count_lines+=1
		
	tk = token
	if(token == "endprogram"):
		return ENDPROGRAMTK

	if(state==ID or state==DIV or state==WORD or state==NUM or state==LESS or state==MORE or state==TWODOTS):
			pos = f.tell()
			c = f.seek(pos-1)
			token=token[:-1]
			tk = token

	if(state<=-4):
		if(tk==ERROR1):
			print("Line: "+str(count_lines))
			print("ERROR termatismos sxoliwn")
			raise SystemExit()
		elif(tk==ERROR2):
			print("Line: "+str(count_lines))
			print("ERROR stoixeio pou den uparxei sthn grammatikh")
			raise SystemExit()
		else:
			print("Line: "+str(count_lines))
			print("ERROR gramma meta apo arithmo")
			raise SystemExit()
	
	
	if(state>=10):
		token = ""
		return state
	elif(state==WORD):
		if(token=="program"):
			return PROGRAMTK
		elif(token=="declare"):
			return DECLARATIONSTK
		elif(token=="if"):
			return IFTK
		elif(token=="then"):
			return THENTK
		elif(token=="else"):
			return ELSETK
		elif(token=="endif"):
			return ENDIFTK
		elif(token=="dowhile"):
			return DOWHILETK
		elif(token=="while"):
			return WHILETK
		elif(token=="endwhile"):
			return ENDWHILETK
		elif(token=="loop"):
			return LOOPTK
		elif(token=="endloop"):
			return ENDLOOPTK
		elif(token=="exit"):
			return EXITTK
		elif(token=="forcase"):
			return FORCASETK
		elif(token=="endforcase"):
			return ENDFORCASETK
		elif(token=="incase"):
			return INCASETK
		elif(token=="endincase"):
			return ENDINCASETK
		elif(token=="when"):
			return WHENTK
		elif(token=="default"):
			return DEFAULTTK
		elif(token=="enddefault"):
			return  ENDDEFAULTTK
		elif(token=="function"):
			return FUNCTIONTK
		elif(token=="endfunction"):
			return ENDFUNCTIONTK
		elif(token=="return"):
			return RETURNTK
		elif(token=="in"):
			return INTK
		elif(token=="inout"):
			return INOUTTK
		elif(token=="inandout"):
			return INANDOUTTK
		elif(token=="and"):
			return ANDTK
		elif(token=="or"):
			return ORTK
		elif(token=="not"):
			return NOTTK
		elif(token=="input"):
			return INPUTTK
		elif(token=="print"):
			return PRINTTK
		elif(token=="enddowhile"):
			return ENDDOWHILE
		else:
			return ID
	elif(state==NUM):
		n = int(NUM)
		if(n>32767 or n<-32767):
			print("Line: "+str(count_lines))
			print("Only numbers between -32767<num<32676")
			raise SystemExit()
		else:
			return NUM

#
#
############## SYNTAKTIKOS ANALYTHS ####################
#
#

def optional_sign():
	global a
	if(a==ADD or a==MINUS):
		return add_oper()
	
def mul_oper():
	global a
	tok = tk
	if(a==MUL or a==DIV):
		a=lex()
	else:
		return None
	return tok
	
def add_oper():
	global a
	tok = tk
	if(a==ADD or a==MINUS):
		a = lex()
	else:
		return None
	return tok
	
def relational_oper():
	global a
	tok = tk
	if(a==EQ or a==LESSEQ or a==MOREEQ or a==MORE or a==LESS or a==DIFF):
		a = lex()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena '<,>,<>,+,<=,>=' kai vrika "+tk)
		raise SystemExit()
	return tok
	
def idtail():
	global a
	if(a==LPAR):
		return actualpars()
		

def factor():
	global a
	
	if(a==NUM):
		F = tk
		a = lex()
	elif(a==LPAR):
		a = lex()
		F = expression()
		if(a==RPAR):
			a = lex()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena ')' kai vrika "+tk)
			raise SystemExit()
	elif(a==ID):
		F = tk
		a = lex()
		tail = idtail()
		if(tail!=None):
			temp3 = newTemp()
			genQuad("par",temp3,"RET","_")
			genQuad("call",F,"_","_")
			F = temp3
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena 'constant' h '(' h 'id' "+tk)
		raise SystemExit()
	return F

def term():
	global a
	F1=factor()
	y = mul_oper()
	while(y != None):
		F2=factor()
		temp3 = newTemp()
		genQuad(y,str(F1),str(F2),temp3)
		F1 = temp3
		y = mul_oper()
	return F1

def expression():
	global a
	x =  optional_sign()
	T1 = term()
	if(x != None):
		temp = newTemp()
		genQuad(x,0,str(T1),str(temp))
		T1 = temp
	x = add_oper()
	while(x!=None):
		T2 = term()
		temp1 = newTemp()
		genQuad(x,str(T1),str(T2),str(temp1))
		T1 = temp1
		x = add_oper()
	return T1

def boolfactor():
	global a
	if(a==NOTTK):
		a = lex()
		if(a==LBRA):
			a = lex()
			BoolPlace = condition()
			BoolPlace = BoolPlace[::-1]
			if(a==RBRA):
				a = lex()
			else:
				print("Line: "+str(count_lines))
				print("ERROR perimena ']' kai vrika "+tk)
				raise SystemExit()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena '[' kai vrika "+tk)
			raise SystemExit()
	elif(a==LBRA):
		a = lex()
		BoolPlace = condition()
		if(a==RBRA):
			a = lex()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena ']' kai vrika "+tk)
			raise SystemExit()
	else:
		E1 = expression()
		relop = relational_oper()
		E2 = expression()
		BTrue = makeList(nextQuad())
		genQuad(relop,E1,E2,"_")
		n = nextQuad()
		BFalse = makeList(n)
		genQuad("jump","_","_",n)
		BoolPlace = (BTrue,BFalse)
	return BoolPlace
		
def boolterm():
	global a
	(bTrue5,bFalse5) = boolfactor()
	while(a==ANDTK):
		backpatch(bTrue5,nextQuad())
		a = lex()
		(bTrue6,bFalse6) =boolfactor()
		bFalse5 = mergeList(bFalse5,bFalse6)
		bTrue5 = bTrue6
	return (bTrue5,bFalse5)
		
def condition():
	global a
	(bTrue3,bFalse3)=boolterm()
	while(a==ORTK):
		backpatch(bFalse3,nextQuad())
		(bTrue4,bFalse4)=boolterm()
		bTrue3 = mergeList(bTrue3,bTrue4)
		bFalse3 = bFalse4
	return (bTrue3,bFalse3)
	
def actualparitem():
	global a
	if(a==INTK):
		a = lex()
		r3 = expression()
		genQuad("par",r3,"CV","_")
	elif(a==INOUTTK):
		a = lex()
		if(a==ID):
			b = tk
			a = lex()
			genQuad("par",b,"REF","_")
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena 'ID' kai vrika "+tk)
			raise SystemExit()
	elif(a==INANDOUTTK):
		a = lex()
		if(a==ID):
			genQuad("par",tk,"RET","_")
			a = lex()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena 'ID' kai vrika "+tk)
			raise SystemExit()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena 'INTK' h 'INOUT' h 'INANDOUT' kai vrika " +tk )
		raise SystemExit()
	return

def actualparlist():
	global a
	if(a==INTK or a==INOUTTK or a==INANDOUTTK):
		actualparitem()
		while(a==COMMA):
			a=lex()
			actualparitem()
	return

def actualpars():
	global a
	if(a==LPAR):
		a = lex()
		actualparlist()
		if(a==RPAR):
			a = lex()
			return 1
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena ')' kai vrika "+tk)
			raise SystemExit()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena '(' kai vrika " +tk)
		raise SystemExit()
	return 
		
def input_stat():
	global a
	if(a==ID):
		genQuad("inp","_","_",tk)
		a = lex()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena 'ID' kai vrika "+tk)
		raise SystemExit()
	return
		
def print_stat():
	global a
	r2 = expression()
	genQuad("out","_","_",r2)
	return
	
	
def return_stat():
	global a
	global returnDict
	r1 = expression()
	lastScope = len(scopesList) - 1
	returnDict = {lastScope: True}
	genQuad("retv","_","_",r1)	
	return


def incase_stat():
	global a
	w = newTemp()
	p1Quad = nextQuad()
	genQuad(":=","1","_",w)
	while(a==WHENTK):
		a = lex()
		if(a==LPAR):
			a = lex()
			(condTrue,condFalse) = condition()
			if(a==RPAR):
				a = lex()
				if(a==TWODOTS):
					a = lex()
					backpatch(condTrue,nextquad())
					genquad(":=",0,"_",w)
					statements()
					backpatch(condFalse,nextquad())
					return
				else:
					print("Line: "+str(count_lines))
					print("ERROR perimena 'TWODOTS' kai vrika "+tk)
					raise SystemExit()
			else:
				print("Line: "+str(count_lines))
				print("ERROR perimena 'RPAR' kai vrika "+tk)
				raise SystemExit()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena 'LPAR' kai vrika "+tk)
			raise SystemExit()
	if(a==ENDINCASETK):
		a = lex()
		genquad("=",w,0,p1Quad)
		#return
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena 'ENDINCASETK' kai vrika "+tk)
		raise SystemExit()
	return
	
def forcase_stat():
	global a
	TQuad = nextQuad()
	while(a==WHENTK):
		a = lex()
		if(a==LPAR):
			a = lex()
			(bTrue2,bFalse2) = condition()
			if(a==RPAR):
				a = lex()
				if(a==TWODOTS):
					backpatch(bTrue2,nextQuad())
					a = lex()
					statements()
					genQuad("jump","_","_",TQuad)
					backpatch(bFalse2,nextQuad())
					#return
				else:
					print("Line: "+str(count_lines))
					print("ERROR perimena 'TWODOTS' kai vrika "+tk)
					raise SystemExit()
					
			else:
				print("Line: "+str(count_lines))
				print("ERROR perimena ')' kai vrika "+tk)
				raise SystemExit()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena '(' kai vrika "+tk)
			raise SystemExit()
	if(a==DEFAULTTK):
		a = lex()
		TQuad = nextQuad()
		if(a==TWODOTSTK):
			a=lex()
			statements()
			if(a==ENDDEFAULTTK):
				a = lex()
				if(a==ENDFORCASE):
					a = lex()
					#return
				else:
					print("Line: "+str(count_lines))
					print("ERROR perimena 'ENDFORCASE' kai vrika "+tk)
					raise SystemExit()
			else:
				print("Line: "+str(count_lines))
				print("ERROR perimena 'ENDDEFAULTTK' kai vrika "+tk)
				raise SystemExit()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena 'DEFAULTTK' kai vrika "+tk)
			raise SystemExit()
					
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena 'FORCASETK' kai vrika "+tk)
		raise SystemExit()
	return

def exit_stat():
	global a
	global loops
	if(a==EXITTK):
		if(loops == 0):
			print("Line: "+str(count_lines))
			print("ERROR vrika 'EXIT' eksw apo loop")
			raise SystemExit()
		t = nextQuad()
		tempList = makeList(t)
		exitQuads.append(tempList)
		exitStats[tempList[0]] = loops
		a = lex()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena 'EXIT' kai vrika "+tk)
		raise SystemExit()
	return

def loop_stat():
	global a
	global loops
	loops += 1
	exitStats[None] = None
	rQuad = nextQuad()
	statements()
	if(a==ENDLOOPTK):
		genQuad("jump","_","_",rQuad)
		if(exitStats):
			for i, extLabel in reversed(list(enumerate(exitStats.keys()))):
				if(exitStats[extLabel] == loops):
					backpatch(exitQuads[i-1],nextQuad())
					exitStats.popitem()
					exitQuads.pop(i-1)
		loops -= 1
		a = lex()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena 'ENDLOOP' kai vrika "+tk)
		raise SystemExit()
	return
	
def do_while_stat():
	global a
	statements()
	if(a==ENDDOWHILE):
		a = lex()
		if(a==LPAR):
			a = lex()
			sQuad = nextQuad()
			(bTrue7,bFalse8) = condition()
			backpatch(bFalse8,sQuad)
			backpatch(bTrue7,nextQuad())
			if(a==RPAR):
				a = lex()
				return
			else:
				print("Line: "+str(count_lines))
				print("ERROR perimena ')' kai vrika "+tk)
				raise SystemExit()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena '(' kai vrika "+tk)
			raise SystemExit()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena 'DOWHILETK' kai vrika "+tk)
		raise SystemExit()
	return
	
def while_stat():
	global a
	if(a==LPAR):
		a = lex()
		b = nextQuad()
		(bTrue1,bFalse2)=condition()
		if(a==RPAR):
			a = lex()
			backpatch(b1True,nextQuad())
			statements()
			if(a==ENDWHILETK):
				a = lex()
				genQuad("jump","_","_",b)
				backpatch(bFalse2,nextQuad())
			else:
				print("Line: "+str(count_lines))
				print("ERROR perimena 'endwhile' kai vrika "+tk)
				raise SystemExit()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena 'RPAR' kai vrika "+tk)
			raise SystemExit()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena 'LPAR' kai vrika "+tk)
		raise SystemExit()
	return
		
def elsepart():
	global a
	if(a==ELSETK):
		a = lex()
		statements()
	return

def if_stat():
	global a
	if(a==LPAR):
		a = lex()
		(bTrue,bFalse)=condition()
		if(a==RPAR):
			a = lex()
			if(a==THENTK):
				a = lex()
				backpatch(bTrue,nextQuad())
				statements()
				x = nextQuad()
				ifList = makeList(x)
				genQuad("jump","_","_",str(x))
				backpatch(bFalse,nextQuad())
				elsepart()
				backpatch(ifList,nextQuad())
				if(a==ENDIFTK):
					a = lex()
				else:
					print("Line: "+str(count_lines))
					print("ERROR perimena 'endif' kai vrika "+tk)
					raise SystemExit()
			else:
				print("Line: "+str(count_lines))
				print("ERROR perimena then kai vrika "+tk)
				raise SystemExit()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena ')' kai vrika "+tk)
			raise SystemExit()
	else:
		print("Line: "+count_lines)
		print("ERROR perimena '(' kai vrika "+tk)
		raise SystemExit()
	return 

def assignment_stat():
	global a
	if(a==ASSIGN):
		a = lex()
		op1 = expression()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena := kai vrika "+tk)
		raise SystemExit()
	return op1
		
def statement():
	global a
	if(a==ID):
		op3 = tk
		a = lex()
		op1 = assignment_stat()
		genQuad(":=",op1,"_",op3)
	elif(a==IFTK):
		a = lex()
		if_stat()
	elif(a==WHILETK):
		a = lex()
		while_stat()
	elif(a==DOWHILETK):
		a = lex()
		do_while_stat()
	elif(a==LOOPTK):
		a = lex()
		loop_stat()
	elif(a==EXITTK):
		exit_stat()
	elif(a==FORCASETK):
		a = lex()
		forcase_stat()
	elif(a==INCASETK):
		a = lex()
		incase_stat()
	elif(a==RETURNTK):
		a = lex()
		return_stat()
	elif(a==INPUTTK):
		a = lex()
		input_stat()
	elif(a==PRINTTK):
		a = lex()
	return

def statements():
	global a
	statement()
	while(a==SCOLON):
		a = lex()
		statement()
	#statement()
	return

def formalparitem(name):
	global a
	global listOfTemps
	if(a==INTK or a==INOUTTK or a==INANDOUTTK):
		b = a
		a = lex()
		listOfTemps.append(tk)
		if(b==INTK):
			addArgument(name, "CV")
			addParameter(tk, "CV")
		elif(b==INOUTTK):
			addArgument(name, "REF")
			addParameter(tk, "REF")
		elif(b==INANDOUTTK):
			addArgument(name, "REV")
			addParameter(tk, "REV")
	if(a==ID):
		a=lex()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena in or inout or inandout kai vrika "+tk)
		raise SystemExit()
	return

		
def formalparlist(name):
	global a
	global listOfTemps
	if(a==INTK or a==INOUTTK or a==INANDOUTTK):
		b = a
		a = lex()
		listOfTemps.append(tk)
		if(b==INTK):
			addArgument(name, "CV")
			addParameter(tk, "CV")
		elif(b==INOUTTK):
			addArgument(name, "REF")
			addParameter(tk, "REF")
		elif(b==INANDOUTTK):
			addArgument(name, "REV")
			addParameter(tk, "REV")
		formalparitem(name)
		while(a==COMMA):
			a = lex()
			formalparitem(name)
	return

def formalpars(name):
	global a
	if(a==LPAR):
		a = lex()
		formalparlist(name)
		if(a==RPAR):
			a = lex()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena ) kai vrika "+tk)
			raise SystemExit()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena ( kai vrika "+tk)
		raise SystemExit()
	return 

def funcbody(name):
	formalpars(name)
	block(name)
	return
	
def subprogram():
	global a
	global returnDict
	if(a==ID):
		name = tk
		addFunction(name)
		a = lex()
		funcbody(name)
		lastScope = len(scopesList)
		if(returnDict.get(lastScope) != True):
			print("ERROR leipei to return apo thn sunarthsh ")
			raise SystemExit()
		else:
			del returnDict[lastScope]
		if(a==ENDFUNCTIONTK):
			a = lex()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena endfunction kai vrika "+tk)
			raise SystemExit()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena id kai vrika "+tk)
		raise SystemExit()
	return 

def subprograms():
	global a
	while(a==FUNCTIONTK):
		createScope()
		a = lex()
		subprogram()
	return

def varlist():
	global a
	global listOfTemps
	if(a==ID):
		listOfTemps.append(tk)
		addVariable(tk)
		a = lex() 
		while(a==COMMA):
			a = lex()
			if(a==ID):
				listOfTemps.append(tk)
				addVariable(tk)
				a = lex()
			else:
				print("Line: "+str(count_lines))
				print("ERROR perimena , kai vrika "+tk)
				raise SystemExit()
	return
		
def declarations():
	global a
	while(a==DECLARATIONSTK):
		a = lex()
		varlist()
		if(a==SCOLON):
			a = lex()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena ; kai vrika "+tk)
			raise SystemExit()
	return 

def block(name):
	global haltLabel
	declarations()
	subprograms()
	startQuad = setFunctionStartQuad(name)
	genQuad("begin_block",name,"_","_")
	statements()
	if ( tk == "endprogram"):
		haltLabel = nextQuad()
		genQuad("halt","_","_","_")
	genQuad("end_block",name,"_","_")
	setFunctionFrameLength(name, scopesList[-1].tempFrameLength)
	printScopesToFile()
	for i in range(5*startQuad,len(quadList),5):
		quadToAsm(quadList[i],quadList[i+1],quadList[i+2],quadList[i+3],quadList[i+4], name)
	del scopesList[-1]
	return

		
def program():
	global a
	global main_name
	global nestingLevel
	if(a==PROGRAMTK):
		a = lex()
		if(a==ID):
			main_name = tk
			scopesList.append(Scope(0,None))
			a = lex()
			block(main_name)
			if(a==ENDPROGRAMTK):
				return 1
			else:
				print("Line: "+str(count_lines))
				print("ERROR perimena endprogram kai vrika "+str(count_lines))
				raise SystemExit()
		else:
			print("Line: "+str(count_lines))
			print("ERROR perimena ID kai vrika "+tk)
			raise SystemExit()
	else:
		print("Line: "+str(count_lines))
		print("ERROR perimena program kai vrika "+tk)
		raise SystemExit()

#
#
############## ENDIAMESOS KWDIKAS ####################
#
#

def nextQuad():
	return labelID
	
def genQuad(name,op1,op2,op3):
	global labelID
	quadList.append(labelID)
	quadList.append(name)
	quadList.append(op1)
	quadList.append(op2)
	quadList.append(op3)
	labelID+=1
	
def newTemp():
	global countNewTemp
	global listOfTemps
	newVar = "T_"+str(countNewTemp)
	listOfTemps.append(newVar)
	countNewTemp+=1
	offset = scopesList[-1].getTempFrameLength()
	scopesList[-1].addEntity(TempVariable(newVar, offset))
	scopesList[-1].setTempFrameLength()
	return newVar

def emptyList():
	return list()
	
def makeList(label):
	newList = emptyList()
	newList.append(label)
	return newList
	
def mergeList(list1,list2):
	return list1+list2
	
def backpatch(list1,z):
	for i in range(0,len(quadList),5):
		if quadList[i] in list1:
			quadList[i+4] = z

def Quads(quadList):
	
	q = open("test.int","w")

	for i in range(0,len(quadList),5) :
		u = str(quadList[i])+" "+str(quadList[i+1])+" "+str(quadList[i+2])+" "+str(quadList[i+3])+" "+str(quadList[i+4])+"\n"
		q.write(u)
		
	q.close()
	
			
def CodeToC(quadList,listOfTemps):
	  
	cCode=open("test.c","w")

	listOfTemps = list(dict.fromkeys(listOfTemps))
		
	cCode.write('#include <stdio.h>\n')
	cCode.write('#include <stdlib.h>')
	cCode.write('\n\n')
	cCode.write("int main()")
	cCode.write("\n")
	cCode.write("{")
	cCode.write("\n")
	cCode.write("int ")
	
	for k in range(0,len(listOfTemps),1):
		if(k==len(listOfTemps)-1):
			cCode.write(listOfTemps[k]+"; \n")
		else:
			cCode.write(listOfTemps[k]+", ")
			
	for i in range(0,len(quadList),5):
		label="L_" + str(quadList[i]);
			
		if((quadList[i+1]=="+") or (quadList[i+1]=="-") or (quadList[i+1]=="*") or (quadList[i+1]=="/")):
			cCode.write("   "+label +":" +str(quadList[i+4]) + "=" + ( quadList[i+2]) +  str(quadList[i+1]) +(quadList[i+3])+";\n")
		elif((quadList[i+1]=="<") or (quadList[i+1]==">") or (quadList[i+1]=="<=") or (quadList[i+1]==">=") or (quadList[i+1]=="=") or (quadList[i+1]=="<>")):
			cCode.write("   "+label +" : if ( "+ str(quadList[i+2]) + str(quadList[i+1]) + str(quadList[i+3]) +  " ) " + " goto "+str(quadList[i+4]) +";\n") 
		elif(quadList[i+1]=="jump"):
			cCode.write("   "+label + ": goto L_" + str(quadList[i+4])+";\n")
		elif(quadList[i+1]==":="):
			cCode.write("   "+ label + ": " + str(quadList[i+4])+ " = " + str(quadList[i+2])+";\n")
		elif(quadList[i+1]=="halt"):
			cCode.write("   "+label+': {}\n')
		elif(quadList[i+1]=="begin_block"):
			cCode.write("   "+label+" : \n")
		elif(quadList[i+1]=="out"):
			cCode.write("   "+label + ": printf(\""+ str(quadList[i+4])+"=%d\", "+ str(quadList[i+4])+");\n")
		elif(quadList[i+1] == "end_block"):
			cCode.write("   "+label+": \n")
		elif(quadList[i+1] == "retv"):
			cCode.write("   "+label+" : return " +str(quadList[i+4]) +"\n")
		elif(quadList[i+1] == "call"):
			cCode.write("   "+label+" : call " +str(quadList[i+2]) +"\n")
		elif(quadList[i+1] == "inp"):
			cCode.write("   "+label+" : input (" +str(quadList[i+4] +")\n"))
	cCode.write("\n")
	cCode.write("}")
	cCode.close()

	
#
#
############## PINAKAS SYMBOLWN ####################
#
#

# Create a new scope
def createScope():
	scopesList.append(Scope(scopesList[-1].nestingLevel + 1, scopesList[-1]))

# Add a new function to the entities list
def addFunction(id):
	if(checkScopeForEntity(id, SymbolType.FUNCTION, scopesList[-1].previousScope.nestingLevel) == True):
		print(" H sunarthsh '" + id + "' exei hdh oristei.")
		raise SystemExit()
	scopesList[-2].addEntity(Function(id,-1))

# Add a variable entity to the entities list
def addVariable(id):
	if (checkScopeForEntity(id, SymbolType.VARIABLE, scopesList[-1].nestingLevel) == True):
		print(" H metavlhth '" + id + "' exei hdh oristei se auto scope.")
		raise SystemExit()
	if (checkScopeForEntity(id, SymbolType.PARAMETER ,scopesList[-1].nestingLevel) == True):
		print( " H metavlhth '" + id + "' exei hdh oristei se auto scope.")
		raise SystemExit()
	offset = scopesList[-1].getTempFrameLength()
	scopesList[-1].addEntity(Variable(id, offset))
	scopesList[-1].setTempFrameLength()

# Add a parameter entity to the entities list
def addParameter(id, parMode):
	if (checkScopeForEntity(id, SymbolType.PARAMETER, scopesList[-1].nestingLevel) == True):
		print( " H parametros '" + id + "' exei hdh oristei se auto scope.")
		raise SystemExit()
	offset = scopesList[-1].getTempFrameLength()
	scopesList[-1].addEntity(Parameter(id, offset, parMode))
	scopesList[-1].setTempFrameLength()

# Add an argument to the function "funcId"
def addArgument(funcId, parMode):
	newArgument = Argument(parMode)
	function = findEntity(funcId, SymbolType.FUNCTION)[0]
	if (function == None):
		print( "H sunarthsh '" + funcId + "' den exei oristei.")
		raise SystemExit()
	function.addArg(newArgument)
	
	

# Set the startQuad of the function
def setFunctionStartQuad(id):
	startQuad = nextQuad()
	if (id == main_name):
		return startQuad
	else:
		function = findEntityWithNoFrameLen(id, SymbolType.FUNCTION)
		if (function == None):
			print( " H sunarthsh'" + function + "' den exei oristei.")
			raise SystemExit()
		function.setStartQuad(startQuad)
		return startQuad
		

# Set the framelength of the function
def setFunctionFrameLength(id, framelength):
	global mainframe
	if (id == main_name):
		mainframe = framelength
		return
	else:
		function = findEntityWithNoFrameLen(id, SymbolType.FUNCTION)
		function.setFrameLegth(framelength)

		

# Check if an entity "id" of type "typeOf" exists at scope "nestingLevel"
def checkScopeForEntity(id, typeOf, nestingLevel):
	if (nestingLevel > scopesList[-1].nestingLevel):
		print("Den uparxei to entity")
		return False
	else:
		currentScope = scopesList[nestingLevel]
		for i in range(len(currentScope.entities)):
			x = currentScope.entities[i]
			for j in range(len(currentScope.entities)):
				y = currentScope.entities[j]
				if x.id == y.id and x.typeOf == y.typeOf and x.id == id and x.typeOf == typeOf:
						return True
		return False

# Find an entity named "id" and of type "typeOf"
# Return that entity along with the level it was found on
def findEntity(id, typeOf):
	currentScope = scopesList[-1]
	while(currentScope != None):
		for i in range(len(currentScope.entities)):
			if(currentScope.entities[i].id == id and currentScope.entities[i].typeOf == typeOf):
				return (currentScope.entities[i], currentScope.nestingLevel)
		currentScope = currentScope.previousScope
	return (None, None)


# Returns the first entity with name "id" and of type "typeOf"
# which hasn't had its framelength updated yet
def findEntityWithNoFrameLen(id, typeOf):
	currentScope = scopesList[-1]
	while(currentScope != None):
		for i in range(len(currentScope.entities)):
			if (currentScope.entities[i].id == id and currentScope.entities[i].typeOf == typeOf):
				if (currentScope.entities[i].frameLength != -1):
					break
				else:
					return currentScope.entities[i]
		currentScope = currentScope.previousScope

#print Scopes to file of symbol table
def printScopesToFile():

	for currentScope in scopesList:
		symtablefile.write("    " * (currentScope.nestingLevel) + " Scope " + str(currentScope) + "\n")
		for currentEntity in currentScope.entities:
			symtablefile.write("    " * (currentScope.nestingLevel) + "  " + str(currentEntity.toString()) + "\n")
			if (isinstance(currentEntity, Function)):
				for i,currentArg in enumerate(currentEntity.args):
					symtablefile.write("    " * (currentScope.nestingLevel+1) + " " + str(i+1) + " " + str(currentArg) + "\n")
	symtablefile.write("\n")
	symtablefile.write(" Main Program's Framelength: " + str(mainframe) + "\n")
	symtablefile.write("\n")

#
#
############## TELIKOS KWDIKAS ####################
#
#
	
# Find and return an entity named "id" with the level it was found 
def findEntityWithNoType(id):
	if (scopesList == list()):
		return
	currScope = scopesList[-1]
	while (currScope != None):
		for currEntity in currScope.entities:
			if (currEntity.id == id):
				return (currEntity, currScope.nestingLevel)
		currScope = currScope.previousScope
	return (None, None)	


#search for a variable which took as argument and store it to a register
def gnlvcode(var):
	(entity, nestLevel) = findEntityWithNoType(var)
	if(entity == None or entity.typeOf == SymbolType.FUNCTION):
		print(" H metavlhth '" + var + "'den exei oristei.")
		raise SystemExit()
	asmfile.write("    lw  $t0, -4($sp)\n")
	counter = scopesList[-1].nestingLevel - nestLevel - 1 # N-1 times
	for i in range(counter, 0, -1):
		asmfile.write("	   lw  $t0, -4($t0)\n")
	asmfile.write("    add  $t0, $t0, -"+str(entity.offset)+"\n" )

#take a value and a register as arguments and store the value to the register
def loadvr(v, r):
	register = "t" + str(r)
	if (str(v).isdigit()):
		asmfile.write("    li  $"+str(register)+", "+str(v)+"\n" )
		return
	(entity, level) = findEntityWithNoType(v)
	if(entity == None):
		print(" H metavlhth '" + v + "' den exei oristei")
		raise SystemExit()
	currentScope = scopesList[-1].nestingLevel
	if (level == 0 and entity.typeOf == SymbolType.VARIABLE):
		asmfile.write("    lw  $"+str(register)+", -"+str(entity.offset)+"($s0)\n" )
	elif (entity.typeOf == SymbolType.TEMPVARIABLE):
		asmfile.write("    lw  $"+str(register)+", -"+str(entity.offset)+"($sp)\n")
	elif (level == currentScope and entity.typeOf != SymbolType.FUNCTION):
		if (entity.typeOf == SymbolType.VARIABLE or\
		   (entity.typeOf == SymbolType.PARAMETER and entity.parMode == "CV")):
		   asmfile.write("    lw  $"+str(register)+", -"+str(entity.offset)+"($sp)\n")
		elif (entity.typeOf == SymbolType.PARAMETER and entity.parMode == "REF"):
			asmfile.write("    lw  $t0, -"+str(entity.offset)+"($sp)\n")
			asmfile.write("    lw  $"+str(register)+", ($t0)\n")	
	elif (level < currentScope):
		if (entity.typeOf == SymbolType.VARIABLE or\
		   (entity.typeOf == SymbolType.PARAMETER and entity.parMode == "CV")):
		   gnlvcode(v)
		   asmfile.write("    lw  $"+register+", ($t0)\n")
		elif (entity.typeOf == SymbolType.PARAMETER and entity.parMode == "REF"):
			gnlvcode(v)
			asmfile.write("    lw  $t0, ($t0)\n")
			asmfile.write("    lw  $"+register+", ($t0)\n")
	else:
		print("ERROR")
		raise SystemExit()

#take a register and a place of memory as arguments and store the register to this place
def storerv(r, v):
	register = "t" + str(r)
	(entity, level) = findEntityWithNoType(v)
	if(entity == None):
		print(" H metavlhth '" + v + "' den exei oristei")
		raise SystemExit()
	currentScope = scopesList[-1].nestingLevel
	if (level == 0 and entity.typeOf == SymbolType.VARIABLE):
		asmfile.write("    sw  $"+str(register)+", -"+str(entity.offset)+"($s0)\n")
	elif (entity.typeOf == SymbolType.TEMPVARIABLE):
		asmfile.write("    sw  $"+str(register)+", -"+str(entity.offset)+"($sp)\n")
	elif (level == currentScope and entity.typeOf != SymbolType.FUNCTION):
		if (entity.typeOf == SymbolType.VARIABLE or\
		   (entity.typeOf == SymbolType.PARAMETER and entity.parMode == "CV")):
		   asmfile.write("    sw  $"+str(register)+", -"+str(entity.offset)+"($sp)\n")
		elif (entity.typeOf == SymbolType.PARAMETER and entity.parMode == "REF"):
			asmfile.write("    lw  $t0, -"+str(entity.offset)+"($sp)\n")
			asmfile.write("    sw  $"+str(register)+", ($t0)\n")	
	elif (level < currentScope):
		if (entity.typeOf == SymbolType.VARIABLE or\
		   (entity.typeOf == SymbolType.PARAMETER and entity.parMode == "CV")):
		   gnlvcode(v)
		   asmfile.write("    sw  $"+str(register)+", ($t0)\n")
		elif (entity.typeOf == SymbolType.PARAMETER and entity.parMode == "REF"):
			gnlvcode(v)
			asmfile.write("    lw  $t0, ($t0)\n")
			asmfile.write("    sw  $"+str(register)+", ($t0)\n")
	else:
		print("ERROR")
		raise SystemExit()


def quadToAsm(label,quadName,op1,op2,op3, name):
	global parametersEncountered
	if (str(label == 0)):
		asmfile.write("                  ")
	asmfile.write('\nL_' + str(label) + ':\n')
	if(quadName == '+'):
		loadvr(op1, 1)
		loadvr(op2, 2)
		asmfile.write("    add  $t1, $t1, $t2\n")
		storerv(1, op3)
	elif(quadName == '-'):
		loadvr(op1, 1)
		loadvr(op2, 2)
		asmfile.write("    sub  $t1, $t1, $t2\n")
		storerv(1,op3)
	elif(quadName == '*'):
		loadvr(op1, 1)
		loadvr(op2, 2)
		asmfile.write("    mul  $t1, $t1, $t2\n")
		storerv(1,op3)
	elif(quadName =='/'):
		loadvr(op1, 1)
		loadvr(op2, 2)
		asmfile.write("    div  $t1, $t1, $t2\n")
		storerv(1,op3)
	if(quadName == '<'):
		loadvr(op1, 1)
		loadvr(op2, 2)
		asmfile.write("    blt  $t1, $t2, L_"+str(op3)+"\n")
	elif(quadName == '<='):
		loadvr(op1, 1)
		loadvr(op2, 2)
		asmfile.write("    ble  $t1, $t2, L_"+str(op3)+"\n")
	elif(quadName == '>'):
		loadvr(op1, 1)
		loadvr(op2, 2)
		asmfile.write("    bgt  $t1, $t2, L_"+str(op3)+"\n")
	elif(quadName == '>='):
		loadvr(op1, 1)
		loadvr(op2, 2)
		asmfile.write("    bge  $t1, $t2, L_"+str(op3)+"\n")
	elif(quadName == '='):
		loadvr(op1, 1)
		loadvr(op2, 2)
		asmfile.write("    beq  $t1, $t2, L_"+str(op3)+"\n")
	elif(quadName == '<>'):
		loadvr(op1, 1)
		loadvr(op2, 2)
		asmfile.write("    bne  $t1, $t2, L_"+str(op3)+"\n")
	elif (quadName == ':='):
		loadvr(op1, 1)
		storerv(1,op3)
	elif (quadName == 'jump'):
		asmfile.write("    j  L_"+str(op3)+"\n")
	elif (quadName == 'retv'):
		loadvr(op3, 1)
		asmfile.write("    lw  $t0, -8($sp)\n")
		asmfile.write("    sw  $t1, ($t0)\n")
		asmfile.write("    lw  $ra, ($sp)\n")
		asmfile.write("    jr  $ra\n")
	elif(quadName == 'call'):
		if(name == main_name):
			callerFramelength = mainframe
			callerScope = 0
		else:
			(callerFunction, callerScope) = findEntity(name, SymbolType.FUNCTION)
			callerFramelength = callerFunction.frameLength
		(calleeFunction, calleeScope) = findEntity(op1, SymbolType.FUNCTION)
		if(calleeFunction == None):
			print( " H sunarthsh '" + op1 + "' den exei oristei akomh ")
			raise SystemExit()
		if (calleeScope == callerScope):
			asmfile.write("    lw  $t0, -4($sp)\n")
			asmfile.write("    sw  $t0, -4($fp)\n")
		else:
			asmfile.write("    sw  $sp, -4($fp)\n")
		asmfile.write("    addi  $sp, $sp, -"+str(callerFramelength)+"\n")
		asmfile.write("    jal  L_"+str(calleeFunction.startQuad)+"\n")
		asmfile.write("    addi  $sp, $sp, "+str(callerFramelength)+"\n")
	elif(quadName == 'out'):
		asmfile.write("    li  $v0, 4\n")
		asmfile.write("    li  $a0, "+str(op3)+"\n")
		asmfile.write("    syscall\n")
	elif(quadName == 'inp'):
		asmfile.write("    li  $v0, 5\n")
		asmfile.write("    syscall\n")
		storerv(1, op3)
	elif(quadName == 'par'):
		if(name == main_name):
			callerFramelength = mainframe
			callerScope = 0
		else:
			(callerFunction, callerScope) = findEntity(name, SymbolType.FUNCTION)
			callerFramelength = callerFunction.frameLength
		if (parametersEncountered == 0):
			asmfile.write("    addi  $fp, $sp, -"+str(callerFramelength)+"\n")
		offset = 12 + 4 * (parametersEncountered-1)
		if (op2 == 'CV'):
			loadvr(op1, 0)
			asmfile.write("    sw  $t0, -"+str(offset)+"($fp)\n")
		elif (op2 == 'REF'):
			(paramEntity, paramScope) = findEntityWithNoType(op1)
			if (paramEntity == None):
				print(" Variable '" + op1 + "' has not been declared.")
				raise SystemExit()
			if (paramScope == callerScope):
				if (paramEntity.typeOf == SymbolType.VARIABLE or \
				   (paramEntity.typeOf == SymbolType.PARAMETER and paramEntity.parMode == 'CV')):
					asmfile.write("    add  $t0, $sp, -"+str(paramEntity.offset)+"\n")
					asmfile.write("    sw  $t0, -"+str(offset)+"($fp)\n")
				elif (paramEntity.typeOf == SymbolType.PARAMETER and paramEntity.parMode == 'REF'):
					asmfile.write("    lw  $t0, -"+str(paramEntity.offset)+"($sp)\n")
					asmfile.write("    sw  $t0, -"+str(offset)+"($fp)\n")
			else:
				if (paramEntity.typeOf == SymbolType.VARIABLE or \
				   (paramEntity.typeOf == SymbolType.PARAMETER and paramEntity.parMode == 'CV')):
				   gnlvcode(op1)
				   asmfile.write("    sw  $t0, -"+str(offset)+"($fp)\n")
				elif (paramEntity.typeOf == SymbolType.PARAMETER and paramEntity.parMode == 'REF'):
					gnlvcode(op1)
					asmfile.write("    lw  $t0, ($t0)\n")
					asmfile.write("    sw  $t0, -"+str(offset)+"($fp)\n")
		elif (op2 == 'RET'):
			paramEntity, paramScope = findEntityWithNoType(op1)
			if (paramEntity == None):
				print(" Variable '" + op1 + "' has not been declared.")
				raise SystemExit()
			asmfile.write("    add  $t0, $sp, -"+str(paramEntity.offset)+"\n")
			asmfile.write("    sw  $t0, -8($fp)\n")
	elif (quadName == 'begin_block'):
		asmfile.write("    sw  $ra, ($sp)\n")
		if (op1 == main_name):
			asmfile.seek(0)
			asmfile.write("    j  L_"+str(label)+"\n\n")
			asmfile.seek(0,2)
			asmfile.write("    add  $sp, $sp, "+str(mainframe)+"\n")
			asmfile.write("    move  $s0, $sp\n")
	elif (quadName == 'end_block'):
		if (op1 == main_name):
			asmfile.write("    j  L_"+str(haltLabel)+"\n")
			asmfile.write("\n\n")
		else:
			asmfile.write("    lw  $ra, ($sp)\n")
			asmfile.write("    jr  $ra\n")
	elif (quadName == 'halt'):
		asmfile.write("    li  $v0, 10\n")
		asmfile.write("    syscall\n")
	
#
#
############## "MAIN" ####################
#
#
	
if(len(sys.argv) <= 1):
    print('ERROR: You must enter a starlet file')
    exit(1)
# open the entered starlet file
f = open(sys.argv[1],'r') 
a = lex()
b = program()
if(b==1):
	print("PROGRAM IS OK")
Quads(quadList)
CodeToC(quadList,listOfTemps)
asmfile.close()
symtablefile.close()
f.close()





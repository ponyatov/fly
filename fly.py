
import os,sys ; print sys.argv

################################################################# frame system

class Frame:
    def __init__(self,V):
        self.type  = self.__class__.__name__.lower()
        self.val   = V
        self.slot  = {}
        self.nest  = []
        self.immed = False
        
    ## dump
    
    def __repr__(self):
        return self.dump()
    def dump(self,depth=0,prefix=''):
        tree = self.pad(depth) + self.head(prefix)
        if not depth: Frame.dumped = []
        if self in Frame.dumped: return tree + ' _/'
        else: Frame.dumped.append(self)
        for i in self.slot:
            tree += self.slot[i].dump(depth+1,prefix='%s = '%i)
        for j in self.nest:
            tree += j.dump(depth+1)
        return tree
    def pad(self,N):
        return '\n' + '\t' * N
    def head(self,prefix=''):
        return '%s<%s:%s> @%x' % (prefix, self.type, self.str(), id(self))
    def str(self):
        return self.val

    ## manipulations
    
    def __getitem__(self,key):
        return self.slot[key]
    def __setitem__(self,key,obj):
        self.slot[key] = obj ; return self
    def __floordiv__(self,obj):
        self.nest.append(obj)
    def __lshift__(self,obj):
        self[obj.val] = obj ; return self
        
    ## stack ops
    
    def top(self):
        return self.nest[-1]
    def pop(self):
        return self.nest.pop()
    def dropall(self):
        self.nest = []
    
    ## execution & code generation
    
    def execute(self):
        S // self
        
    
#################################################################### primitive

class Primitive(Frame): pass
        
class String(Primitive): pass

class Symbol(Primitive): pass

class Number(Primitive): pass

class Integer(Number):
    def toint(self):
        return self

class Hex(Integer):
    def str(self):
        return '%X' % self.val
    def toint(self):
        return Integer(self.val)

#################################################################### container
        
class Container(Frame): pass

class Stack(Container): pass

class Dict(Container):
    def __lshift__(self,F):
        if callable(F): return self << Cmd(F)
        else: return Frame.__lshift__(self, F)
        
class Vector(Container): pass        

####################################################################### active

class Active(Frame): pass

class Cmd(Active):
    def __init__(self,F,I=False):
        Frame.__init__(self, F.__name__)
        self.fn = F
        self.immed = I
    def execute(self):
        self.fn()

############################################################## metaprogramming

class Meta(Frame): pass

class Module(Meta): pass

class File(Meta): pass

######################################################## virtual FORTH machine

S = Stack('DATA')

W = Dict('FORTH')

W['W'] = W
W['S'] = S

######################################################################## stack

def DROPALL(): S.dropall()
W['.'] = Cmd(DROPALL)

################################################################ manipulations

def ST(): B = S.pop() ; W[B.val] = S.pop()
W['!'] = Cmd(ST)

def pST(): C = S.pop() ; B = S.pop() ; A = S.pop() ; C[B.val] = A
W['.!'] = Cmd(pST)

def LSHIFT(): B = S.pop() ; S.top() << B
W['<<'] = Cmd(LSHIFT)

################################################################### conversion

def toINT(): S // S.pop().toint()
W['>INT'] = Cmd(toINT)

######################################################################## debug

def BYE(): sys.exit(0)
W << BYE

def Q(): print S
W['?'] = Cmd(Q,I=True)

def QQ(): print W ; BYE()
W['??'] = Cmd(QQ,I=True)

############################################################## metaprogramming

def META(): S // Meta(S.pop().val)
W << META

def MODULE(): S // Module(S.pop().val)
W << MODULE

def FILE(): S // File(S.pop().val)
W << FILE

############################################################ PLY powered lexer

import ply.lex as lex

tokens = ['symbol','string','hex','integer']

t_ignore = ' \t\r\n'

def t_comment(t):
    r'[\#\\].*\n'
    pass

states = (('str','exclusive'),)
t_str_ignore = ''

def t_string(t):
    r'\''
    t.lexer.lexstring=''
    t.lexer.push_state('str')
def t_str_string(t):
    r'\''
    t.lexer.pop_state()
    return String(t.lexer.lexstring)
def t_str_char(t):
    r'.'
    t.lexer.lexstring += t.value

def t_hex(t):
    r'0x[0-9a-fA-F]+'
    return Hex(int(t.value[2:],0x10))

def t_integer(t):
    r'[\+\-]?[0-9]+'
    return Integer(int(t.value))

def t_symbol(t):
    r'[`]|[^ \t\r\n]+'
    return Symbol(t.value)

def t_ANY_error(t): raise SyntaxError(t)

lexer = lex.lex()

################################################################## interpreter

def QUOTE():
    WORD()
W['`'] = Cmd(QUOTE,I=True)

def WORD():
    token = lexer.token()
    if not token: return False
    S // token  ; return True
    
def FIND():
    token = S.pop()
    try: S // W[token.val]
    except KeyError:
        try: S // W[token.val.upper()]
        except KeyError:
            raise SyntaxError(token)
        
def EXECUTE():
    S.pop().execute()
        
def INTERPRET():
    lexer.input(S.pop().val)
    while True:
        if not WORD(): break
        if isinstance(S.top(), Symbol):
            FIND()
        EXECUTE()
        
def REPL():
    while True:
        print S
        try:
            print '\n' + '-'*40
            S // String(raw_input('fly> '))
            INTERPRET()
        except EOFError:
            print '\n' + '='*40
            break
            
W << REPL        

################################################################## system init

def INIT():
    infiles = sys.argv[1:] ; print infiles
    if not infiles:
        S // String(open('fly.fly').read()) ; INTERPRET()
        REPL()
    else:    
        for i in infiles:
            S // String(open(i).read()) ; INTERPRET()
INIT()

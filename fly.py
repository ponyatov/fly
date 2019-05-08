import os,sys ; print sys.argv

################################################################## frame system

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
        return '%s<%s:%s> @%x' % (prefix, self.type, self.val, id(self))

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
        
    
##################################################################### primitive
        
class String(Frame): pass

class Symbol(Frame): pass

##################################################################### container
        
class Stack(Frame): pass

class Dict(Frame):
    def __lshift__(self,F):
        if callable(F): return self << Cmd(F)
        else: return Frame.__lshift__(self, F)

######################################################################## active

class Cmd(Frame):
    def __init__(self,F,I=False):
        Frame.__init__(self, F.__name__)
        self.fn = F
        self.immed = I
    def execute(self):
        self.fn()
        
############################################################### metaprogramming

class Meta(Frame): pass

class Module(Meta): pass

class File(Meta): pass

######################################################### virtual FORTH machine

S = Stack('DATA')

W = Dict('FORTH')

W['W'] = W
W['S'] = S

################################################################# manipulations

def ST(): B = S.pop() ; W[B.val] = S.pop()
W['!'] = Cmd(ST)

def pST():
    C = S.pop() ; B = S.pop() ; A = S.pop() ; C[B.val] = A
W['.!'] = Cmd(pST)

def LSHIFT(): B = S.pop() ; S.top() << B
W['<<'] = Cmd(LSHIFT)

######################################################################### stack

def DROPALL(): S.dropall()
W['.'] = Cmd(DROPALL)

######################################################################### debug

def BYE(): sys.exit(0)
W << BYE

def Q(): print S
W['?'] = Cmd(Q,I=True)

def QQ(): print W ; BYE()
W['??'] = Cmd(QQ,I=True)

############################################################### metaprogramming

def META(): S // Meta(S.pop().val)
W << META

def MODULE(): S // Module(S.pop().val)
W << MODULE

def FILE(): S // File(S.pop().val)
W << FILE

############################################################# PLY powered lexer

import ply.lex as lex

tokens = ['symbol','string']

t_ignore = ' \t\r\n'

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

def t_comment(t):
    r'[\#\\].*\n'
    pass
def t_symbol(t):
    r'[`]|[^ \t\r\n]+'
    return Symbol(t.value)

def t_ANY_error(t): raise SyntaxError(t)

lexer = lex.lex()

################################################################### interpreter

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
            S // String(raw_input('ok> '))
            INTERPRET()
        except EOFError:
            print '\n' + '-'*40
            break
            
W << REPL        
        
################################################################### system init

infiles = sys.argv[1:] ; print infiles
if not infiles:
    S // String(open('fly.fly').read()) ; INTERPRET()
    REPL()
else:    
    for i in infiles:
        S // String(open(i).read()) ; INTERPRET()

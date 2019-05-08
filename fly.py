import os,sys ; print sys.argv

class Frame:
    def __init__(self,V):
        self.type = self.__class__.__name__.lower()
        self.val  = V
        self.slot = {}
        self.nest = []
    def __setitem__(self,key,obj):
        self.slot[key] = obj ; return self
    def __floordiv__(self,obj):
        self.nest.append(obj)
    def __repr__(self):
        return self.dump()
    def dump(self,depth=0,prefix=''):
        tree = self.pad(depth) + self.head(prefix)
        for i in self.slot:
            tree += self.slot[i].dump(depth+1,prefix='%s = '%i)
        for j in self.nest:
            tree += j.dump(depth+1)
        return tree
    def pad(self,N):
        return '\n' + '\t' * N
    def head(self,prefix=''):
        return '%s<%s:%s> @%x' % (prefix, self.type, self.val, id(self)) 
        
class String(Frame): pass
        
class Stack(Frame): pass

S = Stack('DATA')

class Voc(Frame): pass

W = Voc('VOC')

# W['W'] = W
W['S'] = S

def INTERPRET():
    print W

infiles = sys.argv[1:] ; print infiles
if not infiles: infiles += ['fly.fly']
for i in infiles:
    S // String(i) ; INTERPRET()
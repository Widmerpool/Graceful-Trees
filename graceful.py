import math
import numpy as np
import re
import networkx as nx
import pylab
limits=pylab.axis('off')
import matplotlib.pyplot as plt
import time
import random
from docx import Document
from docx.shared import Inches
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
from docx.enum.style import WD_STYLE_TYPE
import warnings
import matplotlib.cbook
import collections
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

class Tree:
    def __init__(self,ident,size=0):
        self.ident=ident
        self.size=max(scale(ident),size)
        self.fcode=fcode(ident,size)
        self.edges=tcode(ident,size)
        self.adjlist=adjlist(self.edges)
        self.signature=signature(self.edges)
        self.levels=levels(self.signature)
        self.trunk=trunk(self.edges)
        self.centre=centre(self.edges)
        self.diameter=len(self.trunk)
        self.connected=is_connected(self.edges)
        self.certificate=certificate(self.edges)
        self.prufer = tree_to_prufer(self.edges)

    def display(self):
        graph=tcode(self.ident,self.size)
        G = nx.Graph()
        for q in graph:
            G.add_edge(q[0],q[1])
        pos = nx.fruchterman_reingold_layout(G)
        nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'),node_size = 1000)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)
        plt.show()

    def flip(self):
        return Tree(converse(self.ident,self.size),self.size)

    def bud(self):
        i=dcode(self.fcode+[0])
        s=self.size+1
        return Tree(i,s)

class Stock:
    def __init__(self,ident,size=0):
        self.ident=ident
        self.size=max(scale(ident),size)
        self.fcode=fcode(ident,size)
        self.edges=gcode(ident,size)
        self.adjlist=adjlist(self.edges)
        self.signature=signature(self.edges)
        self.levels=levels(self.signature)
        self.trunk=trunk(self.edges)
        self.centre=centre(self.edges)
        self.diameter=diameter(self.edges)
        self.connected=is_connected(self.edges)
        self.certificate=certificate(self.edges)
        self.mutation=mutation(self.edges)
        self.prufer = tree_to_prufer(self.edges)

    def display(self):
        graph=gcode(self.ident,self.size)
        G = nx.Graph()
        for q in graph:
            G.add_edge(q[0],q[1])
        pos = nx.fruchterman_reingold_layout(G)
        nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'),node_size = 1000)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)
        plt.show()

    def flip(self):
        return Stock(converse(self.ident,self.size),self.size)

    def bud(self):
        i=dcode(self.fcode+[0])
        s=self.size+1
        return Stock(i,s)

#===================================================================

def adjlist(tree):
    'Takes a list of edges - as pairs of vertices, such as object.edges - and returns the list of adjacencies. '
    'So the kth entry is a list of all the vertices adjacent to vertex k.'
    s=len(tree)+1
    a=[]
    for i in range(0,s):
        a.append([])
    for edge in tree:
        a[edge[0]].append(edge[1])
        a[edge[1]].append(edge[0])
    return a

def scale(ident):
    'Outputs the largest number whose factorial is less than the input'
    n=ident+1
    s=0
    while n > math.factorial(s):
        s+=1
    return s-1

def fcode(ident,size=0):
    'Takes a number, and the number of entries, and returns the Cantor representation '
    size=max(scale(ident),size)
    f=[]
    m=0
    while math.factorial(m)<=ident:
        f.insert(0,(ident%math.factorial(m+1))//math.factorial(m))
        m+=1
    return [0]*max(size-len(f),0)+f

def dcode(fb):
    'Takes in a Cantor representation of a number, and outputs the decimal '
    'form of the number.'
    size=len(fb)
    db=0
    s=0
    s+=size-1
    f=math.factorial(s)
    while s != 0:
        a=fb.pop(0)
        db+=a*f
        f=f//s
        s=s-1
    return db

def converse(ident,size=0):
    size=max(scale(ident),size)
    return math.factorial(size)-1-ident

def tree_to_prufer(g):
    'takes a graceful graph (as a list of edges, i.e. vertex pairs) and returns its Prüfer code'
    size = len(g)
    if not is_connected(g):
        return None
    a = adjlist(g)
    pru = []
    while len(pru) != size - 1:
        for i in range(size):
            if len(a[i]) == 1:
                c = a[i][0]
                pru.append(c)
                a[i] = []
                for thing in a:
                    if i in thing:
                        thing.remove(i)
                break
    return pru

def prufer_ident(pru):
    'takes a graceful Prüfer code and returns the Cantor ident of the tree'
    if pru == None:
        return None
    size = len(pru)+2
    p = [thing for thing in pru]
    e = []
    r = {i for i in range(len(p)+2)}
    rs = r - set(p)
    while p != []:
        rs = r - set(p)
        s = p.pop(0)
        t = min(rs)
        r.remove(t)
        e.append((max(s,t) - min(s,t),min(s,t)))
    e.append(tuple(r - set(p)))
    e.sort()
    print(p,e,rs,sep = '\t')
    return dcode([thing[1] for thing in e] + [0])

def gcode(ident,size=0):
    'Takes the ident of a Stock and uses its Cantor representation to produce '
    'a list of edges (in the form of pairs of vertices). Guaranteed to be '
    'graceful, but may not be acyclic'
    fb=fcode(ident,size)
    G=[]
    for i in range(0,len(fb)):
        G.append((fb[i],fb[i]+i+1))
    return G

def tcode(ident,size=0):
    'Takes the ident of a Tree and uses its Cantor representation to produce a '
    'list of edges (in the form of pairs of vertices). Guaranteed to be acyclic '
    'but (except for ident = 0 or ident = size!, which yield stars) not graceful'
    size=max(scale(ident),size)
    f=fcode(ident,size)
    t=[(f[i],size+1-i) for i in range(size + 1)]
    return t
                
def degree_list(graph):
    'A list of the degrees of all the vertices, ordered by label'
    d=[]
    alist=adjlist(graph)
    for i in range(0,len(alist)):
        d.append(len(alist[i]))
    return d

def centre(graph):
    if not is_connected(graph):
        return None
    "If the graph isn't connected, return None. Otherwise..."
    'Outputs a pair of vertex labels; two different labels if they are the '
    'bicentre, or the same label twice for the single centre'
    L=trunk(graph)
    r=int(math.floor((len(L)-1)/2))
    s=int(math.ceil(len(L)-r-1))
    return [L[r],L[s]]

def _root_(alist,node):
    'Recursively converts the adjacency list of an undirected unrooted tree '
    'into the adjacency list of a directed tree rooted at "node" '
    fork=alist[node]
    for tine in fork:
        if node in alist[tine]:
            alist[tine].remove(node)
            _root_(alist,tine)
    return alist

def root(graph,node=0):
    'A wrapper for the "_root_" function, taking a tree, and a node to be the '
    'root; and outputting the adjacency list of the directed rooted version of '
    'the tree'
    rootlist = _root_(adjlist(graph),node)
    return rootlist
       
def signature(graph):
    'Converts the hierarchic list version of the certificate to flat form'
    c=certificate(graph)
    if c==None:
        return None
    a = re.sub('\ |\[|\]','',str(c))
    s=[]
    while a!= "":
        n = a.find(',')
        if n==-1:
            s.append(int(a))
            a=""
        else:
            s.append(int(a[:n]))
            a=a[n+1:]
    return s

def _mark_(depth,rootlist,scores,node):
    'We recursively mark vertices with their distance from a starting vertex '
    '("node"), for a given starting distance ("depth") based on the adjacency '
    'list of a rooted tree ("rootlist"), updating the distance list ("scores") '
    'and returning the updated list'
    scores[node]=depth
    depth += 1
    for item in rootlist[node]:
        _mark_(depth,rootlist,scores,item)
    return scores

def mark(tree,node):
    'A wrapper for the "_mark_" function, starting from a given vertex on a '
    'given tree, and calculating the other values to pass down the recursion'
    path=[0]
    for edge in tree:
        path.append(0)
    return _mark_(0,root(tree,node),path,node)
    
def trunk(tree):
    if not is_connected(tree):
        return None
    "If the graph isn't connected, return None. Otherwise..."
    'We start from vertex zero, recursively labelling each vertex with its '
    'distance from zero. We then repeat it, this time starting from the '
    'vertex with the largest label. Finally we retrace our steps, and add '
    'together the last two arrays of labels. The trunk is the set of vertices '
    'with the minimum label value. We start from the last vertex visited and '
    'traverse the path, noting them in order. This ordered list is the trunk'
#  Set up the starting values - a list of vertex depth labels
# (all initialised at zero) and the starting node (we start at zero because,
#  why not?
    path=[0]
    node=0
    for edge in tree:
        path.append(0)
#  Pass twice through the rooted tree - first to find a vertex as far from
#  the start as possible, and the second time to find a vertex as far from
#  that one as possible. 
    for a in (1,2):
        scores = mark(tree,node)
        node = scores.index(max(scores))
#  Now we retrace the path
    rescores = mark(tree,node)
    node = scores.index(max(scores))
#  Finally we add together the distance markers from traversing the tree
#  in both directions, to get the combined distance
    for i in range(0,len(scores)):
        rescores[i] += scores[i]
#  We finish now by logging which vertices ("knots") have the minimum combined
#  distance...
    knots=[]
    m=min(rescores)
    for i in range(0,len(rescores)):
        if rescores[i] == m:
            knots.append(i)
#  ...and then following the trail of knots through the unrooted tree
    trail=[node]
    alist=root(tree,node)
    done=False
    while done == False:
        ready=True
        for knot in alist[trail[-1]]:
            if knot in knots:
                trail.append(knot)
                ready=False
        done=ready
    return trail

def diameter(graph):
    if not is_connected(graph):
        return None
    return len(trunk(graph))

def noble(seed,size=0):
    'Takes an input ("seed") and generates a graceful acyclic tree that could be '
    'built by budding and flipping from an initial single edge '
    c=seed
    s=0
    while c > 0:
        c=c//2
        s+=1
    size=max(s,size)
    b=[]
    for j in range(0,size):
        b.insert(0,seed%2)
        seed=seed//2
    f=[0]
    while b!=[]:
        f.insert(0,b.pop()+f[0])
    return Stock(dcode(f),len(f))

def certificate(graph):
    'Generates the Valiente certificate, in its full list form. If the graph is '
    'not a connected tree, returns "None". '
    size=len(graph)
    if is_connected(graph):
        c=centre(graph)
        a=adjlist(graph)
        w=[label(c[0],root(graph,c[0])),label(c[-1],root(graph,c[-1]))]
        w.sort()
        return w[1]
    return None    
    
def label(node,rootlist):
    'Creates labels used in making the Valiente certificate'
    N=rootlist[node]
    if N==[]:
        return [0]
    L=[len(N)]
    B=[]
    for item in N:
        B.append(label(item,rootlist))
    L=L+sorted(B,reverse=True)
    return L

def residue(graph):
    'Takes a graph and returns a list of the unconnected vertices (if any) '
    size=len(graph)
    alist=adjlist(graph)
    itinerary=list(range(1,size+1))
    scheduled=[0]
    while scheduled != []:
        s=scheduled.pop(0)
        for item in alist[s]:
            if item in itinerary:
                scheduled.append(item)
                itinerary.remove(item)
    return itinerary

# takes an index number and the number of edges, and says whether the graph is a tree
def is_connected(graph):
    'Outputs True if the graph is connected (=acyclic, tree), otherwise false '
    size=len(graph)
    alist=adjlist(graph)
    itinerary=list(range(1,size+1))
    scheduled=[0]
    while scheduled != []:
        s=scheduled.pop(0)
        for item in alist[s]:
            if item in itinerary:
                scheduled.append(item)
                itinerary.remove(item)
    if itinerary==[]:
        return True
    return False

# make a deck of (atomic) switches for an n- tree
def make(n):
	deck=[]
	for i in range(1,n):
		for j in range(1,1+n-i):
			deck.append((i,j))
	return deck

# lists all graceful trees of size n and their certificates
def Stock_catalogue(n):
    'Outputs a list of all graceful trees of size n and their signatures '
    if n==0:
        return [[0],[0]]
    cat=[[],[]]
    for ident in range(0,math.factorial(n),2):
        g=gcode(ident,n)
        if is_connected(g):
            graph=Stock(ident,n)
            v=graph.signature
            if v in cat[0]:
                p=cat[0].index(v)
                cat[1][p].append(ident)
            else:
                cat[0].append(v)
                cat[1].append([ident])
    return cat

def Stock_book(n):
    cat=Stock_catalogue(n)
    bk={}
    for sig in cat[0]:
        j=cat[0].index(sig)
        print(j,sig,cat[1][j],sep='\t')
        'bk[sig] = tuple(cat[1][j])'
    'return bk'

def tree_catalogue(n):
    'Outputs a list of all graceful trees of size n and their signatures '
    if n==0:
        return [[0],[0]]
    cat=[[],[[]]]
    for ident in range(0,math.factorial(n),2):
        v=Tree(ident,n).signature
        if v in cat[0]:
            p=cat[0].index(v)
            cat[1][p].append(ident)
        else:
            cat[0].append(v)
            cat[1].append([ident])
    return cat

def tree_book(n):
    cat=tree_catalogue(n)
    bk={}
    for sig in cat[0]:
        bk[sig] = cat[1][cat[0].index(sig)]
    return bk

def isometric(T1,T2):
    return T1.signature == T2.signature

def adjacency(graph): #gives back a printout of the adjacency matrix
    adj=""
    print(" " + str(0),end=' ')
    for i in range(1,len(graph)+1):
        adj+="\n|"
        for j in range(0,i):
            if (j,i) in graph:
                adj +=" • |"
            else:
                adj +="   |"
        adj += " " + str(i)
    print(adj)

def show_cat(n):
    cat=catalogue(n)
    print(len(cat[0]),'trees')
    for i in range(0,len(cat[0])):
        print(i,len(cat[1][i]),sep='\t')

def exemplars(n):
    cat=tree_catalogue(n)
    w=len(cat[0])
    for i in range(0,w):
        print(n,i,cat[0][i],sep='\t')
        #Stock(cat[1][i][0],n).display()

def pathsig(m):
    if m == 0:
        return [1]
    elif m == 1:
        return [1,0]
    elif m == 2:
        return [2,0,0]
    elif m == 3:
        return [2,1,0,0]
    else:
        p = m%2
        n = m-1
        q = pathsig(n)
        if p == 1:
            q.insert(1,1)
            return q
        else:
            q.insert(-1,1)
    return q

def deep(alist,i):
    if alist[i] == []:
        return 0
    return min([1 + deep(alist,item) for item in alist[i]])

def zero_depth(graph):
    alist = root(graph)
    return deep(alist,0)

def pathlist(m,parity = 0):
    if parity == 0:
        p = 2
    else:
        p = 1
    paths=[]
    maxdepth = m//2 + m%2
    sig = pathsig(m)
    for r in range(0,math.factorial(m),p):
        S = Stock(r,m)
        if S.connected:
            if S.signature == sig:
                zd = zero_depth(S.edges)
                T = S.flip()
                md =  zero_depth(T.edges)
                d,e = (min(zd,m-zd),min(md,m-md))
                paths.append((r,S.mutation,S.fcode,S.trunk,d,e))
    return paths

def path_catalogue(m,parity = 0):
    'generates a list of all paths of length m'
    print("======================\n",m,end = '\t')
    t = time.time()
    p = pathlist(m,parity)
    t = int((time.time() - t)*1000+.5)/1000
    duration =  time.strftime('%H:%M:%S', time.localtime(t+0.5))
    print(str(len(p)) + " paths:\t","t =" + duration ,"\t("+str(t)+"sec)","\n======================")
    for thing in p:
        for item in thing:
            print(item,end='\t')
        print("")

'=================================================================='
'   MUTATIONS'
'=================================================================='

            
def mutation(graph):
    'takes a set of edges and returns the mutation that will generate them.'
    if not is_connected(graph):
        return None

    m=len(graph)
    n=m//2
    mu=[]
    um=[]
    mdict={}
    r = root(graph,0)
    for thing in r:
        for item in thing:
            for target in r[item]:
                mdict[target]=item-target
                um.append((target,item-target))
    um.sort()
    while um != []:
        p=um.pop(0)
        qu=[p[0],p[1]]
        while qu[0] != qu[-1]:
            try:
                i=um.index((qu[-1],mdict[qu[-1]]))
            except KeyError:
                return [(0)]
            p=um[i]
            if p[1]<0:
                qu[-1]*=-1
                qu.append(-p[1])
            else:
                qu.append(p[1])
            um.pop(i)
        mu.append(tuple(qu))
        qu=[]
    return mu

def example(m):
    'creates a random graceful tree with m edges'
    n=int(random.random()*math.factorial(m)/2)*2
    while not is_connected(gcode(n,m)):
        n=int(random.random()*math.factorial(m))
    return Stock(n,m)

def cyclic(m,parity=0):
    'lists all valid cyclic mutations on n vertices (parity is 0 if only even idents are wanted, 1 otherwise)'
    cat=[[],[]]
    top=m//2
    done=False
    i=1
    for v in range(1,top+1):
        cat[i].append([v,v])
    while not done:
        i+=1
        cat.append([])
        for element in cat[i-1]:
            for v in range(upper(element)+1,m-1+parity):
                for slot in range(0,i-1):
                    if element[slot] >0 and abs(v+element[slot]) <= m:
                        if v+abs(element[slot+1]) <= m:
                            c=element[:slot+1]+[v]+element[slot+1:]
                            if c not in cat[i]:
                                cat[i].append(c)
                        if v>abs(element[slot+1]):
                            c=element[:slot+1]+[-v]+element[slot+1:]
                            if c not in cat[i]:
                                cat[i].append(c)
        if cat[-1]==[]:
            done=True
    return cat

def upper(element):
    return max(max(element),-min(element))

def topper(mutation):
    t=0
    for element in mutation:
        w=len(element)-1
        for item in element[:w]:
            i=element.index(item)
            t=max(item+abs(element[i+1]),t)
    return t

def cantor(mutation,size=0):
    'returns the Cantor representation of the result of a mutation'
    size=max(size,topper(mutation))
    c=[0 for x in range(0,size)]
    for component in mutation:
        m=len(component)
        for i in range(1,m):
            a=component[i-1]
            b=component[i]
            if a < 0:
                c[abs(b)-1]=-(a+abs(b))
            else:
                c[abs(b)-1]=a
    return c

def orthogonal(cantor1,cantor2):
    'tests whether two mutations affect disjoint subsets of vertices'
    if len(cantor1) !=len(cantor2): return None
    return sum(i[0]*i[1] for i in zip(cantor1,cantor2))==0

def merge(mut1,mut2,size=0):
    'adds two orthogonal mutations'
    c1=cantor(mut1,size)
    c2=cantor(mut2,size)
    d=len(c1)-len(c2)
    while len(c1) > len(c2):
        c2 = [0]+c2
    while len(c2) > len(c1):
        c1 = [0]+c1
    print(c1)
    print(c2)
    if orthogonal(c1,c2):
        return list(i[0]+i[1] for i in zip(c1,c2))

def independent(item1,item2):
    for component in item1:
        for element in component:
            for target in item2:
                if element in target or -element in target:
                    return False
    return True
    
def _mutations_(n,parity):
    mu=[[(0,0)]]
    cy=cyclic(n,parity)
    for level in cy:
        for thing in level:
            mu.append([tuple(thing)])
    return mu

def _compose_(mu):
    checker=[]
    multi=[]
    for thing in mu[1:]:
        i=mu.index(thing)
        for other in mu[i+1:]:
            if independent(thing,other):
                it=thing+other
                it.sort()
                cant=dcode(cantor(it))
                if it not in mu:
                    mu.append(it)
                    checker.append(cant)
                    if checker.count(cant)>1 and cant not in multi:
                        multi.append(cant)
    redo=True
    while redo:
        redo=False
        for thing in mu[1:]:
            if cantor(thing) in multi:
                redo=True
                mu.remove(thing)        
    return mu

def mutations(m,parity=0):
    'generates a complete set of all mutations and all compositions of mutations. parity is 0 if only even idents are wanted, 1 otherwise'
    return _compose_(_mutations_(m,parity))

def mutations_catalogue(m,parity=0):
    'generates a catalogue of all mutations on m edges'
    M=mutations(m,parity)
    cat=[]
    for thing in M:
        c=cantor(thing,m)
        d=dcode(c)
        s=signature(gcode(d,m))
        cat.append((d,s,thing,c))
    cat.sort()
    return cat

def x(mu1,mu2,size=0):
    s=0
    for mu in (mu1,mu2):
        for thing in mu:
            s=max(s,max(thing),-min(thing))
    size=max(size,s*2)
    c=cantor(mu2,size)
    c2=c[:]
    for part in mu1:
        w=len(part)-1
        for p in range(0,w):
            c2[part[p+1]]=c[part[p]]
    d=dcode(c2)
    g=gcode(d,size)
    print(d,g)
    mu=mutation(g)
    return mu

def list_mutations(m,parity=0):
    'prints signature, cantor representation, ident, and mutation of all mutable trees on m edges'
    C=mutations_catalogue(m,parity)
    widths=[0,0,0,0]
    for row in C:
        for i in range(0,3):
            widths[i]=max(widths[i],len(str(row[i]))+2)
    print('ID',' '*(widths[0]-3),'MUTATION',' '*(widths[1]-9),'CANTOR',' '*(widths[2]-7),'SIGNATURE')
    for row in C:
        for i in range(0,4):
            print(row[i],' '*(widths[i]-len(str(row[i]))),end='')
        print('')
        

def list_exceptions(m,parity=0):
    C=mutations_catalogue(m,parity)
    widths=[0,0,0,0]
    for row in C:
        for i in range(0,3):
            widths[i]=max(widths[i],len(str(row[i]))+2)
    print('\t','ID',' '*(widths[0]-3),'SIGNATUR ',' '*(widths[1]-9),'MUTATIONS',' '*(widths[2]-7),'SIGNATURE')
    s=0
    for row in C:
        if row[1]==None:
            s+=1
            print(s,end='\t')
            for i in range(0,4):
                print(row[i],' '*(widths[i]-len(str(row[i]))),end='')
            print('')

def list_clean(m,parity=0):
    C=mutations_catalogue(m,parity)
    widths=[0,0,0,0]
    for row in C:
        for i in range(0,3):
            widths[i]=max(widths[i],len(str(row[i]))+2)
    print('ID',' '*(widths[0]-3),'MUTATION',' '*(widths[1]-9),'CANTOR',' '*(widths[2]-7),'CANTOR')
    for row in C:
        if row[1]!=None:
            for i in range(0,4):
                print(row[i],' '*(widths[i]-len(str(row[i]))),end='')
            print('')

def test_mutation(mutation):
    check=[]
    burn=[]
    for sub in mutation:
        for i in range(0,len(sub)-1):
            if sub[i]<0:
                a=abs(sub[i])
            else:
                a=sub[i]+abs(sub[i+1])
            check.append(a)
            burn.append(a)
    while burn != []:
        if burn.pop() in burn:
            return (check,False)
    return (check,True)
          
def comp(q):
    for m in range(3,q+1):
        n=trees(m)
        t=len(mutations_catalogue(m))
        print(m,"Trees:",n,"Mutations:",t,"Wronguns:",t-n,sep='\t')
    
def mutation_signatures(m,parity=0):
    mu=mutations(m,parity)
    ms=[]
    for tree in mu:
        ident=dcode(cantor(tree,m))
        ts=signature(gcode(ident,m))
        if ts not in ms:
            ms.append(ts)
    return sorted(ms,reverse=True)

def treecount(n):
    'The OEIS 000055 list of numbers of distinct trees with n vertices - redone '
    'so as to correspond to the number of edges, not vertices '
    if n > 35:
        return None
    num=[1, 1, 1, 2, 3, 6, 11, 23, 47, 106, 235, 551, 1301, 3159, 7741, 19320, 48629, 123867, 317955, 823065, 2144505, 5623756, 14828074, 39299897, 104636890, 279793450, 751065460, 2023443032, 5469566585, 14830871802, 40330829030, 109972410221, 300628862480, 823779631721, 2262366343746, 6226306037178]
    return num[n]

def trees(n,parity=0):
    'a rough and ready count of how many gcodes produce connected trees, by number of edges.'
    num=[1,1,1,2,6,20,82,376,2010,11788,77816,556016]
    if n < 12:
        return num[n]*(1+parity)
    return trees(n-1,parity)*(0.6424*n + 0.1431)

def wrong_mutations(m):
    C=mutations(m)
    return len(C)-trees(m)//2

def partitions(n,k=-1):
    'counts the number of partitions of n if the largest partition is k'
    if k==-1:
        p=1
        for m in range(1,n):
            q=partitions(n,m)
            p+=q
        return p
    if n == 0 and k == 0:
        return 1
    if n < 1 or k < 1:
        return 0
    return partitions(n-k,k)+partitions(n-1,k-1)

def perm(n,objects):
    'takes a list of objects and returns the nth permutation'
    size=len(objects)
    permutator=fcode(n,size)
    if len(permutator) > size:
        return 'Permutator larger than list'
    output = []
    while objects != []:
        p=permutator.pop(0)
        q=objects.pop(p)
        output.append(q)
    return output

def sampling(size,sample=1000000):
    'takes a random sample of stocks of given size to test how many are connected'
    m=math.factorial(size)
    count=0
    found=0
    t=time.time()
    x=0
    while found < 30 and count < 3*m:
        ident=int(random.random()*m)
        count+=1
        if is_connected(gcode(ident,size)):
            found+=1
            print(found,count,int(m*found/count+.5),sep='\t')
        r=found/count
        q=int(m*found/count)
    print(time.time()-t,size,treecount(size),trees(size),q,found,count,sep='\t')

def signat(lay):
    'takes the integer layout of a rooted tree and returns the valiente signature of the tree'
    sig=[]
    size=len(lay)
    for i in range(0,size-1):
        r=lay[i]
        c=0
        j=i+1
        while j<len(lay) and lay[j] > r:
            if lay[j]==r+1:c+=1
            j+=1
        sig.append(c)
    return sig+[0]

def levels(signature):
    'takes a tree signature and returns the levels list'
    p=0
    S=signature
    if S==None:
        return None
    size=len(S)
    L=[0]
    w=[S[p]]
    while w!=[] and len(L)<size:
        q=len(w)-1
        p+=1
        s=S[p]
        w[q]+=-1
        w.append(s)
        q+=1
        L.append(q)
        while w != [] and w[len(w)-1] == 0:
            k=w.pop()
    return L

def rooted_successor(lay):
    'takes the integer layout of a rooted tree and returns the next tree'
    n=len(lay)
    j=-1
    while lay[j] == 1:
        j=j-1
    p=n+j
    while lay[j] != lay[p]-1:
        j=j-1
    q=n+j
    successor=lay[:p]
    d=p-q
    for i in range(p,n):
        successor.append(successor[i-d])
    return successor

def rooted_count(m):
    'returns the number of unlabelled rooted trees of size m up to isomorphism'
    lay=list(range(0,m+1))
    n=1
    while lay != [0]+[1]*m:
##        print(n,lay,signat(lay),sep='\t')
        n+=1
        lay=rooted_successor(lay)
##    print(n,lay,signat(lay),sep='\t')
    return n

def k_mutations(n):
    f=[0]
    for j in range(0,n+1):
        f.append(0)
    h=f[:]
    C=mutations_catalogue(n,0)
    for thing in C:
        if len(thing[1])==1:
            h[len(thing[1][0])] += 1
    print('\n',j,") : ",'\t',end='\t')
    for item in h:
        print(item,end='\t')
    C=mutations_catalogue(n,1)
    for thing in C:
        if len(thing[1])==1:
            h[len(thing[1][0])] += 1
    print(" : ",'\t',end='\t')
    for item in h:
        print(item,end='\t')

def interleaf(mutation):
    inter=[]
    for perm in mutation:
        temp=[]
        for a in range(0,len(perm)-1):
            temp.append(perm[a]+perm[a+1])
        inter.append(tuple(temp))
    return(inter)

import math
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
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

class Tree:
    def __init__(self,ident,size=0):
        self.ident=ident
        self.size=max(scale(ident),size)
        self.fcode=fcode(ident,size)
        self.edges=tcode(ident,size)
        self.adjlist=adjlist(self.edges)
        self.signature=signature(self.edges)
        self.trunk=trunk(self.edges)
        self.centre=centre(self.edges)
        self.diameter=len(self.trunk)
        self.connected=is_connected(self.edges)
        self.certificate=certificate(self.edges)

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
        i=math.factorial(self.size)-1-self.ident
        return Tree(i,self.size)

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
        self.trunk=trunk(self.edges)
        self.centre=centre(self.edges)
        self.diameter=diameter(self.edges)
        self.connected=is_connected(self.edges)
        self.certificate=certificate(self.edges)

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
        i=math.factorial(self.size)-1-self.ident
        return Stock(i,self.size)

    def bud(self):
        i=dcode(self.fcode+[0])
        s=self.size+1
        return Stock(i,s)

#===================================================================

def adjlist(tree):
    'Takes a list of edges - as pairs of vertices - and returns the list of '
    'adjacencies. So the kth entry is a list of all the vertices adjacent to '
    'vertex k.'
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
    'Takes a number, and the number of entries, and returns the Cantor '
    'representation '
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

def gcode(ident,size=0):
    'Takes the ident of a shrub and uses its Cantor representation to produce '
    'a list of edges (in the form of pairs of vertices). Guaranteed to be '
    'graceful, but may not be acyclic'
    fb=fcode(ident,size)
    G=[]
    for i in range(0,len(fb)):
        G.append((fb[i],fb[i]+i+1))
    return G

def tcode(ident,size=0):
    'Takes the ident of a tree and uses its Cantor representation to produce a '
    'list of edges (in the form of pairs of vertices). Guaranteed to be acyclic '
    'but (except for ident = 0, which yields a star) not graceful'
    size=max(scale(ident),size)
    f=fcode(ident,size)
    t=[]
    for i in range(0,size):
        t.append((f[i],size-i))
    return t
                
def degree_list(graph):
    'A list of the degrees of all the vertices'
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
    'Recursively turns the adjacency list of an undirected unrooted tree '
    'into the adjacency list of a directed tree rooted at "node" '
    fork=alist[node]
    for tine in fork:
        if node in alist[tine]:
            alist[tine].remove(node)
            _root_(alist,tine)
    return alist

def root(tree,node):
    'A wrapper for the "_root_" function, taking a tree, and a node to be the '
    'root; and outputting the adjacency list of the directed rooted version of '
    'the tree'
    rootlist = _root_(adjlist(tree),node)
    return rootlist
       
def signature(graph):
    'Converts the list version of the certificate to string form'
    a = re.sub('\ |\[|\]','',str(certificate(graph)))
    return re.sub('\,','-',a)

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
        w=[label(c[0],root(graph,c[0])),label(c[1],root(graph,c[1]))]
        return sorted(w)[1]
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
def shrub_catalogue(n):
    'Outputs a list of all graceful trees of size n and their signatures '
    if n==0:
        return [[0],[0]]
    cat=[[],[]]
    for ident in range(0,math.factorial(n),2):
        graph=Stock(ident,n)
        if graph.connected:
            v=graph.signature
            if v in cat[0]:
                p=cat[0].index(v)
                cat[1][p].append(ident)
            else:
                cat[0].append(v)
                cat[1].append([ident])
    return cat

def shrub_book(n):
    cat=shrub_catalogue(n)
    bk={}
    for sig in cat[0]:
        bk[sig] = cat[1][cat[0].index(sig)]
    return bk

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
                adj +="•|"
            else:
                adj +=" |"
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
        
'=================================================================='
'   SWITCHES  AND OTHER MUTATIONS'
'=================================================================='

# make a deck of (atomic) switches for an n-tree
def make(n):
    deck=[]
    for i in range(1,n):
        for j in range(1,min(1+n-i,n)):
            deck.append((i,j))
    return deck

# make a list of all possible sets of 1, 2, 3... etc. sets of independent switches for an n-tree	
def poll(n):
    hands=[[],[]]
    deck=make(n)
    for card in deck:
        hands[1].append([card])
    while hands[-1]!=[]:
        hands.append([])
        for hand in hands[-2]:
            for card in deck:
                if valid(card,hand):
                    hands[-1].append(hand+[card])
    s=len(hands)-1
    return hands[:s]

# tests whether a card is independent and can be added to a hand
def valid(card,hand):
	for other in hand:
		if card[0] < other[0] or card[1]  in other or card[0] in other:
			return False
	return True
	
# gives the ident of a hand
def score(hand,n):
	s=0
	for card in hand:
		a=card[0]
		b=card[1]
		if a<b:
			s+=a*math.factorial(n-b)+b*math.factorial(n-a)
		elif a==b:
			s+=a*math.factorial(n-a)
		else:
			s+=(a-b)*math.factorial(n-b)+b*math.factorial(n-a)
	return s

def census(n):
    t=time.time()
    c=[signature(gcode(0,n))]
    cat=shrub_catalogue(n)[0]
    for deal in poll(n):
        for hand in deal:
            s=signature(gcode(score(hand,n),n))
            if s not in c:
                c.append(s)
    sorted(c,reverse=True)
    sorted(cat,reverse=True)
    for tree in c:
        if tree in cat:
            cat.remove(tree)
    return cat,time.time()-t

def quiz(a,b=0):
    b=max(b,a+1)
    for m in range(a,b):
        c=census(m)
        d=[]
        if len(c[0])>0:
            d=c[0][-1]
        print('\n',m,c[0],c[1],sep='\n')
            
def mutations(n):
    m=[[],[]]
    idents=[0]
    d=0
    for q in range(1,n//2+1):
        m[-1].append((q,q))
    for i in range(0,n):
        m.append([])
        pool=m[-2]
        for thing in pool:
            use=[x for x in list(range(thing[0]+2-n,n+1-thing[0])) if (x not in thing and -x not in thing)]
            use.remove(0)
            for slot in range(1,len(thing)):
                a=thing[slot-1]
                c=thing[slot]
                for item in use:
                    if abs(item)>thing[0]:
                        if usable(a,item,c,n):q=thing[:slot]+(item,)+thing[slot:]
                        if q not in m[-1]:
                            m[-1].append(q)
                            d=dcode(cantor(q,n))
                            if d > math.factorial(n):print(q)
                        if d not in idents:idents.append(d)
    return sorted(idents)
    #return m

def usable(a,b,c,n):
    if a < 0:
        if abs(a)<=abs(b): return False
    if b < 0:
        if abs(b)<=abs(c): return False
    if a>0:
        if a + abs(b) > n: return False
    if b>0:
        if b + abs(c) >n: return False
    if b in (a,c): return False
    return True

def cantor(mutation,size=0):
    c=[]
    m=len(mutation)
    for i in range(1,m):
        size=max(size,abs(mutation[i-1]+abs(mutation[i])))
    for i in range(0,size):
        c.append(0)
    for i in range(1,m):
        a=mutation[i-1]
        b=mutation[i]
        if a < 0:
            c[abs(b)-1]=-(a+abs(b))
        else:
            c[abs(b)-1]=a
    return c

def orthogonal(cantor1,cantor2):
    if len(cantor1) !=len(cantor2): return None
    return sum(i[0]*i[1] for i in zip(cantor1,cantor2))==0

def o(mut1,mut2,size=0):
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

def independent(mutation_list):
    size=len(mutation_list)
    for mutation in mutation_list[:size-1]:
        p=mutation_list.index(mutation)
        for other in mutation_list[p+1:]:
            for item in other:
                if item in mutation or -item in mutation: return False
    return True

def mix(n):
    'generates a complete set of all mutations and all compositions of mutations'
    m=[]
    mu=mutations(n)

def mutation_signatures(n):
    m=mutations(n)
    ms=[]
    for tree in m:
        ts=signature(gcode(tree,n))
        if ts != 'None' and ts not in ms:
            ms.append(ts)
    return sorted(ms,reverse=True)

def treecount(n):
    'The OEIS 000055 list of numbers of distinct trees with n vertices - redone '
    'so as to correspond to the number of edges, not vertices '
    if n > 35:
        return None
    num=[1, 1, 1, 2, 3, 6, 11, 23, 47, 106, 235, 551, 1301, 3159, 7741, 19320, 48629, 123867, 317955, 823065, 2144505, 5623756, 14828074, 39299897, 104636890, 279793450, 751065460, 2023443032, 5469566585, 14830871802, 40330829030, 109972410221, 300628862480, 823779631721, 2262366343746, 6226306037178]
    return num[n]

def trees(n):
    'a rough and ready count of how many gcodes produce connected trees, by'
    'number of edges.'
    num=[1, 1, 2, 4, 12, 40, 164, 752, 4020, 23576, 155632]
    if n < 11:
        return num[n]
    return int(trees(n-1)*2*n/3)

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
    #for x in range(0,min(2*m,sample)):
    while found < 30 and count < 3*m:
        ident=int(random.random()*m)
        count+=1
        if is_connected(gcode(ident,size)):
            found+=1
            print(found,count,int(m*found/count+.5),sep='\t')
        r=found/count
        q=int(m*found/count)
    print(time.time()-t,size,treecount(size),trees(size),q,found,count,sep='\t')

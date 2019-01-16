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

class Bush:
    def __init__(self,ident,size=0):
        self.ident=ident
        self.size=max(scale(ident),size)
        self.fcode=fcode(ident,size)
        self.edges=gcode(ident,size)
        self.adjlist=adjlist(self.edges)
        self.signature=signature(self.edges)
        self.trunk=trunk(self.edges)
        self.centre=centre(self.edges)
        self.diameter=len(self.trunk)
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
        return Bush(i,self.size)

    def bud(self):
        i=dcode(self.fcode+[0])
        s=self.size+1
        return Bush(i,s)

#===================================================================

def adjlist(graph): # lists all the nodes that link to the nth node, where n is the place in this list.
    ex=[[]]
    for links in graph:
        ex.append([])
    for links in graph:
        ex[links[0]].append(links[1])
        ex[links[1]].append(links[0])
    return ex

def scale(ident):
    s=0
    while math.factorial(s)<ident:
        s+=1
    return s-1

def fcode(ident,size=0):
    f=[]
    m=0
    while math.factorial(m)<=ident:
        f.insert(0,(ident%math.factorial(m+1))//math.factorial(m))
        m+=1
    return [0]*max(size-len(f),0)+f

def dcode(fb):# takes a factoradic representation of a number, and gives back the decimal form of the number.
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
    fb=fcode(ident,size)
    G=[]
    for i in range(0,len(fb)):
        G.append((fb[i],fb[i]+i+1))
    return G

def tcode(ident,size=0):
        size=max(scale(ident),size)
        f=fcode(ident,size)
        t=[]
        for place in range(0,size):
                a=f[place]
                b=size-place
                c=(a,b)
                t.append(c)
        return t
                
def degree_list(graph):
    d=[]
    alist=adjlist(graph)
    for i in range(0,len(alist)):
        d.append(len(alist[i]))
    return d

def centre(graph):
    L=trunk(graph)
    r=int(math.floor((len(L)-1)/2))
    s=int(math.ceil(len(L)-r-1))
    return [L[r],L[s]]

def rooted(root,graph):
    size=len(graph)
    rootlist=adjlist(graph)
    return scrub(root,rootlist)
    
def scrub(root,rootlist):
    for node in rootlist[root]:
        rootlist[node].remove(root)
        scrub(node,rootlist)
    return rootlist

# takes a set of edges and gives back the string version of the certificate        
def signature(graph):
    return re.sub('\ |\[|\]','',str(certificate(graph)))

# creates a list of all the nodes on the longest path or "trunk" of the tree
def trunk(graph):
    size=len(graph)
    a=adjlist(graph)
    path=[]
    for nodes in a:
        path.append([-1,-1,-1])
        if len(nodes)==1:
            j=a.index(nodes)
    for run in range(0,3):
        mark(j,run,path,a,0)
        mx=0
        for node in path:
            if node[run]>mx:
                mx=node[run]
                j=path.index(node)
    p=[]
    for j in range(0,mx+1):
        p.append(0)
    for node in path:
        if node[1]+node[2]==mx:
            p[node[2]]=path.index(node)
    return p

# recursively marks all the nodes in a Bush, to calculate the longest path or "trunk"
def mark(j,n,path,graph,count):
    path[j][n]=count
    count+=1
    for k in graph[j]:
        if path[k][n]==-1:
            mark(k,n,path,graph,count)

#constructs the noble Bush from the given seed
def noble(seed,size=0):
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
    return Bush(dcode(f),len(f))

#generates the Valiente certificate
def certificate(graph):
    size=len(graph)
    if is_connected(graph):
        c=centre(graph)
        a=adjlist(graph)
        w=[label(c[0],rooted(c[0],graph)),label(c[1],rooted(c[1],graph))]
        return sorted(w)[1]
    return None    
    
def label(node,rootlist):
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
def catalogue(n):
    if n==0:
        return [[0],[0]]
    cat=[[],[]]
    for ident in range(0,math.factorial(n),2):
        graph=Tree(ident,n)
        if graph.connected:
            v=graph.signature
            if v in cat[0]:
                p=cat[0].index(v)
                cat[1][p].append(ident)
            else:
                cat[0].append(v)
                cat[1].append([ident])
    return cat

def isometric(T1,T2):
    return T1.signature == T2.signature

def adjacency(graph): #gives back a printout of the adjacency matrix
    adj=""
    print(" " + str(0),end=' ')
    for i in range(1,graph.size+1):
        adj+="\n|"
        for j in range(0,i):
            if (j,i) in graph.edges:
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
    cat=catalogue(n)
    w=len(cat[0])
    for i in range(0,w):
        print(cat[0][i])
        Bush(cat[1][i][0],n).display()
        
'=================================================================='
'   SWITCHES '
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
    c=[signature(0,n)]
    cat=catalogue(n)[0]
    for deal in poll(n):
        for hand in deal:
            s=signature(score(hand,n),n)
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
        print(m,len(c[0]),d,c[1],sep='\t')
            
def mutations(n):
    pool=[[],[]]
    p=[0]
    q=1
    for i in range(1,n//2+1):
        pool[1].append([i,i])
    while p != []:
        q+=1
        pool.append([])
        p=pool[q-1]
        for perm in p:
            for slot in range(1,q):
                m=n-max(perm[slot-1],perm[slot])+2
                c=list(range(1,m))
                for item in perm:
                    if item in c:
                        c.remove(item)
                for item in c:
                    d=perm[:slot]+[item]+perm[slot:]
                    e=d.index(min(d))
                    d=d[e:-1]+d[:e]+[min(d)]
                    if d not in pool[q]:
                        pool[q].append(d)
    #return pool
    clade=[]
    for group in pool[1:]:
        level=pool.index(group)
        for perm in pool[level]:
            cantor=[0]*n
            for node in range(0,level):
                cantor[perm[node+1]-1]=perm[node]
            if cantor not in clade:
                clade.append(cantor)
    return clade

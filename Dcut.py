import networkx as nx
import matplotlib.pyplot as plt
import random
import json
import sys

if len(sys.argv) < 2:
    print('You should enter the graph file as argument')
    sys.exit(-1)

file_name = str(sys.argv[1])
graph_data = None
with open(file_name) as json_file:
    graph_data = json.load(json_file)

if not graph_data:
    sys.exit(-1)

nb_of_nodes = graph_data['nb_of_nodes']
edges = [tuple(e) for e in graph_data['edges']]

# Setting the graph
G = nx.Graph()
for i in range(1,nb_of_nodes+1):
    G.add_node(i, checked=False, connected=None, density=None)
G.add_edges_from(edges)

def resetAttributs(G:nx.Graph):
    for node in list(G.nodes):
        G.nodes[node]['checked'] = False
        G.nodes[node]['connected'] = None,
        G.nodes[node]['density'] = None

def s(u,v):
    nu = [n for n in G.neighbors(u)]
    nu.insert(0, u)
    nv = [n for n in G.neighbors(v)]
    nv.insert(0, v)
    nbIn = 0
    for n in nu:
        if n in nv:
            nbIn += 1
    nbUn = len(nu)+len(nv)-nbIn
    return nbIn/nbUn

def DCT(G:nx.Graph, leader):
    T = []
    DCT = nx.DiGraph()
    G.nodes[leader]['checked'] = True
    T.append(leader)
    while len(T) < G.number_of_nodes():
        maxv = -1
        for i in range(0, len(T)):
            u = T[i]
            for v in G.neighbors(u):
                if G.nodes[v]['checked'] == False:
                    if s(u,v) > maxv:
                        maxv = s(u,v)
                        p = v
                        q = u
        G.nodes[p]['checked'] = True
        G.nodes[p]['connected'] = q
        G.nodes[p]['density'] = maxv
        DCT.add_node(p)
        DCT.add_node(q)
        DCT.add_edge(q,p,density=maxv)
        T.append(p)
    return DCT

def countNodes(G:nx.Graph, node:int, c=0):
    neighbors = list(G.neighbors(node))
    if len(neighbors) == 0:
        return 0
    for neighbor in neighbors:
        c += countNodes(G, neighbor)+1
    return c

def minCut(G:nx.Graph):
    minimum = 9999
    edge = None
    for node in list(G.nodes):
        for neighbor in list(G.neighbors(node)):
            after = countNodes(G, neighbor) + 1
            before = G.number_of_nodes() - after
            d = G.get_edge_data(node, neighbor)
            if after <= before:
                dcut = d['density']/after
            else:
                dcut = d['density']/before
            if dcut<minimum:
                minimum = dcut
                edge = (node, neighbor)
    return edge

def partition(G:nx.Graph, node:int, C1=[]):
    C1.append(node)
    neighbors = list(G.neighbors(node))
    if len(neighbors) == 0:
        return
    for neighbor in neighbors:
        partition(G, neighbor, C1)

def Dcut(G:nx.Graph):
    nodes = list(G.nodes)
    dct = DCT(G, nodes[0])
    cut = minCut(dct)
    C1 = []
    partition(dct, cut[1], C1)
    C2 = [x for x in nodes if x not in C1]
    resetAttributs(G)
    return C1, C2

def plotGraph(G:nx.Graph):
    plt.subplot(121)
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif', label_pos=1)
    #nx.draw_networkx_edge_labels(G,pos)
    plt.show()

def plotPartitions(G:nx.Graph, partitions:[]):
    plt.subplot(121)
    pos = nx.spring_layout(G)
    colors = []
    for _ in range(0,len(partitions)):
        r = lambda: random.randint(0,255)
        colors.append('#%02X%02X%02X' % (r(),r(),r()))

    c = 0
    for i in partitions:
        nx.draw_networkx_nodes(G,pos,
                            nodelist=i,
                            node_color=colors[c],
                            node_size=500,
                        alpha=0.8)
        c += 1
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif', label_pos=1)
    plt.show()

def main():
    plotGraph(G)
    k = int(input('nb of cluster (>2):'))
    if k<2:
        print('k should be >=2')
        sys.exit(-1)
    result = [list(G.nodes)]
    result = []
    C1,C2=Dcut(G)
    result.extend([C1,C2])
    for _ in range(2,k):
        C = result.pop()
        G1 = G.subgraph(C)
        C1,C2 = Dcut(G1)
        result.insert(0,C2)
        result.insert(0,C1)
    print(result)
    plotPartitions(G,result)

main()
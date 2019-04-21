from processdata import *
# from datetime import date,datetime, timedelta
import networkx as nx
# import matplotlib
# import matplotlib.pyplot as plt
# from matplotlib.ticker import MaxNLocator

# from sympy import Interval, Union
# from scipy import optimize
# import sys
# import powerlaw


def helperconstructG(validnode, activechannel, gtype = 'G'):
    '''
    :param validnode: list<Node>
    :param activechannel: list<Channel>
    :param gtype: 'G'-unweighted, single-edge; 'Gmw'-multiedge; 'Gw'-weighted, single-edge
    :return: graph
    '''
    edgelist = getEdge(activechannel)
    if gtype == 'G':
        g = nx.Graph()
        g.clear()
        edges = [(e[0],e[1]) for e in edgelist]#redundacy
        for node in validnode:
            g.add_node(node.id,alias=node.alias, pubkey=node.pubkey, joined=node.jointime)
        g.add_edges_from(edges)#only the last duplicate edge is keeped
    if gtype == 'Gmw':
        g = nx.MultiGraph()
        g.clear()
        for node in validnode:
            g.add_node(node.id, alias=node.alias, pubkey=node.pubkey, joined=node.jointime)
        g.add_edges_from(edgelist)
    if gtype == 'Gw':
        g = nx.Graph()
        g.clear()
        edge_weight = [(e[0], e[1],{'weight':float(e[2]['weight'])}) for e in edgelist]
        for node in validnode:
            g.add_node(node.id, alias=node.alias, pubkey=node.pubkey, joined=node.jointime)
        for edge in edge_weight:
            u, v, cap = edge[0], edge[1], edge[2]['weight']
            if g.has_edge(u, v):#multi-edge,only the last multi edge attribute is keeped
                g.add_edge(u, v, weight=cap + g[u][v]['weight'] )
            else:
                g.add_edge(u, v, weight=cap)
    return g


def constructG(snapdate, nodes, channels, gtype='G'):
    # filterNode takes in date not datetime
    snapday = snapdate.date()
    return helperconstructG(filterNode(nodes, snapday), filterChannel(channels, snapdate), gtype)


def freeze(graphs):
    '''freeze graphs
    :param graphs: List<Graph>
    :return: void
    '''
    for graph in graphs:
        nx.freeze(graph)


def metrics(g):
    '''
    :param g: input graph
    :return: graph metrics
    '''
    n = nx.number_of_nodes(g)
    m = nx.number_of_edges(g)
    diameter = nx.diameter(g)
    # d = nx.average_shortest_path_length(g)
    # E = nx.global_efficiency(g)
    # r = nx.degree_assortativity_coefficient(g)
    # T = nx.transitivity(g)
    # C = nx.average_clustering(g)
    len(list(nx.isolates(g)))
    temp = nx.betweenness_centrality(g)
    betweencentrality = sorted(temp.items(), key=lambda kv: kv[1], reverse=True)
    temp = nx.closeness_centrality(g)
    closecentrality = sorted(temp.items(), key=lambda kv: kv[1], reverse=True)
    temp = nx.degree_centrality(g)
    degreecentrality = sorted(temp.items(), key=lambda kv: kv[1], reverse=True)


def getStats(nodes, channels, time):
    g = constructG(time, nodes, channels, 'Gw')
    nd = g.number_of_nodes()
    ch = g.number_of_edges()
    cap = sum([wt for u, v, wt in g.edges(data='weight')])
    iso = len(list(nx.isolates(g)))
    clus = nx.average_clustering(g)
    assor = nx.degree_assortativity_coefficient(g)
    gc = max(nx.connected_component_subgraphs(g), key=len)
    ndc = gc.number_of_nodes()
    chc = gc.number_of_edges()
    capc = sum([wt for u, v, wt in gc.edges(data='weight')])
    clusc = nx.average_clustering(gc)
    assorc = nx.degree_assortativity_coefficient(gc)
    return [nd, ch, cap, iso, clus, assor, ndc, chc, capc, clusc, assorc]

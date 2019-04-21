from ltgraph import *
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

# plt.rcParams['axes.labelsize'] = 16
# plt.rcParams['axes.labelweight'] = 'regular'

def knbrs(g, start, k):
    '''
    get kth order neighbor of node start in graph g
    :param g: graph
    :param start: Node/Int
    :param k: Int, order
    :return: Set<Node>/Set<Int>
    '''
    nbrs = set([start])
    for l in range(k):
        nbrs = set((nbr for n in nbrs for nbr in g[n]))
    return nbrs
def knbrs_total(g, start, k):
    '''
    return the union of all nbrs of start node within k steps
    :return: Set<Node/Int>
    '''
    allnbr = knbrs(g, start, 1)
    for i in range(1, k+1):
        allnbr = allnbr.union(knbrs(g, start, i))
    return allnbr
def gethop(g, alpha):
    '''
    return a list of least steps for all nodes in g
    :param g:
    :param alpha:
    :return: List<Int>
    '''
    hops = []
    # i is the least steps node n needs to reach at least alpha
    # percent of all nodes in graph
    for n in list(g.nodes()):
        i = 1
        print('n', n)
        while len(knbrs_total(g, n, i))-1 < (len(g)-1)*alpha:
            i = i+1
        hops.append(i)
        print(i)
    return hops

# effective eccentricty
def geteffecc(nodes, channels, day=datetime(2018, 12, 22, 12, 0), alist = [1, 0.9, 0.7]):
    #effective eccentricities with alpha list
    g = constructG(day, nodes, channels,'G')
    gc = max(nx.connected_component_subgraphs(g), key=len)
    effecc, label = [], []
    for alpha in alist:
        effecc.append(gethop(gc, alpha))
        label.append(r'$\alpha = $'+str(alpha))
    return [effecc, label, day]


def getecdf(data):
    '''
    return empirical cdf of effective eccentricity for plotting
    :param data: List<Int> Each hop repeated by appearance time
    :return: Set<List<Int>, List<Double>>
    '''
    N = len(data)
    X = np.sort(data)
    F = (np.array(range(N)) + 1) / float(N)
    X = list(X)
    F = list(F)
    # add small step(cdf = 0) at the front and large step(cdf=1) at the rear
    for i in reversed(range(2, min(data))):
        X.insert(0, i)
        F.insert(0, 0)
    for j in range(max(data)+1, 10):
        X.append(j)
        F.append(1)
    return (X, F)


def ploteccentricity(data):
    '''
    plot empirical cdf of eff eccentricity, data format is return of geteffecc
    '''
    fig, ax = plt.subplots()
    # font = {'family': 'serif', 'size': 16, 'serif': ['computer modern roman']}
    # plt.rc('font', **font)
    # plt.rc('legend', **{'fontsize': 14})
    # matplotlib.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}']
    #
    # plt.rcParams.update({'font.size': 13})
    res1 = getecdf(data[0][0])
    res2 = getecdf(data[0][1])
    res3 = getecdf(data[0][2])
    # res4 = getecdf(data[0][3])
    plt.plot(res1[0], res1[1], 'k', label=data[1][0])
    plt.plot(res2[0], res2[1], 'k--', label=data[1][1])
    plt.plot(res3[0], res3[1], 'k:', label=data[1][2])
    # plt.plot(res4[0], res4[1], 'k-.', label=data[1][3])
    plt.xlabel('Hops', fontsize=22)
    plt.ylabel('CDF', fontsize=22)
    # plt.xticks(fontsize=14)
    # plt.yticks(fontsize=14)
    plt.tick_params(labelsize=23)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(prop={'size': 20}, frameon=False, loc=4)
    fig.tight_layout()
    plt.savefig('fig/effeccen.png', dpi=300)
    plt.show()

# channel capacity
def getChannelcap(nodes, channels, day=datetime(2018, 12, 22, 12, 0)):
    '''
    return list of all channel capacities in gws and gmwc
    edge for edge capacity distribution, channel for multi edge capacity distribution
    :return: List<List<float>, List<float>>
    '''
    gw = constructG(day, nodes, channels, 'Gw')
    gmw = constructG(day, nodes, channels, 'Gmw')
    gwc = max(nx.connected_component_subgraphs(gw), key=len)
    gmc = max(nx.connected_component_subgraphs(gmw), key=len)
    edgecap, channelcap = [], []
    for (u, v, wt) in gwc.edges.data('weight'):
        edgecap.append(wt)
    for u, v, keys, weight in gmc.edges(data='weight', keys=True):
        if weight is not None:
            channelcap.append(weight)
    return (edgecap, channelcap)


def getchcapCDF(chcap, amount):
    '''get cdf of chcap for given amount'''
    cap = chcap[0]
    res = list(filter(lambda a: a <= amount, cap))
    cdf = len(res)/len(cap)
    return cdf


def plotChannelcap(channelCapacity):
    '''plot empirical cdf for channel capacity distribution'''
    edata, cdata = channelCapacity[0], channelCapacity[1]
    # method 1
    Ne, Nc = len(edata), len(cdata)
    Xe, Xc = np.sort(edata), np.sort(cdata)
    Fe = (np.array(range(Ne)) + 1) / float(Ne)
    Fc = (np.array(range(Nc)) + 1) / float(Nc)
    #plt.plot(X, F)
    # method 2--get the cdf of each distinct cap value by filtering
    # x = sorted(list(set(data)))
    # y = []
    # for i in x:
    #     y.append(getchcapCDF(channelCapacity, i))
    # plt.plot(x,y)
    # method 3--get occurence number of each distinct cap value and cumsum get Num(X < x)
    # x = sorted(list(set(data)))
    # y = [data.count(i) for i in x]
    # f = np.cumsum(y) / sum(y)
    # plt.plot(x, f)
    # fig, ax = plt.subplots()
    plt.plot(Xe, Fe, 'k', label="Edge")
    plt.plot(Xc, Fc, 'r--', label="Channel")
    ax, fig = plt.gca(), plt.gcf()
    ax.legend(frameon=False, fontsize=20)
    plt.xlabel('Capacity', fontsize=22)
    plt.ylabel('CDF', fontsize=22)
    # >>>>>>>>>>>>>>>>>>>>>>>>>
    # plt.xlim([0, 0.2])
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<
    # plt.tick_params(labelsize=23)
    plt.tick_params(labelsize=26)
    fig.tight_layout()
    # plt.savefig('fig/capdistrilocal0.2.png', dpi=300)
    plt.savefig('fig/capdistri.png', dpi=300)
    plt.show()


# routing efficiency
def removeEdges(nodes, channels, alpha=50, day=datetime(2018, 12, 22, 12, 0)):
    #G = G7 remove edges whose capacity is below target-alpha percentile
    g = constructG(day, nodes, channels, 'Gw')
    gc = max(nx.connected_component_subgraphs(g), key = len)
    h = gc.copy()
    remove = []
    edges = [(u, v, w) for (u, v, w) in h.edges(data='weight')]
    target = np.percentile(edges, alpha)
    for u, v, wt in edges:
        if wt < target:
            remove.append((u, v))
    h.remove_edges_from(remove)
    return h


# overload
def removeEdge(g, amount):
    '''
    in-place remove unqualified edges in graph g for given routing amount
    :param g: Graph, should be biggest connected component
    :param alpha: Number
    :return: void
    '''
    remove = []
    edges = [(u, v, w) for (u, v, w) in g.edges(data='weight')]
    for u, v, wt in edges:
        if wt < amount:
            remove.append((u, v))
    g.remove_edges_from(remove)


def percentileAmount(g, alphas):
    '''
    return routing amounts for given capacity pertentile(alpha)
    :param g: Graph
    :param alphas: List<Num>
    :return: List<float>
    '''
    weights = [w for (u, v, w) in g.edges(data='weight')]
    amounts = []
    for a in alphas:
        amounts.append(np.percentile(weights, a))
    return amounts


def getEfficiency(nodes, channels, day=datetime(2018, 12, 22, 12, 0)):
    '''
    return efficiency, 'second efficiency', isolated fraction and alpha list that used
    :param nodes: List<Node>
    :param channels: List<Channel>
    :param day: datetime
    :return: List<List>
    '''
    g = constructG(day, nodes, channels,'Gw')
    gc = max(nx.connected_component_subgraphs(g), key=len)
    # h = gc.copy()
    alphas = np.arange(0, 101, 2)
    N, plotNum = len(gc), len(alphas)
    efficiency = [0 for i in range(plotNum)]
    secondcc = [0 for i in range(plotNum)]#first decrease to zero
    isolates = [1 for i in range(plotNum)]
    amounts = percentileAmount(gc, alphas)
    for i in range(plotNum):
        print(i)
        removeEdge(gc, amounts[i])
        qc = sorted(nx.connected_components(gc), key=len, reverse=True)
        if len(qc) == 1:
            efficiency[i], secondcc[i], isolates[i] = 1, 0, 0
            continue
        size1, size2 = len(qc[0]), len(qc[1])
        if size2 > 1:
            tmp = size2/N
        elif size1 >1:
            tmp = 0
        else:
            break
        efficiency[i] = size1/N
        secondcc[i] = tmp
        isolates[i] = len(list(nx.isolates(gc)))/N
    return [efficiency, secondcc, isolates, alphas]

def getEfficiency2(nodes, channels, day=datetime(2018, 12, 22, 12, 0)):
    g = constructG(day, nodes, channels,'Gw')
    gc = max(nx.connected_component_subgraphs(g), key=len)
    # alphas = np.arange(0,101,5)
    alphas = [100]
    N, plotNum = len(gc), len(alphas)
    efficiency, secondcc, isolates = [], [], []
    amounts = percentileAmount(gc, alphas)
    for amount in amounts:
        print(amount)
        removeEdge(gc, amount)
        qc = sorted(nx.connected_components(gc), key=len, reverse=True)
        eff = len(qc[0])/N if len(qc[0]) > 1 else 0
        efficiency.append(eff)
        temp = len(qc[1])/N if len(qc) > 1 else 0
        secondcc.append(temp)
        isolates.append(len(list(nx.isolates(gc)))/N)
        if eff == 0:
            break
    leftNum = plotNum-len(efficiency)
    temp1 = [0 for i in range(leftNum)]
    temp2 = [1 for i in range(leftNum)]
    # for i in range(leftNum):
    efficiency = sum([efficiency, temp1],[])
    secondcc += temp1
    isolates += temp2
    return [efficiency, secondcc, isolates, alphas]


def plotEfficiency(data):
    eff, secondcc, isolates, x = data[0], data[1], data[2], data[3]
    fig, ax = plt.subplots()
    ax.plot(x, eff, c = 'black', markersize=5, marker='o', label='Efficiency')
    ax.plot(x, secondcc, c='red', markersize=5, marker='^', label='SQC')
    ax.plot(x, isolates, c='blue', markersize=5, marker='s', label='Isolates')
    ax.set_xlabel(r'Routing Amount Percentile $\beta$', fontsize=22)
    ax.set_ylabel('Fraction', fontsize=22)
    ax.legend(frameon=False, fontsize=16)
    plt.tick_params(labelsize=23)
    fig.tight_layout()
    plt.savefig('fig/routing.png', dpi=300)
    plt.show()
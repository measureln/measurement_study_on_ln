import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


def rankNode(g, index='between'):
    '''
    get the ranked nodelist of graph g evaluated using index from most important to least
    :param g: Graph, should use connected
    :param index: betweeness centrality or closeness centrality
    :return: List<Set<rank, index value>>
    '''
    if index == 'between':
        temp = nx.betweenness_centrality(g)
        betweencentrality = sorted(temp.items(), key=lambda kv: kv[1], reverse=True)
        return betweencentrality
    elif index == 'close':
        temp = nx.closeness_centrality(g)
        closecentrality = sorted(temp.items(), key=lambda kv: kv[1], reverse=True)
        return closecentrality
    elif index == 'pr':
        pr = nx.pagerank(g, alpha=0.9)
        pr = sorted(pr.items(), key=lambda kv: kv[1], reverse=True)
        return pr


def attack(g, nodeRank, graphEval, plotNum=100):
    # pnum is the # of data; rank is node rank criteria; eval is graph evaluation criteria
    n = g.number_of_nodes()
    removeNum = np.arange(0, n, int(n / plotNum))
    h = g.copy()
    # x = np.arange(0, n, int(n / 100)) / n
    if graphEval == 'eff':
        # for not removing nodes (original eff)
        efflist = [nx.global_efficiency(g)]
        # for rn in removeNum:
        for i in range(len(removeNum)-1):
            print(i)
            # H = g.copy()
            removenodes = [x[0] for x in nodeRank[removeNum[i]:removeNum[i+1]]]
            h.remove_nodes_from(removenodes)
            # efflist.append([rn/n, nx.global_efficiency(H)])
            efflist.append(nx.global_efficiency(h))
        return efflist
    if graphEval == 'cap':
        caplist = [1]
        weights = sum([w for u, v, w in g.edges(data='weight')])
        for i in range(len(removeNum) - 1):
            removenodes = [x[0] for x in nodeRank[removeNum[i]:removeNum[i + 1]]]
            h.remove_nodes_from(removenodes)
            newweights = sum([wt for u, v, wt in h.edges(data='weight')])
            caplist.append(newweights/weights)
        return caplist
    if graphEval == 'ccsize':
        slist = [1]
        for i in range(len(removeNum) - 1):
            removenodes = [x[0] for x in nodeRank[removeNum[i]:removeNum[i + 1]]]
            h.remove_nodes_from(removenodes)
            slist.append(len(max(nx.connected_component_subgraphs(h), key=len))/n)
        return slist


def plotattack(data, n, plotnum):
    '''

    :param data:
    :param n: total node number in graph;
    :param plotnum: number of plots; for getting x axis, can just return from above and pass in
    '''
    x = np.arange(0, n, int(n / plotnum)) / n
    fig, ax = plt.subplots()
    # linestyle
    ax.plot(x, data[0], c='black', markersize=5, marker='o', label='Betweeness')
    ax.plot(x, data[1], c='blue', markersize=5, marker='^', label='Closeness')
    # ax.plot(x, data[4], c='red', markersize=5, marker='s', linestyle='--', label="PageRank")
    ax.plot(x, data[4], c='red', markersize=5, marker='s', label="PageRank")
    ax.set_xlabel(r'Removed Nodes Fraction $\gamma$', fontsize=20)
    # ax.set_xlabel(r'Removed Nodes Fraction $\gamma$', fontsize=22)
    # ax.set_xlabel(r'$\frac{N_{rm}}{N}$', fontsize=16)
    ax.set_ylabel('Network Efficiency', fontsize=20)
    ax.legend(loc=0, frameon=False, fontsize=20)
    # plt.xticks(fontsize=14)
    # plt.yticks(fontsize=14)
    # plt.tick_params(labelsize=23)
    plt.tick_params(labelsize=18)
    fig.tight_layout()
    plt.savefig('fig/attackevaluation.png', dpi=300)
    plt.show()
    # plt.figure(2)
    # fig1, ax1 = plt.gcf(), plt.gca()
    fig1, ax1 = plt.subplots()
    ax1.plot(x, data[2], c='black', markersize=5, marker='o', label='Network Capacity')
    ax1.plot(x, data[3], c='blue', markersize=5, marker='^', label=r'$LCC$ Size')
    ax1.set_xlabel(r'Removed Nodes Fraction $\gamma$', fontsize=20)
    # ax1.set_xlabel(r'Removed Nodes Fraction $\gamma$', fontsize=22)
    ax1.set_ylabel('Network Performance', fontsize=20)
    # if performance is not normalized, can use below to set different scale on left and right
    # ax2 = ax1.twinx()
    # ax2.plot(x, data[3], c='blue', markersize=3, marker='s', label='Biggest CC Size')
    # lines, labels = ax1.get_legend_handles_labels()
    # lines2, labels2 = ax2.get_legend_handles_labels()
    # ax2.legend(lines + lines2, labels + labels2, loc=0, frameon=False)
    ax1.legend(loc=0, frameon=False, fontsize=20)
    plt.tick_params(labelsize=18)
    fig1.tight_layout()
    plt.savefig('fig/attackperformance.png', dpi=300)
    plt.show()

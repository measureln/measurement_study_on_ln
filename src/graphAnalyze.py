import statistics
from processdata import *
from ltgraph import *
from analysis import *
from efficiency import *
from robustness import *
from steadiness import *
from small import *
from dynamicSG import *

dir = 'robtex_0404'
nodefile = dir + '/' + 'robtex_nodediscovered_4.4.txt'
# nodefile = dir + '/' + 'robtex_mainetnode_12.24.txt'
# chfile = dir+'/robtex_channel_1022_mod.txt'
chfile = dir+'/robtex_channel_0404.txt'
# process data
nodes = readNode(nodefile)
nodemap = indexNode(nodes)
chlist = readChannel(chfile)
channels = buildChannel(chlist, nodemap)
# filter testnet nodes(nodes with no channels all the time)
# mnodesID = set()
# mnodes = []
# for channel in channels:
#     mnodesID.add(channel.node1.pubkey)
#     mnodesID.add(channel.node2.pubkey)
# for node in nodes:
#     if node.pubkey in mnodesID:
#         mnodes.append(node)
# nodes = mnodes
# nodemap = indexNode(nodes)
# # write to file
# dirname = 'robtex_1224'
# filename = dirname + '/'+'robtex_mainetnode_12.24.txt'
# f = open(filename, 'w')
# f.write('index\talias\tpubkey\tdiscover\n')
# count = 1
# for node in nodes:
#     f.write('{}\t{}\t{}\t{}\n'.format(count, node.alias, node.pubkey, node.jointime))
#     count += 1
# f.close()

existnodes = filterNode(nodes)
activechannel = filterChannel(channels)

edgelist = getEdge(channels)

# ltgraph
G = constructG(datetime(2019, 4, 1, 12, 0), nodes, channels,'G')
GW = constructG(datetime(2019, 4, 1, 12, 0), nodes, channels,'Gw')
GM = constructG(datetime(2019, 4, 1, 12, 0), nodes, channels,'Gmw')

GC = max(nx.connected_component_subgraphs(G), key = len)
GMC = max(nx.connected_component_subgraphs(GM), key = len)
GWC = max(nx.connected_component_subgraphs(GW), key = len)
freeze([G, GW, GM, GC, GMC, GWC])

stats = getStats(nodes, channels, datetime(2019, 4, 1, 12, 0))


# analysis
lifes = channellife(channels, datetime(2019, 4, 1, 12, 0))
fees = fee(channels, datetime(2019, 4, 1, 12, 0))
openfee, closefee = fees[0], fees[1]
totalfee = openfee + closefee
statistics.mean(openfee)
np.cov(openfee)
caps = channelcap(channels)
stats = analy(nodes, channels)
plotanaly(stats)
# powerlaw
degree = getdegree(nodes, channels)
alpha = pwlaw(degree)
# degree cdf

# efficiency
# eccentrencity
eccentricity = geteffecc(nodes, channels, datetime(2019, 4, 1, 12, 0), [1, 0.9, 0.7])
ploteccentricity(eccentricity)
# capacity
channelCap = getChannelcap(nodes, channels)
plotChannelcap(channelCap)
# efficiency
effdata = getEfficiency(nodes, channels, datetime(2019, 4, 1, 12, 0))
plotEfficiency(effdata)

# add-on
efdata = getEff(nodes, channels)
eftdata = getTimeEff(nodes, channels)
plotTimeEff(eftdata)

# robustness
# node importance
# GC
temp = nx.betweenness_centrality(GC)
betweencentrality = sorted(temp.items(), key=lambda kv: kv[1], reverse=True)
temp = nx.closeness_centrality(GC)
closecentrality = sorted(temp.items(), key=lambda kv: kv[1], reverse=True)
# G
temp = nx.betweenness_centrality(G)
between = sorted(temp.items(), key=lambda kv: kv[1], reverse=True)
temp = nx.closeness_centrality(G)
close = sorted(temp.items(), key=lambda kv: kv[1], reverse=True)
# consider weight
temp = nx.betweenness_centrality(GW, weight='weight')
wbetween = sorted(temp.items(), key=lambda kv: kv[1], reverse=True)
temp = nx.closeness_centrality(GW, distance='weight')
wclose = sorted(temp.items(), key=lambda kv: kv[1], reverse=True)
#
prtest = nx.pagerank(GC, alpha=0.9)
prtests = sorted(prtest.items(), key=lambda kv: kv[1], reverse=True)

# meaningless to remove isolated nodes
pr = rankNode(GC, 'pr')
# get node cap percentile
nodesCapLs = []
for n in GMC:
    nedge = dict(GWC[n])
    temp = 0
    for e in nedge:
        temp += nedge[e]['weight']
    nodesCapLs.append(temp)

nodecap = 0
d = dict(GW[1])
for n in d:
    nodecap += d[n]['weight']
def getnodecap(n):
    nodecap = 0
    d = dict(GW[n])
    for n in d:
        nodecap += d[n]['weight']
    return nodecap
np.percentile(nodesCapLs, nodecap)

# attack
betweencentrality = rankNode(GC, 'between')
closecentrality = rankNode(GC, 'close')
robustBetEffi = attack(GC, betweencentrality, 'eff')
robustCloEffi = attack(GC, closecentrality, 'eff')
robustPr = attack(GC, pr, 'eff')
#
# robustCap = attack(GC, betweencentrality, 'cap')
# robustSize = attack(GC, betweencentrality, 'ccsize')
robustCap = attack(GWC, pr, 'cap')
robustSize = attack(GC, pr, 'ccsize')
# plot
n = GC.number_of_nodes()
plotNum = 100
plotattack([robustBetEffi, robustCloEffi, robustCap, robustSize, robustPr], n, plotNum)

#add-on
rbtdata = getTimeRobust(nodes, channels, pr)
plotTimeRobust(rbtdata)
# steadiness
# avai
availability = getAvailas(channels)
plotavaila3(availability)
# commu
pairs = getPairChannel(channels)
commu = communication(pairs)
commus = getCommus(nodes, pairs, type='nonzero')
# plotcommu(commus)
# a & c
# plotac([availability, commus])
# stability
stability = conscommu(pairs)
stabs = getStabs(nodes, pairs, type='nonzero')

# plotacs([availability, commus, stabs])
# use below
plotcs([commus, stabs])

# a ans s for multi channel node pairs
mcommu = multicommunication(pairs)
mstab = multistability(pairs)

mcommus = getmCommus(pairs)
mstabs = getmStabs(pairs)
# plotcsm([mcommu, mstab])#one day
plotmcs([mcommus, mstabs])#use this 3 days

# overlap
intersec = overlapClose(pairs)
separat = overlapFar(pairs)
plotOverlap(separat)

# get multi channels info
pairChNum = []
for pair in pairs:
    pairChNum.append(len(pairs[pair]))
plotpairChNum(pairChNum)

# cost
avgCost = getCost(nodes, channels, datetime(2018, 10, 20, 12, 0))

# channellist = getpairs(channeltimelist,nodeindex)
# if __name__ == 'main':
#     dir = 'robtex_1022'
#     nodelist = readnode(dir + '/' + 'robtex_nodediscovered_10.22.txt')=
data1, data2 = avgCost[0], avgCost[1]
n1, n2 = len(data1), len(data2)
f1 = np.arange(1, n1+1)/n1
x1 = sorted(data1)
f2 = np.arange(1, n2+1)/n2
x2 = sorted(data2)
plt.plot(x1, f1)
plt.plot(x2, f2)
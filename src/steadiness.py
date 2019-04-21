from sympy import Interval, Union
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

from processdata import *

# availability
def getAvaila(channels, date=datetime(2018, 12, 22, 12, 0)):#channel availability, snapshoted at date
    '''
    get a list of channel availabilities for all channel that was opened before date
    :param channels: List<Channel>
    :param date:
    :return: List<float>
    '''
    availability = []
    # openedChannels = list(filter(lambda x: x.opentime <= date, channels))
    for channel in channels:
        if channel.opentime <= date:
            time = date - channel.opentime
            if channel.closetime == 'None' or channel.closetime > date:
                availability.append(1)
            else:
                opentime = channel.closetime - channel.opentime
                availability.append(opentime / time)
    return availability


def getAvailas(channels, dates=[datetime(2018,6,20,12,0), datetime(2018,12,5,12,0), datetime(2019,4,1,12,0)]):
    avais = []
    for date in dates:
        avais.append(getAvaila(channels, date))
    return avais


def getavaicdf(channels, a, day=datetime(2018, 10, 22, 12, 0)):
    avai = getAvaila(channels, day)
    res = list(filter(lambda x: x <= a, avai))
    return len(res)/len(avai)

# def plotavaila2(date = datetime(2018,6,30,12,0)):#on certain date
#     avaifraction = availa(date)
#     x = np.sort(avaifraction)
#     y = np.arange(1, len(x)+1)/len(x)
#     #plt.plot(x,y,marker = '.',linestyle = 'none')
#     plt.plot(x, y,c = 'blue')
#     fig = plt.gcf()
#     plt.xlabel('Channel Availability')
#     plt.ylabel('CDF')
#     #plt.margins(0.02)
#     fig.tight_layout()
#     plt.savefig('robtex_0630/fig3/channelavaila.png', dpi=600)
#     plt.show()
def plotavaila3(data):
    fig, ax = plt.subplots()
    x = np.sort(data[0])
    f = np.arange(1, len(x)+1)/len(x)
    # ax.plot(x, f, c='black', label=r'$S_1$')
    ax.plot(x, f, c='black', marker='^', markersize=0.3, label=r'$S_1$')
    x = np.sort(data[1])
    f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x, f, c='red', marker='o', markersize=0.3, label=r'$S_2$')
    # ax.plot(x, f, c='blue', linestyle='-.', label=r'$S_2$')
    x = np.sort(data[2])
    f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x, f, c='blue', marker='s', markersize=0.3, label=r'$S_3$')
    # ax.plot(x, f, c='black', linestyle='--', label=r'$S_3$')
    plt.xlabel('Channel Availability')
    plt.ylabel('CDF')
    plt.legend(loc=0, frameon = False)
    fig.tight_layout()
    plt.savefig('fig/channelavaila.png', dpi=600)
    plt.show()


# communication
def union(data):  # return interval, use .start/end to obtain num
    """ Union of a list of intervals e.g. [(1,2),(3,4)] """
    intervals = [Interval(begin, end) for (begin, end) in data]
    u = Union(*intervals)
    return [list(u.args[:2])] if isinstance(u, Interval) \
        else list(u.args)


def communication(pairchannels, date=datetime(2018, 12, 22, 12, 0), base=datetime(2017, 12, 1, 0, 0)):
    '''
    return the communication between all pair of nodes
    :param pairchannels: Map<k:nodepair, v:List<Channel>>, nodepair: (node1id, node2id)
    :param date: only consider node pairs that started communication before date
    :param base: for getting interval
    :return:List<float>
    '''
    commu = []
    for nodepair in pairchannels:
        unionset = []
        commutime = 0
        # iterate over all historic and now channels between this pair of nodes
        for channel in pairchannels[nodepair]:
            if channel.opentime < date:
                if channel.closetime == 'None' or channel.closetime > date:
                    # then set close time to snapdate
                    unionset.append(((channel.opentime - base).total_seconds(), (date - base).total_seconds()))
                else:
                    unionset.append(((channel.opentime - base).total_seconds(), (channel.closetime - base).total_seconds()))
        # if nodes havent opened channel until date, i.e, all channels between this pair is opend after observeday
        if len(unionset) == 0:
            continue
        # union channel time interval(open time to close time)
        unionres = union(unionset)
        # if only 1 interval is obtained after union
        if len(unionres) == 1:
            commutime = unionres[0][1] - unionres[0][0]
            firstopen = unionres[0][0]
        else:
            firstopen = unionres[0].start
            for intval in unionres:
                commutime = commutime + (intval.end - intval.start)
        total = ((date - base).total_seconds()) - firstopen
        commu.append(commutime / total)
    commu = [float(x) for x in commu]
    return commu


def getCommus(nodes, pairchannels, type='nonzero', dates=[datetime(2018,6,1,12,0), datetime(2018,8,5,12,0), datetime(2018,12,22,12,0)],
              base=datetime(2017, 12, 1, 0, 0)):
    commus = []
    if type == 'nonzero':
        for date in dates:
            commus.append(communication(pairchannels, date, base))
    elif type == 'all':
        for date in dates:
            commus.append(all_communication(nodes, pairchannels, date, base))
    return commus


def plotcommu(data):
    fig, ax = plt.subplots()
    x = np.sort(data[0])
    f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x, f, c='black', label=r'$S_1$')
    ax.plot(x, f, c='black', marker='^', markersize=0.3, label=r'$S_1$')
    x = np.sort(data[1])
    f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x, f, c='red', marker='o', markersize=0.3, label=r'$S_2$')
    # ax.plot(x, f, c='blue', linestyle='-.', label=r'$S_2$')
    x = np.sort(data[2])
    f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x, f, c='blue', marker='s', markersize=0.3, label=r'$S_3$')
    # ax.plot(x, f, c='black', linestyle='--', label=r'$S_3$')
    plt.xlabel('Nodes Communication')
    plt.ylabel('CDF')
    plt.legend(loc=0, frameon=False)
    fig.tight_layout()
    plt.savefig('fig/nodecommu.png', dpi=600)
    plt.show()


def plotac(data):
    avais, commus = data[0], data[1]
    fig, ax = plt.subplots()
    x = np.sort(avais[0])
    f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::40], f[::40], c='black', marker='^', markersize=2, label=r'$S_1$ Channel Availability')
    x = np.sort(avais[1])
    f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::40], f[::40], c='black', marker='o', markersize=2, label=r'$S_2$')
    x = np.sort(avais[2])
    f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::60], f[::60], c='black', marker='s', markersize=2, label=r'$S_3$')
    x = np.sort(commus[0])
    f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::60], f[::60], c='red', marker='^', markersize=2, label=r'$S_1$ Nodes Communication Availability')
    x = np.sort(commus[1])
    f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::80], f[::80], c='red', marker='o', markersize=2, label=r'$S_2$')
    x = np.sort(commus[2])
    f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::80], f[::80], c='red', marker='s', markersize=2, label=r'$S_3$')
    ax.legend(loc=0, prop={'size': 8}, frameon=False)
    plt.ylabel('CDF', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    fig.tight_layout()
    plt.savefig('fig/ac.png', dpi=600)
    plt.show()


# stability
def conscommu(pairchannels, date = datetime(2018, 12, 22, 12, 0), base=datetime(2017, 12, 1, 0, 0)):
    # first union, then find the longest interval
    conscommu = []
    # for nodepair in pairchannels:
    #     # get List<Channel> between this pair
    #     ndchannels = pairchannels[nodepair]
    #     # get the open time of this node pair's first channel
    #     firstopen = ndchannels[0].opentime
    #     # for ndchannel in ndchannels:
    #     #     if ndchannel.opentime < firstopen:
    #     #         firstopen = ndchannel.opentime
    #     if ndchannels[0].closetime == 'None' or ndchannels[0].closetime > date:
    #         longest = date - ndchannels[0].opentime
    #     else:
    #         longest = ndchannels[0].closetime - ndchannels[0].closetime.opentime
    #     for x,y in chlist[channel]:
    #         if x < firstopen:
    #             firstopen = x
    #         if y == 'None' or y > date:
    #             if longest < date-x:
    #                 longest = date-x
    #         elif y-x >longest:
    #             #print(x,y)
    #             longest = y-x
    #     if firstopen < date:
    #         conscommu.append(longest/(date-firstopen))
    for nodepair in pairchannels:
        unionset = []
        longest = 0
        # iterate over all channels between this pair of nodes
        for channel in pairchannels[nodepair]:
            if channel.opentime < date:
                if channel.closetime == 'None' or channel.closetime > date:
                    unionset.append(((channel.opentime - base).total_seconds(), (date - base).total_seconds()))
                else:
                    unionset.append(
                        ((channel.opentime - base).total_seconds(), (channel.closetime - base).total_seconds()))
        if len(unionset) == 0:
            continue
        unionres = union(unionset)
        if len(unionres) == 1:
            longest = unionres[0][1] - unionres[0][0]
            firstopen = unionres[0][0]
        else:
            firstopen = unionres[0].start
            for intval in unionres:
                longest = max(longest, (intval.end - intval.start))
        total = ((date - base).total_seconds()) - firstopen
        conscommu.append(longest / total)
    conscommu = [float(x) for x in conscommu]
    return conscommu


def getStabs(nodes, pairchannels, type='nonzero', dates=[datetime(2018,6,1,12,0), datetime(2018,8,5,12,0), datetime(2018,12,22,12,0)],
             base=datetime(2017, 12, 1, 0, 0)):
    stabs = []
    if type == 'nonzero':
        for date in dates:
            stabs.append(conscommu(pairchannels, date, base))
    elif type == 'all':
        for date in dates:
            stabs.append(all_conscommu(nodes, pairchannels, date, base))
    return stabs


def plotacs(data):
    avais, commus, stabs = data[0], data[1], data[2]
    fig, ax = plt.subplots()
    x = np.sort(avais[0])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::40], f[::40], c='black', marker='^', markersize=2, label=r'$S_1$ Channel Availability')
    x = np.sort(avais[1])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::70], f[::70], c='black', marker='o', markersize=2, label=r'$S_2$')
    x = np.sort(avais[2])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::90], f[::90], c='black', marker='x', markersize=3, label=r'$S_3$')

    x = np.sort(commus[0])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::40], f[::40], c='red', marker='^', markersize=2, label=r'$S_1$ Nodes Communication Availability')
    x = np.sort(commus[1])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::70], f[::70], c='red', marker='o', markersize=2, label=r'$S_2$')
    x = np.sort(commus[2])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::90], f[::90], c='red', marker='x', markersize=3, label=r'$S_3$')

    x = np.sort(stabs[0])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::40], f[::40], c='blue', marker='^', markersize=2, label=r'$S_1$ Nodes Communication Stability')
    x = np.sort(stabs[1])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::70], f[::70], c='blue', marker='o', markersize=2, label=r'$S_2$')
    x = np.sort(stabs[2])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x[::90], f[::90], c='blue', marker='x', markersize=3, label=r'$S_3$')
    ax.legend(loc=0, prop={'size': 9}, frameon=False)
    plt.ylim(0.2, 1)
    plt.ylabel('1 - CDF', fontsize=16)
    # plt.ylabel('CDF', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    fig.tight_layout()
    plt.savefig('fig/acs_reverse.png', dpi=600)
    # plt.savefig('fig/acs.png', dpi=600)
    plt.show()

def plotcs(data):
    commus, stabs = data[0], data[1]
    fig, ax = plt.subplots()
    # commu
    x = np.sort(commus[0])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::180], f[::180], c='red', marker='^', markersize=5, label=r'$S_1$ Communication')
    ax.plot(x[::180], f[::180], c='red', label=r'$S_1\ \rho_{a}$')
    x = np.sort(commus[1])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::190], f[::190], c='red', marker='o', markersize=4, label=r'$S_2$ Communication')
    ax.plot(x[::190], f[::190], c='black', label=r'$S_2\ \rho_{a}$')
    x = np.sort(commus[2])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::230], f[::230], c='red', marker='x', markersize=5, label=r'$S_3$ Communication')
    ax.plot(x[::230], f[::230], c='blue', label=r'$S_3\ \rho_{a}$')
    #stab
    x = np.sort(stabs[0])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::160], f[::160], c='black', marker='^', linestyle='--', markersize=5, label=r'$S_1$ Stability')
    ax.plot(x[::160], f[::160], c='red', linestyle='--', label=r'$S_1\ \rho_{s}$')
    x = np.sort(stabs[1])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::230], f[::230], c='black', marker='o', linestyle='--', markersize=4, label=r'$S_2$ Stability')
    ax.plot(x[::230], f[::230], c='black', linestyle='--', label=r'$S_2\ \rho_{s}$')
    x = np.sort(stabs[2])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::280], f[::280], c='black', marker='x', linestyle='--', markersize=5, label=r'$S_3$ Stability')
    ax.plot(x[::280], f[::280], c='blue', linestyle='--',label=r'$S_3\ \rho_{s}$')
    ax.legend(prop={'size': 16}, frameon=False)
    plt.ylim(0.2, 1)
    plt.ylabel('1 - CDF', fontsize=22)
    plt.xlabel(r'$\rho_{a}, \rho_{s}$', fontsize=22)
    plt.tick_params(labelsize=23)
    fig.tight_layout()
    plt.savefig('fig/csreverse.png', dpi=300)
    plt.show()

# commu and stab of all nodes(including those doesn't have channel)
def all_communication(nodes, pairchannels, date=datetime(2018, 10, 20, 12, 0), base=datetime(2017, 12, 1, 0, 0)):
    commu = communication(pairchannels, date, base)
    num = len(commu)
    nodeNum = len(filterNode(nodes, date.date()))
    all = int(nodeNum*(nodeNum - 1) / 2)
    zeros = [0 for i in range(all-num)]
    commu += zeros
    return commu


def all_conscommu(nodes, pairchannels, date = datetime(2018, 10, 20, 12, 0), base=datetime(2017, 12, 1, 0, 0)):
    stab = conscommu(pairchannels, date, base)
    num = len(stab)
    nodeNum = len(filterNode(nodes, date.date()))
    all = int(nodeNum * (nodeNum - 1) / 2)
    zeros = [0 for i in range(all - num)]
    stab += zeros
    return stab


# communication and stability for pairs that have opened at least two edges before day
def multicommunication(pairchannels, date=datetime(2018, 12, 22, 12, 0), base=datetime(2017, 12, 1, 0, 0)):
    commu = []
    for nodepair in pairchannels:
        openchannels = []
        for ch in pairchannels[nodepair]:
            if ch.opentime < date:
                openchannels.append(ch)
        if len(openchannels) < 2:
            continue
        unionset = []
        commutime = 0
        for channel in openchannels:
            if channel.closetime == 'None' or channel.closetime > date:
                closeTime = date
            else:
                closeTime = channel.closetime
            openTime = channel.opentime
            unionset.append(((openTime - base).total_seconds(), (closeTime-base).total_seconds()))
        unionres = union(unionset)
        # if only 1 interval is obtained after union
        if len(unionres) == 1:
            commutime = unionres[0][1] - unionres[0][0]
            firstopen = unionres[0][0]
        else:
            firstopen = unionres[0].start
            for intval in unionres:
                commutime = commutime + (intval.end - intval.start)
        total = ((date - base).total_seconds()) - firstopen
        commu.append(commutime / total)
    commu = [float(x) for x in commu]
    return commu

def getmCommus(pairs, dates=[datetime(2018,6,1,12,0), datetime(2018,8,5,12,0), datetime(2018,12,22,12,0)],
              base=datetime(2017, 12, 1, 0, 0)):
    commus = []
    for date in dates:
        commus.append(multicommunication(pairs, date, base))
    return commus



def multistability(pairchannels, date=datetime(2018, 12, 22, 12, 0), base=datetime(2017, 12, 1, 0, 0)):
    validPair = {}
    for nodepair in pairchannels:
        chs = 0
        for ch in pairchannels[nodepair]:
            if ch.opentime < date:
                chs += 1
        if chs >= 2:
            validPair[nodepair] = pairchannels[nodepair]
    return conscommu(validPair, date, base)

def getmStabs(pairs, dates=[datetime(2018,6,1,12,0), datetime(2018,8,5,12,0), datetime(2018,12,22,12,0)],
              base=datetime(2017, 12, 1, 0, 0)):
    stabs = []
    for date in dates:
        stabs.append(multistability(pairs, date, base))
    return stabs

def plotcsm(data):
    mcommus, mstabs = data[0], data[1]
    fig, ax = plt.subplots()
    x = np.sort(mcommus)
    f = np.arange(1, len(x) + 1) / len(x)
    rf = 1 - f
    ax.plot(x[::30], rf[::30], c='red', marker='^', markersize=3, label='Communication Availability(multi)')
    x = np.sort(mstabs)
    f = np.arange(1, len(x) + 1) / len(x)
    rf = 1 - f
    ax.plot(x[::30], rf[::30], c='blue', marker='o', markersize=3, label='Nodes Communication Stability(multi)')
    ax.legend(loc=0, prop={'size': 13}, frameon=False)
    plt.ylabel('1 - CDF', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    fig.tight_layout()
    plt.savefig('fig/mcs.png', dpi=300)
    plt.show()

def plotmcs(data):
    commus, stabs = data[0], data[1]
    print(len(commus))
    fig, ax = plt.subplots()
    # commu
    x = np.sort(commus[0])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::180], f[::180], c='red', marker='^', markersize=5, label=r'$S_1$ Communication')
    ax.plot(x[::180], f[::180], c='red', label=r'$S_{1}\ \rho_{a}$')
    x = np.sort(commus[1])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::190], f[::190], c='red', marker='o', markersize=4, label=r'$S_2$ Communication')
    ax.plot(x[::190], f[::190], c='black', label=r'$S_2\ \rho_{a}$')
    x = np.sort(commus[2])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::230], f[::230], c='red', marker='x', markersize=5, label=r'$S_3$ Communication')
    ax.plot(x[::230], f[::230], c='blue', label=r'$S_3\ \rho_{a}$')
    #stab
    x = np.sort(stabs[0])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::160], f[::160], c='black', marker='^', linestyle='--', markersize=5, label=r'$S_1$ Stability')
    ax.plot(x[::160], f[::160], c='red', linestyle='--', label=r'$S_1\ \rho_{s}$')
    x = np.sort(stabs[1])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::230], f[::230], c='black', marker='o', linestyle='--', markersize=4, label=r'$S_2$ Stability')
    ax.plot(x[::230], f[::230], c='black', linestyle='--', label=r'$S_2\ \rho_{s}$')
    x = np.sort(stabs[2])
    f = 1 - np.arange(1, len(x) + 1) / len(x)
    # f = np.arange(1, len(x) + 1) / len(x)
    # ax.plot(x[::280], f[::280], c='black', marker='x', linestyle='--', markersize=5, label=r'$S_3$ Stability')
    ax.plot(x[::280], f[::280], c='blue', linestyle='--',label=r'$S_3\ \rho_{s}$')
    ax.legend(prop={'size': 16}, frameon=False)
    plt.ylim(0.2, 1)
    plt.ylabel('1 - CDF', fontsize=22)
    plt.xlabel(r'$\rho_{a}, \rho_{s} (multi)$', fontsize=22)
    plt.tick_params(labelsize=23)
    fig.tight_layout()
    plt.savefig('fig/mcsreverse.png', dpi=300)
    plt.show()

def plotpairChNum(data):
    x = np.sort(data)
    f = np.arange(1, len(x) + 1)/len(x)
    fig, ax = plt.subplots()
    ax.plot(x, f, 'k')
    # plt.xlim([1, 5])
    plt.xlabel('Pair Channel Numbers', fontsize=22)
    plt.ylabel('CDF', fontsize=22)
    plt.tick_params(labelsize=23)
    plt.tick_params(labelsize=26)
    fig.tight_layout()
    # plt.savefig('fig/multichnum_local.png', dpi=300)
    plt.savefig('fig/multichnum.png', dpi=300)
    plt.show()

def getPairChNumCDF(data, num):
    x = np.sort(data)
    return len(list(filter(lambda a: a <= num, x)))/len(data)


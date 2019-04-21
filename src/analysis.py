# from processdata import *
from ltgraph import *
from datetime import date,datetime, timedelta
import powerlaw
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

def channellife(channellist, closebefore=datetime(2018,10,20,12,0)):
    '''
    return all lifes of channels that are closed before closebefore
    :param channellist:
    :param closebefore:
    :return: List<double>
    '''
    clifes = []
    for channel in channellist:
        if channel.closetime == 'None':
            continue
        if channel.closetime <= closebefore:
            life = channel.closetime - channel.opentime
            life = life.days + life.seconds/(3600*24)
            clifes.append(life)
    return clifes


def fee(channellist, observe=datetime(2018,10,20,12,0)):
    '''
    return open fee for all channels that is opened before observe. same for close fee
    :param channellist: List<Channel>
    :param observe:
    :return: List<double>
    '''
    openfees, closefees = [], []
    for channel in channellist:
        if channel.opentime <= observe:
            openfees.append(channel.openfee)
        if channel.closetime != 'None' and channel.closetime <= observe:
            closefees.append(channel.closefee)
    return (openfees, closefees)


def channelcap(channellist, openbefore=datetime(2018,12,22,12,0)):
    '''
    return a list of capacity of channels that are opened before openbefore
    :param channellist: List<Channel>
    :param openbefore:
    :return: List<double>
    '''
    caps = []
    for channel in channellist:
        if channel.opentime <= openbefore:
            caps.append(channel.capacity)
    return caps


def analy(nodes, channels, start='2018 1 1 12 0',end='2018 10 20 12 0'):
    '''
    :param start:
    :param end:
    :return: List<List<float>>
    number of nodes, isolated nodes, channels(multi edge), edges, network capacity
    in everyday from start to end
    '''
    d1, d2 = datetime.strptime(start,'%Y %m %d %I %S'), datetime.strptime(end,'%Y %m %d %I %S')
    days = [d1 + timedelta(days=x) for x in range((d2 - d1).days + 1)]
    #date = [matplotlib.dates.date2num(day) for day in daylist]
    nodenum, isolate, cc, chnum, edgenum, netcap = [], [], [], [], [], []
    for day in days:
        print(day)
        g = constructG(day, nodes, channels, 'Gw')
        gc = max(nx.connected_component_subgraphs(g), key=len)
        cc.append(gc.number_of_nodes())
        nodenum.append(g.number_of_nodes())
        isolate.append(len(list(nx.isolates(g))))
        edgenum.append(g.number_of_edges())
        edge = list(g.edges(data = 'weight'))
        cap = sum([weight[2] for weight in edge])
        netcap.append(cap)
        chnum.append(len(filterChannel(channels, day)))
    return [nodenum, isolate, cc, chnum, edgenum, netcap]


def plotanaly(stats, d1=datetime(2018,1,1,12,0), d2=datetime(2018,10,20,12,0)):
    plt.rcParams.update({'font.size': 13})
    nodenum, isolate, cc, chnum, edgenum, netcap = stats[0], stats[1], stats[2], stats[3], stats[4], stats[5]
    days = [d1 + timedelta(days=x) for x in range((d2 - d1).days + 1)]
    date = [matplotlib.dates.date2num(day) for day in days]
    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
    ax.xaxis.set_minor_locator(matplotlib.dates.YearLocator())
    ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%Y'))
    ax.tick_params(pad=20)
    # ax.grid(True)
    ax.set_ylabel('Nodes')
    ax.plot(date, nodenum, 'k*', markersize=1, label='all')
    ax.plot(date, isolate, 'k+', markersize=1, label='isolated')
    ax.plot(date, cc, 'kx', markersize=1, label='biggest connected')
    ax.legend(fontsize='large', frameon=False)
    fig.tight_layout()
    plt.savefig('fig/nodes.png',dpi = 600)
    plt.show()
    fig1, ax1 = plt.subplots()
    ax1.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
    ax1.xaxis.set_minor_locator(matplotlib.dates.YearLocator())
    ax1.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%Y'))
    ax1.tick_params(pad=20)
    ax1.plot(date, chnum, 'k*', markersize=1, label='Channel')
    ax1.plot(date, edgenum, 'k+', markersize=1, label='Edge')
    ax2 = ax1.twinx()
    #ax2.set_ylabel('network capacity/BTC')
    ax2.plot(date, netcap, 'kx', markersize=1, label='Capacity/BTC', linestyle='--')
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines+lines2,labels+labels2, loc=0, fontsize='large', frameon=False)
    fig1.tight_layout()
    plt.savefig('fig/chcap.png',dpi = 600)
    plt.show()


def getdegree(nodes, channels, day=datetime(2018,12,22,12,0)):
    '''
    get degree list for fitting power law, dchannel is multi channel, dedge is single channel/number of nbr
    :param nodes: all List<Node>
    :param channels: all List<Channel>
    :param day:
    :return:
    '''
    gm = constructG(day, nodes, channels, 'Gmw')
    gmc = max(nx.connected_component_subgraphs(gm),key = len)
    dchannel = []
    dedge = []
    dedgec = []
    for n in gm:
        # dchannel.append(len(nx.edges(gm,n)))
        if len(gm[n]) != 0:
            dchannel.append(gm.degree(n))
            dedge.append(len(gm[n]))
    for n in gmc:
        dedgec.append(len(gmc[n]))
    return [dchannel, dedge, dedgec]


def pwlaw(degree):
    '''
    :param degree: List<List<Int>>, len=2
    :return: fitting and plot power line, return alpha
    '''
    deg = degree[1]
    # remove degree 0
    deg = list(filter(lambda a: a != 0, deg))
    sorteddeg = list(np.sort(deg))
    fit = powerlaw.Fit(sorteddeg)#alpha
    alpha = fit.alpha
    fit = powerlaw.Fit(sorteddeg, xmin=1)
    xdata = list(set(sorteddeg))
    ydata = [sorteddeg.count(l) for l in xdata]
    ydata = [y / sum(ydata) for y in ydata]
    fig, ax = plt.subplots()
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.scatter(xdata, ydata, s=9, marker='x', c='blue')
    #fit = powerlaw.Fit(x, discrete=True)
    #figCCDF = fit.plot_pdf(color='b', linewidth=2)
    fit.power_law.plot_pdf(color='black', linestyle='--', ax=ax)
    a, x = (fit.power_law.alpha, fit.power_law.xmin)
    minx, maxx = ax.get_xlim()
    miny, maxy = ax.get_ylim()
    ax.text(minx * 50, maxy / 8, r'$y \backsim x^{-2.06}$',fontsize=32)
    ax.set_xlim(1, 1000)
    ax.set_ylim(0.0001, 1)
    ax.set_xlabel('Degree', fontsize=22)
    ax.set_ylabel('Fraction', fontsize=20)
    plt.tick_params(labelsize=23)
    fig.tight_layout()
    plt.savefig('fig/logdegree.png', dpi=300)
    plt.show()
    return alpha


def getdegcdf(degree, edgeNum):
    '''
    :param degree:
    :param edgeNum: Int
    :return: return F(edgeNum), F is the cdf of channel numbers
    '''
    # channel exclude 0
    deg = degree[1]
    zeros = deg.count(0)
    res = list(filter(lambda a: a <= edgeNum, deg))
    cdf = (len(res)-zeros) / (len(deg) - zeros)
    return cdf


def plotdegcdf(degree):
    '''
    plot empirical cdf of degree distribution, exclude d = 0
    :param degree:
    '''
    deg = list(filter(lambda a: a != 0, degree[1]))
    # plt.plot(np.sort(deg), np.linspace(0, 1, len(deg)), endpoint=False)
    # sorteddeg = list(np.sort(deg))
    # d = set(sorteddeg)
    # cdf = [deg.count(l) for l in d]
    # cdf = np.transpose(np.cumsum(cdf))
    N = len(deg)
    X = np.sort(deg)
    F = (np.array(range(N))+1) / float(N)
    plt.plot(X, F,'k')
    # uncomment this line to get local graph
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>
    plt.xlim([1, 16])
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    plt.xlabel('Degree', fontsize=22)
    plt.ylabel('CDF', fontsize=22)
    # plt.xticks(fontsize=14)
    # plt.yticks(fontsize=14)
    plt.tick_params(labelsize=23)
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    fig = plt.gcf()
    fig.tight_layout()
    plt.savefig('fig/degreecdf.png', dpi=300)
    plt.show()

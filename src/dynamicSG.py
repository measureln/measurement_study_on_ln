from efficiency import *

# efficiency with time
# include diameter
def getEff(nodes, channels, day=datetime(2018, 12, 22, 12, 0)):
    g = constructG(day, nodes, channels,'Gw')
    gc = max(nx.connected_component_subgraphs(g), key=len)
    # alphas = np.arange(0,101,5)
    alphas = np.arange(0, 101, 20)
    N, plotNum = len(gc), len(alphas)
    efficiency, secondcc, isolates, diam = [], [], [], []
    amounts = percentileAmount(gc, alphas)
    for amount in amounts:
        print(amount)
        # h = gc.copy()
        removeEdge(gc, amount)
        qc = sorted(nx.connected_components(gc), key=len, reverse=True)
        eff = len(qc[0])/N
        efficiency.append(eff)
        print('1')
        dia = nx.diameter(gc.subgraph(qc[0]))
        print(dia)
        diam.append(dia)
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
    diam += temp1
    return [efficiency, secondcc, isolates, alphas, diam]


# 50% eff with time
def getTimeEff(nodes, channels, d1=datetime(2018,4,1,12,0), d2=datetime(2018,12,22,12,0)):
    dates = [d1 + timedelta(days=x) for x in range((d2 - d1).days + 1)]
    timeEff, timeDia = [], []
    for day in dates:
        g = constructG(day, nodes, channels, 'Gw')
        gc = max(nx.connected_component_subgraphs(g), key=len)
        alphas = [20, 50, 80]
        N = len(gc)
        efficiency, diam = [], []
        amounts = percentileAmount(gc, alphas)
        for amount in amounts:
            removeEdge(gc, amount)
            qc = sorted(nx.connected_components(gc), key=len, reverse=True)
            eff = len(qc[0]) / N
            efficiency.append(eff)
            dia = nx.diameter(gc.subgraph(qc[0]))
            print(dia)
            diam.append(dia)
        timeEff.append(efficiency)
        timeDia.append(diam)
    eff1 = [x[0] for x in timeEff]
    eff2 = [x[1] for x in timeEff]
    eff3 = [x[2] for x in timeEff]
    dia1 = [x[0] for x in timeDia]
    dia2 = [x[1] for x in timeDia]
    dia3 = [x[2] for x in timeDia]
    return [eff1, eff2, eff3, alphas, d1, d2, dia1, dia2, dia3]


def plotTimeEff2(data):
    eff1, eff2, eff3, alphas, dia1, dia2, dia3 = data[0], data[1], data[2], data[3], data[6], data[7], data[8]
    d1, d2 = data[4], data[5]
    days = [d1 + timedelta(days=x) for x in range((d2 - d1).days + 1)]
    date = [matplotlib.dates.date2num(day) for day in days]
    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
    ax.xaxis.set_minor_locator(matplotlib.dates.YearLocator())
    ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%Y'))
    ax.tick_params(pad=20)
    # ax.grid(True)
    ax.set_ylabel('Efficiency')
    ax.plot(date, eff1, 'k', markersize=1, label='30')
    ax.plot(date, dia1, 'k', marker='^', markersize=3, label='30d')
    ax.plot(date, eff2, 'b', markersize=1, label='50')
    ax.plot(date, dia2, 'b', marker='x', markersize=3, label='50d')
    ax.plot(date, eff3, 'r', markersize=1, label='80')
    ax.plot(date, dia3, 'r', marker='o', markersize=3, label='80d')
    ax.legend(fontsize='large', frameon=False)
    fig.tight_layout()
    plt.savefig('fig/efftime_n.png', dpi=300)
    plt.show()

#     use below
def plotTimeEff(data):
    eff1, eff2, eff3, alphas, dia1, dia2, dia3 = data[0], data[1], data[2], data[3], data[6], data[7], data[8]
    d1, d2 = data[4], data[5]
    days = [d1 + timedelta(days=x) for x in range((d2 - d1).days + 1)]
    date = [matplotlib.dates.date2num(day) for day in days]
    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
    ax.plot(date, eff1, 'r', label=r'$\beta = 20$')
    ax.plot(date, eff2, 'k', label=r'$\beta = 50$')
    ax.plot(date, eff3, 'b', label=r'$\beta = 80$')
    # ax.grid(True)
    plt.ylim([0, 1])
    ax.legend(fontsize=18, frameon=False)
    ax.set_ylabel('Routing efficiency', fontsize=22)
    plt.tick_params(labelsize=18)
    fig.tight_layout()
    plt.savefig('fig/efftime2.png', dpi=300)
    plt.show()

#     bin chart
def plotTimeLQC(data):
    eff1, eff2, eff3, alphas, dia1, dia2, dia3 = data[0], data[1], data[2], data[3], data[6], data[7], data[8]
    d1, d2 = data[4], data[5]
    days = [d1 + timedelta(days=x) for x in range((d2 - d1).days + 1)]
    date = [matplotlib.dates.date2num(day) for day in days]
    # fig, ax = plt.subplots()
    # ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    # ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
    # # ax.grid(True)
    # ax.plot(date, eff1, 'r', label=r'$\beta = 20$')
    # ax.plot(date, eff2, 'k', label=r'$\beta = 50$')
    # ax.plot(date, eff3, 'b', label=r'$\beta = 80$')
    # plt.ylim([0, 1])
    # ax.legend(fontsize=23, frameon=False)
    # ax.set_ylabel('Routing efficiency', fontsize=24)
    # plt.tick_params(labelsize=18)
    # fig.tight_layout()
    # plt.savefig('fig/efftime.png', dpi=300)
    # plt.show()
    fig1, ax1 = plt.subplots()
    ax1.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
    plt.bar(date, dia1, label=r'$\beta = 20$')
    plt.bar(date, dia2, label=r'$\beta = 50$')
    plt.bar(date, dia3, label=r'$\beta = 80$')
    # plt.bar(date, dia1, label=r'$\beta = 20$', color='black')
    # plt.bar(date, dia2, label=r'$\beta = 50$', color='orange')
    # plt.bar(date, dia3, label=r'$\beta = 80$', color='blue')
    plt.ylim([5, 14])
    ax1.legend(fontsize=18, frameon=False)
    ax1.set_ylabel(r'Routing $LQC$ diameter', fontsize=24)
    plt.tick_params(labelsize=18)
    fig1.tight_layout()
    plt.savefig('fig/efflqctime.png', dpi=300)
    plt.show()

# robust with time
def getTimeRobust(nodes, channels, nodeRank, d1=datetime(2018,4,1,12,0), d2=datetime(2019,4,1,12,0)):
    dates = [d1 + timedelta(days=x) for x in range((d2 - d1).days + 1)]
    timeCap, timeSize = [], []
    for day in dates:
        g = constructG(day, nodes, channels, 'Gw')
        gc = max(nx.connected_component_subgraphs(g), key=len)
        n = gc.number_of_nodes()
        removeNum = [0, 0.01, 0.05, 0.1]
        removeNum = [int(i*n) for i in removeNum]
        cap, size = [], []
        weights = sum([w for u, v, w in g.edges(data='weight')])
        for i in range(len(removeNum) - 1):
            removenodes = [x[0] for x in nodeRank[removeNum[i]:removeNum[i + 1]]]
            gc.remove_nodes_from(removenodes)
            newweights = sum([wt for u, v, wt in gc.edges(data='weight')])
            cap.append(newweights / weights)
            size.append(len(max(nx.connected_component_subgraphs(gc), key=len)) / n)
        timeCap.append(cap)
        timeSize.append(size)
    # cap1 remove = 0.01
    cap1 = [x[0] for x in timeCap]
    cap2 = [x[1] for x in timeCap]
    cap3 = [x[2] for x in timeCap]
    size1 = [x[0] for x in timeSize]
    size2 = [x[1] for x in timeSize]
    size3 = [x[2] for x in timeSize]
    return[cap1, cap2, cap3, size1, size2, size3, d1, d2, removeNum]


def plotTimeRobust(data):
    cap1, cap2, cap3, size1, size2, size3, d1, d2 = data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]
    days = [d1 + timedelta(days=x) for x in range((d2 - d1).days + 1)]
    date = [matplotlib.dates.date2num(day) for day in days]
    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
    # ax.tick_params(pad=20)
    # bin
    ax.set_ylabel('Network Capacity', fontsize=24)
    plt.bar(date, cap1, label=r'$\gamma = 0.01$')
    plt.bar(date, cap2, label=r'$\gamma = 0.05$')
    plt.bar(date, cap3, label=r'$\gamma = 0.1$')
    ax.legend(fontsize=17, frameon=False)
    plt.tick_params(labelsize=18)
    fig.tight_layout()
    plt.savefig('fig/captime.png', dpi=300)
    plt.show()
    fig1, ax1 = plt.subplots()
    ax1.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
    ax1.set_ylabel(r'$LCC$ size', fontsize=24)
    ax1.plot(date, size1, 'k', label=r'$\gamma = 0.01$')
    ax1.plot(date, size2, 'b', label=r'$\gamma = 0.05$')
    ax1.plot(date, size3, 'r', label=r'$\gamma = 0.1$')
    ax1.legend(fontsize=18, frameon=False)
    plt.tick_params(labelsize=18)
    fig1.tight_layout()
    plt.savefig('fig/sizetime.png', dpi=300)
    plt.show()
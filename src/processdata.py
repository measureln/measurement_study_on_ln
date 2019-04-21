from datetime import date,datetime, timedelta


class Node:
    def __init__(self, id, alias, pubkey, jointime):
        self.id = id
        self.alias = alias
        self.pubkey = pubkey
        self.jointime = jointime

class Channel:
    def __init__(self, lst):
        self.id = lst[0]
        self.node1 = lst[1]
        self.node2 = lst[2]
        self.capacity = lst[3]
        self.opentime = lst[4]
        self.openfee = lst[5]
        self.closetime = lst[6]
        self.closefee = lst[7]

# not key-value pair, hard to index
def readNode(file, observeday = date(2019, 4, 11)):
    '''read all nodes from robtex_node_discovered
    :rtype list[Node]
    '''
    nodes = []
    with open(file,'r') as f:
        temp = f.readlines()
    temp.pop(0)
    nodelist = [l.strip('\n') for l in temp]
    # nodelist = [l.split(sep='\t')[:-1] for l in nodelist]
    nodelist = [l.split(sep='\t') for l in nodelist]
    for node in nodelist:
        # print(node)
        node[3] = node[3].split(sep = ':')[1].split()[0]
        node[3] = observeday - timedelta(days=int(node[3]))
        nd = Node(int(node[0]), node[1], node[2], node[3])
        nodes.append(nd)
    return nodes


def filterNode(nodes, snapday = date(2019,4,1)):
    '''return a new list of nodes that joined b
    efore snapday
    ***fix***
    should not include nodes who has no channel before snapday--testnet
    :rtype list[Node]
    '''
    validnodes = []
    for node in nodes:
        if node.jointime <= snapday:
            validnodes.append(node)
    return validnodes


def indexNode(nodes):
    '''easier to search node
    :rtype map<k:nodeid, v:Node>
    '''
    nodemap = {}
    for node in nodes:
        nodemap[node.pubkey] = node
    return nodemap


def readChannel(file):
    with open(file,'r') as f:
        temp = f.readlines()
    temp.pop(0)
    channellist = [l.strip('\n') for l in temp]
    channellist = [l.split(sep = '\t') for l in channellist]
    return channellist


def buildChannel(channellist, nodemap):
    '''
    :rtype: list<Channel>
    '''
    clist = []
    for cl in channellist:
        print(cl[0],'here')
        # obtain opentime
        otemp = cl[7].split(sep='_')
        oday, otime = otemp[0], otemp[1]
        ot = datetime(int(oday.split(sep='-')[0]), int(oday.split(sep='-')[1]), int(oday.split(sep='-')[2]),
                      int(otime.split(sep=':')[0]), int(otime.split(sep=':')[1]))
        ofee = float(cl[8])
        # obtain close time
        if cl[10] != 'None':
            ctemp = cl[10].split(sep='_')
            cday, ctime = ctemp[0], ctemp[1]
            print(cl[0],cday,ctime)
            ct = datetime(int(cday.split(sep='-')[0]), int(cday.split(sep='-')[1]), int(cday.split(sep='-')[2]),
                          int(ctime.split(sep=':')[0]), int(ctime.split(sep=':')[1]))
            cfee = float(cl[11])
        else:
            ct = 'None'
            cfee = 'None'
        try:
            # nodes in channel.txt but not in node.txt, possibly new node
            node1, node2 = nodemap[cl[1]], nodemap[cl[3]]
            # update node join time if channel open time is earlier than node join time
            ########################################################################
            od = date(int(oday.split(sep='-')[0]), int(oday.split(sep='-')[1]), int(oday.split(sep='-')[2]))
            if od < node1.jointime:
                node1.jointime = od
            if od < node2.jointime:
                node2.jointime = od
            ########################################################################
        except:
            continue
        #     make sure node1.id < node2.id
        if node1.id > node2.id:
            node1, node2 = node2, node1
        capacity = float(cl[5])
        channel = Channel([cl[0], node1, node2, capacity, ot, ofee, ct, cfee])
        clist.append(channel)
    return clist


def filterChannel(chlist, snaptime = datetime(2019,4,1,12,0)):
    '''return a new list of channel that is active at snaptime
    :chlist: List<Channel>
    :rtype: List<Channel>
    '''
    activechannel = []
    for channel in chlist:
        if channel.opentime <= snaptime:
            if channel.closetime == 'None' or channel.closetime >= snaptime:
                activechannel.append(channel)
    return activechannel


def getEdge(channels):
    '''
    get all edge info for building graph
    :param channels: list<Channel>
    :return: List<Set<'node1id','node2id',Map<k:chID, weight...>>>
    '''
    edges = []
    for channel in channels:
        edgeattri = dict([['chID', channel.id],['weight', channel.capacity], ['open', channel.opentime],
                          ['openfee', channel.openfee],['close',channel.closetime],['closefee', channel.closefee]])
        edge = (int(channel.node1.id), int(channel.node2.id), edgeattri)
        edges.append(edge)
    return edges


def getPairChannel(channels):
    '''
    get a list of all channels between all node pairs for communication
    :param channels: List<Channel>
    :return: Map<k:(node1id, node2id), v:List<Channel>>
    '''
    pairs = {}
    for channel in channels:
        u, v = channel.node1.id, channel.node2.id
        if (u, v) in pairs:
            pairs[(u, v)].append(channel)
        else:
            pairs[(u, v)] = [channel]
    return pairs

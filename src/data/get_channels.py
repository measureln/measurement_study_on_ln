from selenium import webdriver


class Channel():
        ID = None
        node1 = 'None'
        node2 = 'None'
        alias1 = 'None'
        alias2 = 'None'
        capacity = 'None'
        openfee = 'None'
        opentx = None
        opentime = 'None'
        closetx = 'None'
        closetime = 'None'
        closefee = 'None'
        discovertime = 'None'
        lastseen = 'None'
        lastupdate = 'None'
        lock1 = 'None'
        lock2 = 'None'


def get_urls():
    with open(dirname + '/'+'robtex_nodelink_4.4.txt', 'r') as f1:
    # with open(dirname + '/'+'testnodelink.txt', 'r') as f1:
        temp = f1.readlines()
    url_list = [l.strip('\n') for l in temp]
    f1.close()
    return url_list


def saveFile(filename, channellist):
    with open(filename,'w') as f2:
        f2.write('channelID'+'\t'+'node1'+'\t'+'alias1'+'\t'+'node2'+'\t'+'alias2'+'\t'+
                 'capacity'+'\t'+'opentx'+'\t'+'opentime'+'\t'+'openfee'+'\t'+'closetx'+
                 '\t'+'closetime'+'\t'+'closefee'+'\t'+'discovertime'
                 + '\t' +'lastseen'+'\t'+'lastupdate'+'\t'+'lock1'+'\t'+'lock2'+'\n')
        for channel in channellist:
            f2.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.
                     format(channel.ID, channel.node1, channel.alias1, channel.node2, channel.alias2, channel.capacity,
                     channel.opentx, channel.opentime, channel.openfee,
                     channel.closetx, channel.closetime, channel.closefee,
                     channel.discovertime,channel.lastseen, channel.lastupdate,channel.lock1, channel.lock2))


def savechidList(filename, channelid):
    with open(filename, 'w') as f3:
        for ch in channelid:
            f3.write('https://hashxp.org/lightning/channel/{}\n'.format(ch.ID))


def get_channels(urlist, filename):
    channellist  = []
    cIDlist = []
    f3 = open(filename, 'a')
    print('Start getting channel ID...')
    browser = webdriver.PhantomJS()
    browser.implicitly_wait(35)
    for url in urlist:
        print(url)
        browser.get(url+'?old=1')#containing closed channel
        #browser.implicitly_wait(5)
        elements = browser.find_elements_by_class_name('lnctab')
        for element in elements:
            channel = Channel()
            lists = element.text.split(sep='\n')
            channelID = lists[7].split()[2]
            channel.ID = channelID
            print('current channel',channelID)
            if channelID not in cIDlist:
                if len(channelID) == 18 and channelID[0] != 't':
                    channellist.append(channel)
                    f3.write('https://hashxp.org/lightning/channel/{}\n'.format(channelID))
                    print('valid unique channel',channelID)
                cIDlist.append(channelID) #filter duplex channel
    print('Finish getting channel ID...')
    # savechidList(dirname + '/' + 'robtex_channelId_1017.txt', channellist)
    browser.quit()
    f3.close()
    return channellist


def search_channels(channellist, foname):
    print('Start searching channels...')
    f2 = open(foname,'a')
    f2.write('channelID' + '\t' + 'node1' + '\t' + 'alias1' + '\t' + 'node2' + '\t' + 'alias2' + '\t' + 'capacity' + '\t'
             + 'opentx' + '\t' + 'opentime' + '\t' + 'openfee' + '\t' + 'closetx' + '\t' + 'closetime' + '\t' + 'closefee' + '\t'
             + 'discovertime' + '\t' + 'lastseen' + '\t' + 'lastupdate' + '\t' + 'lock1' + '\t' + 'lock2' + '\n')
    browser = webdriver.PhantomJS()
    browser.implicitly_wait(35)
    for channel in channellist:
        channel_url = 'https://hashxp.org/lightning/channel/'+ channel.ID
        browser.get(channel_url)
        #browser.implicitly_wait(5)
        element = browser.find_elements_by_xpath('//tbody/tr')
        num = len(element)

        for i in range(num):#using if allows that there is no such item on the webpage
            index = element[i].text.split()
            if index[0] == 'Capacity':
                channel.capacity = index[2]
            elif index[0] == 'Opened':
                channel.opentime = index[1]+'_'+index[2]
                try:
                    channel.openfee = index[4]
                except:
                    pass
            elif index[0] == 'Closed':
                try:
                    channel.closetime = index[1]+'_'+index[2]
                    channel.closefee = index[4]
                    print(channel.ID,'closed at',channel.closetime)
                except:
                    print(channel.ID,'is active channel')
            elif index[0] == 'Discovered':
                channel.discovertime = index[1]+'_'+index[2]
            elif index[0] == 'Last':
                if index[1] == 'seen':
                    try:
                        channel.lastseen = index[2]+'_'+index[3]
                    except:
                        print(channel.ID,'no last seen time')
            #elif index[0]+index[1] == 'Lastupdate':
                if index[1] == 'update':
                    try:
                        channel.lastupdate = index[2]+'_'+index[3]
                    except:
                        print(channel.ID,'no last update time')
            elif index[0] == 'Open':
                if index[1] == 'TX':
                    channel.opentx = index[2]
                if index[1] == 'Addrs':
                    channel.address = index[2]
            elif index[0] == 'Close':
                if index[1] == 'TX':
                    try:
                        channel.closetx = index[2]
                    except:
                        pass
            elif index[0] == 'id':
                if channel.node1 == 'None':
                    channel.node1 = index[1]
                else:
                    channel.node2 = index[1]
            elif index[0] == 'alias':
                if channel.alias1 == 'None':
                    channel.alias1 = index[1]
                else:
                    channel.alias2 = index[1]
            elif index[0] == 'Time':
                if channel.lock1 == 'None':
                    try:
                        channel.lock1 = index[3]
                    except:
                        channel.lock1 = 'none'
                else:
                    try:
                        channel.lock2 = index[3]
                    except:
                        channel.lock2 = 'none'
            else:
                pass
        f2.write(
            '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(channel.ID, channel.node1,channel.alias1,
            channel.node2, channel.alias2, channel.capacity, channel.opentx, channel.opentime, channel.openfee,channel.closetx,
            channel.closetime, channel.closefee, channel.discovertime, channel.lastseen, channel.lastupdate,channel.lock1, channel.lock2))
    f2.close()
    return channellist


if __name__ == '__main__':
    dirname = 'robtex_0404'
    urls = get_urls()  # We pass urls to getchannels in__init__. If we want to obtain urls outisde __init__, we need to def self.urls
    chidlist = get_channels(urls, dirname + '/' + 'robtex_channelId_0404.txt')#write to file
    chlist = search_channels(chidlist, dirname + '/' + 'robtex_channel_0404.txt')
    # saveFile(dirname + '/' + 'robtex_channel_1017.txt',chlist)
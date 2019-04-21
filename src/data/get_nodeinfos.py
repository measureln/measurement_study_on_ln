from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import os

def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

url = 'https://hashxp.org/lightning/node/'
nodelist = []
dirname = 'robtex_0404'
mkdir(dirname)
filename = dirname + '/'+'robtex_nodediscovered_4.4.txt'
f = open(filename, 'w')
f.write('index\talias\tpubkey\tdiscover\tlast update\n')

browser = webdriver.PhantomJS()
browser.get(url)
browser.implicitly_wait(5)

elements = browser.find_element_by_class_name('lnconn')
links = elements.find_elements_by_tag_name('a')
i = 1
for link in links:
    temp = link.text.split(sep = '\n')
    nodelist.append([i,temp[0],temp[1],temp[2],temp[3]])
    print(i, temp[0])
    i = i+1

browser.quit()
for node in nodelist:
    f.write('{}\t{}\t{}\t{}\t{}\n'.format(node[0],node[1],node[2],node[3],node[4]))

f.close()
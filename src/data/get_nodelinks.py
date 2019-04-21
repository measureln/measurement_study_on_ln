from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import os
# get link of all nodes
def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

# url = 'https://www.robtex.com/lightning/node/'
url = 'https://hashxp.org/lightning/node/'
# url_list = []
# nodeID_list = []
dirname = 'robtex_0404'
mkdir(dirname)
filename = dirname + '/'+'robtex_nodelink_4.4.txt'
f = open(filename, 'w')

browser = webdriver.PhantomJS()
browser.get(url)
browser.implicitly_wait(5)

elements = browser.find_element_by_class_name('lnconn')
links = elements.find_elements_by_tag_name('a')
for link in links:
    nodehref = link.get_attribute('href')
    # url_list.append(nodehref)
    # nodeID_list.append(nodehref.split(sep = '/')[-1])
    f.write(nodehref+'\n')

browser.quit()
f.close()


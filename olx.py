import copy
import random
import socket
import sys
import time
import unicodedata
import urllib
from subprocess import call
import pandas as pd

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

    
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from IPython.display import Image, display
import requests
import re
from time import sleep

def randdelay(a, b):
    time.sleep(random.uniform(a, b))


def u_to_s(uni):
    return unicodedata.normalize('NFKD', uni).encode('ascii', 'ignore')


class PinterestHelper(object):

    def __init__(self, download=False):
#         self.download = download
#         # self.browser = webdriver.Firefox()
        self.browser = webdriver.Chrome()
#         self.browser.get("https://www.pinterest.com")
#         login_btn = self.browser.find_element_by_class_name("RCK")
#         login_btn.click()
#         email, password = self.browser.find_element_by_id("email"), self.browser.find_element_by_id("password")
#         email.send_keys(login)
#         password.send_keys(pw)
#         password.send_keys(Keys.RETURN)
#         randdelay(2, 4)

    def runme(self, url, threshold=10):
        final_results = []
        previmages = []
        tries = 0
        data=pd.read_csv('images.csv')
        try:
            self.browser.get(url)
            while threshold > 0:
                try:
                    results = []
                    for i in range(10):
#                         try:
                        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                        sleep(3)
                        btn=self.browser.find_element_by_class_name("rui-3sH3b.rui-3K5JC.rui-1zK8h")
                        btn.click()
#                         except:
#                             return final_results
                    images = self.browser.find_elements_by_tag_name("img")
                    if images == previmages:
                        tries+=1
                    else:
                        tries = 0
                    if tries > 1:
                        return final_results
                    for i in images:
                        if i in previmages:
                            continue
                        src = i.get_attribute("src")
#                         if src:
#                             if src.find("/236x/") != -1 or src.find("/474x/") != 1:
#                                 # print(src)
#                                 src = src.replace("/236x/", "/736x/")
#                                 src = src.replace("/474x/", "/736x/")
                        src=re.sub(';s=.*$','',src)
                        if src in data['urls']:
                            continue
                        display(Image(requests.get(src).content,width=200,height=200))
                        res=input()
                        if (res=='1'):
                            results.append(src)
                        if(res=='2'):
                            final_results = list(set(final_results + results))
                            return final_results
                    previmages = copy.copy(images)
                    final_results = list(set(final_results + results))
                    print(len(final_results))
                    out=pd.DataFrame({'urls':final_results})
                    out.to_csv('images.csv',mode='a',index=False,header=False)
                    # if(len(final_results)>100):
                    #     return final_results
                    # dummy = self.browser.find_element_by_tag_name('a')
                    # dummy.send_keys(Keys.PAGE_DOWN)
                    randdelay(0, 1)
                    threshold -= 1
                except StaleElementReferenceException:
                    threshold -= 1
#                     return final_results
        except (socket.error, socket.timeout):
            pass
        return final_results

    def close(self):
        """ Closes the browser """
        self.browser.close()

def main(url):
    ph = PinterestHelper()
#     data=pd.read_csv('urls.csv')
    images = ph.runme(url)
    ph.close()
    out=pd.DataFrame({'urls':images})
    out.to_csv('images.csv',mode='a',index=False,header=False)
    print(len(images))

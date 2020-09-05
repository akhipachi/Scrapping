#!/usr/bin/env python3
# coding: utf-8
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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

try:
    from config_sample import PINTEREST_PASSWORD, PINTEREST_USERNAME
except Exception as e:
    print(e)


def randdelay(a, b):
    time.sleep(random.uniform(a, b))


def u_to_s(uni):
    return unicodedata.normalize('NFKD', uni).encode('ascii', 'ignore')


class PinterestHelper(object):

    def __init__(self, login, pw, download=False):
        self.download = download
        # self.browser = webdriver.Firefox()
        self.browser = webdriver.Chrome()
        self.browser.get("https://www.pinterest.com")
        login_btn = self.browser.find_element_by_class_name("RCK")
        login_btn.click()
        email, password = self.browser.find_element_by_id("email"), self.browser.find_element_by_id("password")
        email.send_keys(login)
        password.send_keys(pw)
        password.send_keys(Keys.RETURN)
        randdelay(2, 4)

    def runme(self, url, threshold=500):
        final_results = []
        previmages = []
        tries = 0
        try:
            self.browser.get(url)
            while threshold > 0:
                try:
                    results = []
                    images = self.browser.find_elements_by_tag_name("img")
                    if images == previmages:
                        tries += 1
                    else:
                        tries = 0
                    if tries > 3:
                        return final_results
                    for i in images:
                        src = i.get_attribute("src")
                        if src:
                            if src.find("/236x/") != -1 or src.find("/474x/") != 1:
                                # print(src)
                                src = src.replace("/236x/", "/736x/")
                                src = src.replace("/474x/", "/736x/")
                                results.append(src)

                    previmages = copy.copy(images)
                    final_results = list(set(final_results + results))
                    print(len(final_results))
                    # if(len(final_results)>100):
                    #     return final_results
                    self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                    # dummy = self.browser.find_element_by_tag_name('a')
                    # dummy.send_keys(Keys.PAGE_DOWN)
                    randdelay(0, 1)
                    threshold -= 1
                except StaleElementReferenceException:
                    threshold -= 1
        except (socket.error, socket.timeout):
            pass
        return final_results

    def close(self):
        """ Closes the browser """
        self.browser.close()


def main():
    ph = PinterestHelper(PINTEREST_USERNAME, PINTEREST_PASSWORD)
    data=pd.read_csv('urls.csv')
    images = ph.runme('https://in.pinterest.com/houseinkerala/kerala-home-elevations/')
    ph.close()
    out=pd.DataFrame({'urls':images})
    out.to_csv('images.csv',mode='a',index=False,header=False)
    print(len(images))
    

if __name__ == '__main__':
    main()

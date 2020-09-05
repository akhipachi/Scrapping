from selenium import webdriver
import json
from time import time, sleep
from tqdm import tqdm
from copy import deepcopy
from random import randint
import numpy as np
import pandas as pd
import sys
import os
def fetch_image_urls(max_links_to_fetch=150, wd=None, sleep_between_interactions=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # time.sleep(sleep_between_interactions)    
    
    # build the google query
    search_url = 'https://www.google.com/search?q=houses&tbm=isch&tbs=rimg%3ACXZcVZITN9hSYWRZ8QDbxPpY&rlz=1C1CHBF_enIN899IN899&hl=en-GB&sa=X&ved=0CBwQuIIBahcKEwjgrNCC687rAhUAAAAAHQAAAAAQBg&biw=1349&bih=625'

    # load the page
    wd.get(search_url)

    image_urls = set()
    image_count = 0
    results_start = 0
    similar=[]
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            try:
                more=wd.find_elements_by_css_selector('a.So4Urb.lxa62b.MIdC8d')
                similar.append(more[0].get_attribute('href'))
            except:
                print(len(image_urls))
            for actual_image in actual_images:
                urs = actual_image.get_attribute('src')
                if urs.find("http")<0 or urs.find("https") or urs.find("encrypted")>0:
                    continue
                else:
                    image_urls.add(urs)
                    break
                # if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                #     image_urls.add(actual_image.get_attribute('src'))
                #     break
            

            image_count = len(image_urls)

        if len(image_urls) >= max_links_to_fetch:
            print(f"Found: {len(image_urls)} image links, done!")
            break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            wd.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(10)
            

        # move the result startpoint further down
        results_start = len(thumbnail_results)
    return image_urls,similar
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-certificate-error')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--ignore-certificate-errors-spki-list')
driver=webdriver.Chrome(chrome_options=options)
images,similar=fetch_image_urls(wd=driver)
out=pd.DataFrame({'urls':list(images)})
out.to_csv('images_new.csv',mode='a',index=False,header=False)
links=pd.DataFrame({'urls':similar})
links.to_csv('urls.csv',mode='a',index=False,header=False)
driver.close()

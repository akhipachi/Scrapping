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
def fetch_image_urls(max_links_to_fetch=150, wd=None, sleep_between_interactions=1,data=pd.read_csv('urls.csv')):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(sleep_between_interactions)
        
    image_urls = set() # main set containing the image urls
    similar=[]    
    for i in range(len(data)):
        
        # build the google query
        search_url = data['urls'][i]
        
        # declaring the variables
        results_start = 0
        image_count = 0
        
        # load the page
        wd.get(search_url)

        # validate the page
        res=input()
        if(res=='1'):
            data=data.drop(i)
            continue
        if(res=='2'):
            break

        #extracting the thumbnails
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
                    
                    #validaring the url
                    if urs.find("http")<0 or urs.find("https") or urs.find("encrypted")>0:
                        continue
                    else:
                        image_urls.add(urs)
                        break
                

            # checking the required quantity
            image_count = len(image_urls)
            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                # print('index'+str(i)+'done')
                break
            else:
                print("Found:", len(image_urls), "image links, looking for more ...")
                wd.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                sleep(3) 
            # move the result startpoint further down
            results_start = len(thumbnail_results)

        # droping the scrapped urls
        data=data.drop(i)
    
    data.to_csv('urls.csv',index=False)
    return image_urls,similar

# building the driver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-certificate-error')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--ignore-certificate-errors-spki-list')
driver=webdriver.Chrome(chrome_options=options)

# scapping
images,similar=fetch_image_urls(wd=driver)

#saving the results
out=pd.DataFrame({'urls':list(images)})
out.to_csv('images_new.csv',mode='a',index=False,header=False)
links=pd.DataFrame({'urls':similar})
links.to_csv('urls.csv',mode='a',index=False,header=False)

driver.close()

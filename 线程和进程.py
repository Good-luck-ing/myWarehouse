# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 12:06:12 2020

@author: 29620
"""

import re
import requests
from fake_useragent import UserAgent
import time
import concurrent
import threading
from multiprocessing.pool import Pool

#装饰器，计算运行时间
def gettime(func):
    def warapper(*args,**kwargs):
        print("-"*30)
        print(func.__name__,"start...")
        starttime = time.time()
        func(*args)
        endtime = time.time()
        spendtime = endtime - starttime
        print(func.__name__,"end...")
        print("spend",spendtime,"a totally")
        print("-"*30)
    return warapper

#获取大量网址
def getwz():
    url = "https://www.hao123.com"
    ua = UserAgent(verify_ssl=True)
    headers = {"user-agent":ua.random}
    resp = requests.get(url, headers)
    data = resp.text
    urls= re.findall(r'href="(http.*?)"', data)
    urls = urls[4:104]
    return urls


#请求网址，获取数据
def getdata(url):
    ua = UserAgent(verify_ssl=True)
    headers = {"user-agent":ua.random}
    try:
        html = requests.get(url,headers=headers)
    except Exception as e:
        html = None

#串行
@gettime
def mynormal(urls):
    for url in urls:
        getdata(url)

#进程池
@gettime
def myprocesspool(urls,num = 5):
    pool = Pool(num)
    result = pool.map(getdata, urls)
    pool.close()
    pool.join()
    return result

#多线程
@gettime
def mymultithread(urls,max_thread = 5):
    def urls_process():
        while True:
            try:
                url = urls.pop()
            except IndexError as e:
                break
            getdata(url)
    threads = []
    while int(len(threads)<max_thread):
        thread = threading.Thread(target = urls_process)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
     
        
#线程池
@gettime
def myfutures(urls, num_of_max_max_workers = 5):
    with concurrent.futures.ThreadPoolExecutor(max_workers = num_of_max_max_workers) as executor:
        executor.map(getdata, urls)
        executor.shutdown(wait=True)    

if __name__ == "__main__":
    urls = getwz()
    mynormal(urls)
    myprocesspool(urls)
    #注意mymultithread方法和myfutures方法顺序，因urls.pop()原因mymultithread方法一定在最后
    myfutures(urls)
    mymultithread(urls)
    
    
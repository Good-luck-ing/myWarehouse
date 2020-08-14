# -*- coding: utf-8 -*-
"""
Created on Fri May 29 17:37:22 2020

@author: 29620
"""
import threading#线程
import requests
from lxml import etree#解析库
from urllib import request
import os
import re
from queue import Queue #队列


#--------------------------------生产者------------------------------------
class Producer(threading.Thread):
    #请求头
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }
        #初始化
        def __init__(self,page_queue,img_queue,*args,**kwargs):
            super(Producer, self).__init__(*args,**kwargs)
            self.page_queue = page_queue
            self.img_queue = img_queue
    
    
        def run(self):
            while True:
                if self.page_queue.empty():
                    break
                url = self.page_queue.get()
                self.parse_page(url)
    
        def parse_page(self,url):
            response = requests.get(url,headers=self.headers)
            text = response.text
            html = etree.HTML(text)
            print(html)
            imgs = html.xpath("//div[@class='page-content text-center']//a//img")
            for img in imgs:
                if img.get('class') == 'gif':
                    continue
                img_url = img.xpath(".//@data-original")[0]
                suffix = os.path.splitext(img_url)[1]
                alt = img.xpath(".//@alt")[0]
                
                alt = re.sub(r'[，。？?,/\\·]','',alt)
                img_name = alt + suffix
                self.img_queue.put((img_url,img_name))

#--------------------------------消费者------------------------------------   
class Consumer(threading.Thread):
        def __init__(self,page_queue,img_queue,*args,**kwargs):
            super(Consumer, self).__init__(*args,**kwargs)
            self.page_queue = page_queue
            self.img_queue = img_queue
    
        def run(self):
            while True:
                if self.img_queue.empty():
                    if self.page_queue.empty():
                        return
                img = self.img_queue.get(block=True)
                url,filename = img
                request.urlretrieve(url,r'D:\WorkRegion\pachong/'+filename)
                print(filename+'  下载完成！')
    
def main():
    #---------构造队列------------------
    page_queue = Queue(100)
    img_queue = Queue(500)
    #-----------------------------------
    for x in range(1,2):
        url = "http://www.doutula.com/photo/list/?page=%d" % x
        #添加url到page队列中
        page_queue.put(url)
    
    #循环5个生产者线程
    for x in range(5):
        t = Producer(page_queue,img_queue)
        t.start()
    #循环5个消费者线程
    for x in range(5):
        t = Consumer(page_queue,img_queue)
        t.start()
    
if __name__ == '__main__':
     main()


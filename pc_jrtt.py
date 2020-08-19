#利用ajax抓取微博
import requests #请求库
from fake_useragent import UserAgent #伪装ua
import pandas as pd #分析包
from queue import Queue #队列
from pyquery import PyQuery as pq

page_queue = Queue(100)#构造长度100的id队列
pl_queue = Queue(100)#构造长度100的评论量队列
ua = UserAgent()
headers = ua.random
url = "" #填写目标微博地址
url_ajax = "https://m.weibo.cn/api/container/getIndex?type=uid&value=xxxxx&containerid=xxxxx4&page=1"#分析ajax
requests.get(url, headers)
html = requests.get(url_ajax, headers)
html2 = html.json()
#id
id = []
for item in html2.get('data').get("cards"):
    id.append(item.get('mblog').get("id"))
    page_queue.put(item.get('mblog').get("id"))#将id添加到消息队列
#是否原创
original_reprint= ["原创" if item.get('mblog').get("retweeted_status")==None else "转载" for item in html2.get('data').get("cards")]
#判断原创/转载
Original_text = [] #微博原创正文
Original_pictures = [] #原创图片
Original_attitudes = [] #点赞量
Original_comment = [] #评论量
#------------------------------------------------------------------------------------------------------------------------
Reprint_text = [] #微博转载正文
Reprint_pictures = [] #转载图片
Reprint_attitudes = [] #转载点赞量
Reprint_comment = [] #转载评论量
for i in html2.get('data').get("cards"):
    #原创
    if i.get('mblog').get("retweeted_status") == None:
        if i.get('mblog').get("pic_num") == 0:
            Original_pictures.append("无图片")
        else:
            Original_pictures.append([one.get('url') for one in i.get('mblog').get("pics")])
        Original_attitudes.append(i.get('mblog').get("attitudes_count"))
        Original_comment.append(i.get('mblog').get("comments_count"))
        pl_queue.put(i.get('mblog').get("comments_count"))  # 将评论量添加到消息队列
        Original_text.append(i.get('mblog').get("raw_text"))
        Reprint_pictures.append("")
        Reprint_text.append("")
        Reprint_attitudes.append("")
        Reprint_comment.append("")
    #转载
    else:
        if i.get('mblog').get("retweeted_status").get('pic_num') == 0:
            Reprint_pictures.append("无图片")
        else:
            Reprint_pictures.append([two.get('url') for two in i.get('mblog').get("retweeted_status").get('pics')])
        Reprint_text.append(i.get('mblog').get("retweeted_status").get("raw_text"))
        Reprint_attitudes.append(i.get('mblog').get("retweeted_status").get("attitudes_count"))
        Reprint_comment.append(i.get('mblog').get("retweeted_status").get("comments_count"))
        Original_text.append(i.get('mblog').get("raw_text"))
        Original_pictures.append("")
        Original_attitudes.append(i.get('mblog').get("attitudes_count"))
        Original_comment.append(i.get('mblog').get("comments_count"))
        pl_queue.put(i.get('mblog').get("comments_count"))  # 将评论量添加到消息队列
#解析第二层ajax链接
pl_id = [] #评论人id
pl_name = [] #评论人name
pl_text = [] #评论人正文
hf_id = [] #评论人id
hf_name = [] #回复人name
hf_text = [] #回复人正文
while True:
    try:
        nub = pl_queue.get(block=False)
        mid = page_queue.get(block=False)
        if nub != 0:
            url_ajax2 = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0'.format(mid, mid)
            html3 = requests.get(url_ajax2, headers)
            html4 = html3.json()
            pl_id.append([i.get("user").get('id') for i in html4.get('data').get('data')])
            pl_name.append([i.get("user").get('screen_name') for i in html4.get('data').get('data')])
            pl_text.append([pq(i.get("text")).text() for i in html4.get('data').get('data')])
            hf_id.append([k.get("user").get('id')  for i in html4.get('data').get('data') if i.get("comments") for k in i.get("comments")])
            hf_name.append([k.get("user").get('screen_name')  for i in html4.get('data').get('data') if i.get("comments") for k in i.get("comments")])
            hf_text.append([pq(k.get("text")).text()for i in html4.get('data').get('data') if i.get("comments") for k in i.get("comments")])
        else:
            pl_id.append(None)
            pl_name.append(None)
            pl_text.append(None)
            hf_id.append(None)
            hf_name.append(None)
            hf_text.append(None)
            continue
    except Exception as e:
        print(e)
        break
keep_date = pd.DataFrame()
keep_date["id"] = id
keep_date["是否原创"] = original_reprint
keep_date["原创正文"] = Original_text
keep_date["原创图片"] = Original_pictures
keep_date["点赞量"] = Original_attitudes
keep_date["评论量"] = Original_comment
keep_date["转载正文"] = Reprint_text
keep_date["转载图片"] = Reprint_pictures
keep_date["转载点赞量"] = Reprint_attitudes
keep_date["转载评论量"] = Reprint_comment
keep_date["评论id"] = pl_name
keep_date["评论正文"] = pl_text
keep_date["回复id"] = hf_name
keep_date["回复正文"] = hf_text
keep_date.to_csv(r'weibo.csv', index=None, encoding="utf_8_sig")



#使用selenium自动化抓取淘宝
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException #超时
from selenium.webdriver.common.by import By #节点类型
from selenium.webdriver.common.keys import Keys #keys类（键盘操作指令）
from selenium.webdriver.support import expected_conditions as EC #检测节点是否被加载出来
from selenium.webdriver.support.wait import WebDriverWait #用于显示等待
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pyquery import PyQuery as pq #解析库
from urllib.parse import urlencode #urlencode 对字典或由两元素元组组成的列表进行码编码，将其转换为符合url规范的查询字符串
from urllib.parse import quote #quote 对非ASCII编码的字符进行编码，默认进行UTF-8编码,一般对请求url路径中非ASCII编码的字符(string)进行编码
import time
import random
import pandas as pd
import csv
import datetime
import json
import os

def get_Time(randomORnow_time):
    '''
    randomORnow_time 0: 1-5秒内随机休整
    randomORnow_time 1: 返回年-月-日 时:分:秒
    randomORnow_time 2: 返回年-月-日
    randomORnow_time 3: 返回年/月/日
    '''
    if randomORnow_time == 0:
        time.sleep(random.randint(1, 5))
    if randomORnow_time == 1:
        return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    if randomORnow_time == 2:
        return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    if randomORnow_time == 3:
        timeone = datetime.datetime.now().timetuple()
        return str(timeone.tm_year) + '/' + str(timeone.tm_mon) + '/' + str(timeone.tm_mday)

def page_index(page):
    """
    函数作用：等待每页dom中各个节点加载完成
    参数介绍：page（页数，类型：int）
    """
    print("\r" + "正在爬取第{}页信息...".format(page), end="", flush=True)
    try:
        if page > 1:
            input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mainsrp-pager"]/div/div/div/div[2]/input')))
            submit = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mainsrp-pager"]/div/div/div/div[2]/span[3]')))
            input.clear()
            input.send_keys(page)
            submit.click()
        #查找当前页码是否加载完全
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page)))
        #查找当前页商品是否加载完全
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mainsrp-itemlist"]/div/div/div[1]')))
        get_data() #获取数据
    except Exception as e:
        print("第 {} 页请求超时！".format(page))
        matter_index(driver.current_url,key,page,e) #将存在问题页收录日志

def login_ing(url,user,password,n):
    """
    函数介绍：页面登录
    参数介绍：url（页面地址，类型：str） user（账号，类型：str） password（密码，类型：str） n(爬取页数，类型：int)
    """
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fm-login-password"]')))
    driver.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(user)
    driver.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(password)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="nc_1_n1z"]')))
    n1z = driver.find_element_by_xpath('//*[@id="nc_1_n1z"]')
    # ActionChains(driver).drag_and_drop_by_offset(fff, xoffset=100, yoffset=0).perform()
    # time.sleep(3)
    # driver.find_element_by_xpath('//*[@id="login-form"]/div[4]/button').click()
    if n1z is not None:
        print(input("请手动验证,按回车键继续: "))
    else:
        driver.find_element_by_xpath('//*[@id="login-form"]/div[4]/button').click()
    if n > 100:
        n = 100
    for i in range(1, n+1):
        page_index(i)
        get_Time(0)  # 随机休整

def get_data():
    """
    函数介绍：爬取规定数据
    """
    html = pq(driver.page_source) #获取源码
    html.find("#mainsrp-itemlist .item.J_MouserOnverReq.item-ad").remove() #去除广告
    itmes = html('#mainsrp-itemlist .items .item').items()
    for i in itmes:
        w = {
            "img_url" : i.find(".pic .img").attr("data-src"),
            "price" : i.find(".price > strong").text(),
            "deal": i.find(".deal-cnt").text(),
            "title": i.find(".title").text(),
            "shop": i.find(".shop").text(),
            "location": i.find(".location").text(),
        }
        with open(r"TB_data.txt", 'a', encoding="utf_8_sig") as f:
            f.write(json.dumps(w, indent=2, ensure_ascii=False))
            f.write("\n")
    return print("爬取成功！")

def matter_index(Q_url, Q_key, Q_page, Q_text):
    """
    函数介绍：内置错误机制，保存错误信息。文件类型csv  文件路径../Question.csv
    """
    global overall_situation
    with open(r"Question.csv", 'a', newline="", encoding="utf_8_sig") as f:
        w = csv.writer(f)
        if os.stat(r"Question.csv").st_size <= 0:
            w.writerow(list(["url", "搜索信息", "问题页数", "问题文本", "发生时间", "日期"]))
        w.writerow(list([Q_url, Q_key, Q_page, Q_text, get_Time(1), get_Time(3)]))
    proving = pd.read_csv(r'Question.csv')
    Q_today = [x for x in proving["日期"] if x == "{}".format(get_Time(3))]
    if len(Q_today) == overall_situation + 1:
        print("产生错误已收录成功...", "今日累计错误数:{}".format(len(Q_today)))
    else:
        print("错误收录失败,{}".format(Q_page))
    overall_situation += 1

if __name__ == "__main__":
    if os.path.isfile(r'Question.csv'):
        proving = pd.read_csv(r'Question.csv')
        overall_situation = len([x for x in proving["日期"] if x == "{}".format(get_Time(3))])
    else:
        overall_situation = 0
    #添加代理
    # chromeOptions.add_argument("'--proxy-server={}".format(proxy))
    driver = webdriver.Chrome()

    #显示等待
    wait = WebDriverWait(driver,10)
    key = "内存条"
    ym_url = 'https://s.taobao.com/search?q=' + quote(key)
    ym_user = "账号"
    ym_password = "密码"
    ym_num = 3 #目标爬取页数（tb 最多100页）
    login_ing(ym_url,ym_user,ym_password,ym_num)

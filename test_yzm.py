from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import requests
import cv2.cv2 as cv
import numpy as np
import time

web = webdriver.Chrome()

#请求网址
web.get("https://dun.163.com/trial/sense")

#点击事件
web.find_element_by_xpath('/html/body/main/div[1]/div/div[2]/div[2]/ul/li[2]').click()
time.sleep(2)
#验证阶段
web.find_element_by_xpath('/html/body/main/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/div[2]/div[3]/div/div/div[1]/div[1]/div').click()
time.sleep(3)
#获取图片
bg = web.find_element_by_xpath('/html/body/main/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div/div[1]/img[1]').get_attribute('src')
font = web.find_element_by_xpath('/html/body/main/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div/div[1]/img[2]').get_attribute('src')

#将写入文件 准备处理
with open('bg.jpg','wb') as f:
    f.write(requests.get(bg).content)
with open('font.jpg','wb') as f:
    f.write(requests.get(font).content)

#图片处理 灰度二值化
bg = cv.imread("bg.jpg")
font = cv.imread("font.jpg")

bg = cv.cvtColor(bg,cv.COLOR_BGR2GRAY)
font = cv.cvtColor(font,cv.COLOR_BGR2GRAY)

#去除滑块图片中除划片的多余部分
font = font[font.any(1)]

#cv视觉 匹配像素算法
result = cv.matchTemplate(bg,font,cv.TM_CCOEFF_NORMED) #精度高，速度慢，返回一个矩阵，矩阵中元素是font在bg每一个像素点的匹配度

#找出矩阵匹配度最高的元素的二维坐标
x,y = np.unravel_index(np.argmax(result), result.shape)


#定义滑动轨迹[更加拟合人手滑动]
#前4/5位移加速移动，后1/5减速移动
#依赖公式：1:[x = v0*t + 1/2*a*t*t]  2:[v = v0 + a*t]
t = 0.3
shift = []#每间隔0.2秒的位移
Current_shift= 0#当前位移
threshold = y*3/5 #速度阈值
v = 0#初速度

while True:
    if Current_shift > y:
        break
    else:
        #判断当前位移是否小于阈值，若小于则需满足【前4/5位移加速移动】
        if Current_shift < threshold:
            a = 2 #给定初速度
        #否则则需满足【后1/5减速移动】
        else:
            a = -3
        v0 = v
        v = v0 + a*t
        x = (v0*t) + (1/2*a*t*t)
        Current_shift += x
        shift.append(round(x))


#动作链 完成滑动动作
div = web.find_element_by_xpath('/html/body/main/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/div[2]/div[3]/div/div/div[2]/div/div/div[2]/div[2]')
ActionChains(web).click_and_hold(div).perform()
for i in shift:
    ActionChains(web).move_by_offset(xoffset=i,yoffset=0).perform()
time.sleep(0.5)
ActionChains(web).release().perform()
time.sleep(1)


#检验是否成功
try:
    Text = web.find_element_by_xpath('//*[@class="yidun_classic-tips"]/span[2]')
    if "验证成功" in Text.text:
        print("验证成功！")
    else:
        print("验证失败！")
        #此处可做验证失败后重新验证,不在赘述。
except Exception as e:
    print(e)






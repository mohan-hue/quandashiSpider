# -*- coding: utf-8 -*-

import random
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from testSpider.cnSpider.ocrImage import getCode


class QuanDaShiSpider(object):

    def __init__(self):
        self.driver = webdriver.Chrome()
        # 将浏览器窗口最大化
        self.driver.maximize_window()
        # 建立显示等待
        self.wait = WebDriverWait(self.driver, 10)
        self.index = 0

    def loginQDS(self):
        """
        登录权大师，使用密码登录，接上QQ快速登录，可以省略验证码，
        若不然则需要接上打码平台"""
        self.driver.get('https://www.quandashi.com/')
        time.sleep(random.randrange(2, 4))
        # 点击登录
        self.driver.find_element_by_xpath('//div[@id="page-header"]/div[2]/a[3]').click()
        time.sleep(random.randrange(2, 4))
        # 点击密码登录
        self.driver.find_element_by_xpath('//div[@class="login-bodyer"]/div[2]/div[2]/a[1]').click()
        time.sleep(random.randrange(2, 4))
        # 点击同意协议
        self.driver.find_element_by_xpath('//div[@class="username-box"]/div[4]/label/input').click()
        time.sleep(random.randrange(2, 4))
        # 点击QQ快速登录
        self.driver.find_element_by_xpath('//div[@class="username-box"]/div[3]/div[2]/a[2]').click()
        time.sleep(random.randrange(2, 4))
        pages = self.driver.page_source
        with open('qds.html', 'w', encoding='utf-8') as f:
            f.write(pages)

        self.driver.switch_to.frame('ptlogin_iframe')
        # 有时候xpath定位不到iframe里面的标签可以用css
        self.driver.find_element_by_xpath('//*[@id="img_out_1347337893"]').click()
        # self.driver.find_element_by_css_selector('#img_out_1347337893').click()
        time.sleep(random.randrange(2, 4))
        # 搜索商标
        self.driver.find_element_by_xpath('//div[@class="public-search"]/div[2]/input').send_keys('阿里')
        time.sleep(random.randrange(2, 4))
        self.driver.find_element_by_xpath('//div[@class="public-search"]/div[2]/button').click()
        time.sleep(random.randrange(2, 4))
        self.getBrand(0)

    def getBrand(self, number):
        """获取商标详情信息"""
        # 更换窗口标签
        winHandles = self.driver.window_handles
        time.sleep(random.randrange(2, 4))
        self.driver.switch_to.window(winHandles[1])
        # print('第一个窗口', winHandles)
        brandButtonList = \
            self.driver.find_elements_by_xpath('//ul[@class="search-list hhr-search-list"]/li/div/div[2]/h2/span[1]')

        # brand1 = self.driver.find_elements_by_xpath('//li[contains(@class, "clearfix")]')
        print("所有按钮信息", brandButtonList)
        # print("所有按钮信息1", brand1)
        for i in range(len(brandButtonList)):
            # 这里是只取每页的前三个
            if i > 3:
                break
            time.sleep(random.randrange(3, 5))
            brandButtonList[i].click()
            time.sleep(random.randrange(2, 4))
            self.extractBrankInfo()

        # # 写一个跳转至最后一页进行测试，查看函数是否退出递归
        # self.driver.find_element_by_xpath\
        #     ('//*[@id="searchList"]/div[2]/div[3]/div[1]/div[1]/div/div/div/div[1]/div/div[3]/ul/li[13]/input').\
        #     send_keys('1000')
        # self.driver.find_element_by_xpath\
        #     ('//*[@id="searchList"]/div[2]/div[3]/div[1]/div[1]/div/div/div/div[1]/div/div[3]/ul/li[13]/a').click()
        time.sleep(random.randrange(2, 4))
        # 下一页，若是最后一页会报错， 然后退出
        number += 1
        try:
            print("数字", number)
            if number > 3:
                print("数字", number)
                return -1
            else:
                self.driver.find_element_by_xpath('//div[@class="pagination"]/ul/li[@class="go-page"]/preceding-sibling::*[1]').click()
                self.getBrand(number)
        except Exception as e:
            print('报错了，程序也结束了')

    def extractBrankInfo(self):
        """提取商标信息"""
        winHandles = self.driver.window_handles
        # print(winHandles)
        self.driver.switch_to.window(winHandles[2])
        time.sleep(random.randrange(2, 4))
        pages = self.driver.page_source
        with open('1.html', 'w', encoding='utf-8') as f:
            f.write(pages)
        brandInfoTitle = self.driver.find_elements_by_xpath('//div[@id="searchDetail"]/div[2]/table/tbody/tr/td')
        brandList = []
        print("商标注册信息列表(需要遍历提取text属性)", len(brandInfoTitle), brandInfoTitle)
        for info in brandInfoTitle:
            brandList.append(info.text)
        print("提取出来的商标信息", len(brandList), brandList)  # 列表里的数据两两成组，有25组，50个数据
        # 以下为保存数据到csv文件
        titleBrand = []
        contentBrand = []
        self.index += 1
        with open('quandashi.csv', 'a', newline='') as f:
            write = csv.writer(f)
            for i in range(len(brandList)):
                if i % 2 == 0:
                    titleBrand.append(brandList[i])
                else:
                    # 将日期格式中的-符号换为.符号，不然显示不出，而该列只有.符号的则是无内容
                    if "-" in brandList[i]:
                        brandList[i] = brandList[i].replace("-", ".")
                    contentBrand.append(brandList[i])
            # 标题只写如一次
            if self.index == 1:
                write.writerow(titleBrand)
            write.writerow(contentBrand)

        time.sleep(random.randrange(3, 5))
        self.driver.close()

        winHandles = self.driver.window_handles
        self.driver.switch_to.window(winHandles[1])
        # print(winHandles)
        # brandBtn = \
        #     self.driver.find_elements_by_xpath('//ul[@class="search-list hhr-search-list"]/li/div/div[2]/h2/span[1]')
        # print('看看是否会自动返回到前一个窗口', brandBtn)


if __name__ == "__main__":
    qds = QuanDaShiSpider()
    qds.loginQDS()

"""
登录按钮xpath：//div[@id="page-header"]/div[2]/a[3]
密码登录按钮xpath：//div[@class="login-bodyer"]/div[2]/div[2]/a[1]
协议按钮xpath：//div[@class="username-box"]/div[4]/label/input
QQ快速登陆(前提是电脑挂着QQ并且不是第一次登录权大师)xpath
 --> //div[@class="username-box"]/div[3]/div[2]/a[2]
快速登录头像按钮xpath(可能找不到): //*[@id="img_out_1347337893"]

搜索框xpath：//div[@class="public-search"]/div[2]/input
权一下按钮xpath：//div[@class="public-search"]/div[2]/button
提取商标列表xpath：//ul[@class="search-list hhr-search-list"]/li/div/div[2]/h2/span

提取详情信息xpath：//div[@id="searchDetail"]/div[2]/table/tbody/tr/td
之后就需要遍历返回的列表

下一页xpath：//div[@class="pagination"]/ul/li[@class="go-page"]/preceding-sibling::*[1]  
preceding是找当前节点的哥哥节点
下一页xpath：//div[@class="pagination"]/ul/li[@class="go-page"]/following-sibling::*[1]  
following是找当前节点的弟弟节点(均包含自己在内)

"""

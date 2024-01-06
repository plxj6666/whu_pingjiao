#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
import time

import click as click
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By


def init_driver() -> Chrome:
    # 初始化 driver
    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    if 'Windows' in platform.platform():
        executable_path = os.path.join(os.path.dirname(__file__), './driver/chromedriver.exe')
    else:
        executable_path = os.path.join(os.path.dirname(__file__), './driver/chromedriver')
    service = Service(executable_path=executable_path)
    # driver = Chrome(executable_path=executable_path, options=chrome_options)
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(3)
    return driver


def login(driver: Chrome, username: str, password: str) -> bool:
    driver.get('http://s.ugsq.whu.edu.cn/caslogin')
    username_input = driver.find_element(By.XPATH, '//*[@id="username"]')
    username_input.send_keys(username)
    password_input = driver.find_element(By.XPATH, '//*[@id="password"]')
    password_input.send_keys(password)
    login_button = driver.find_element(By.XPATH, '//*[@id="casLoginForm"]/p[2]/button')
    login_button.click()
    loginstates = True
    try:
        loginstate = driver.find_element(By.XPATH, '//*[@id="casLoginForm"]/*[@id="msg"]').text
        if loginstate == "您提供的用户名或者密码有误" :
            loginstates = False
    except:
        pass
    # time.sleep(3)
    return loginstates

def pingjia(driver: Chrome) -> None:
    # 限制不能给满分，第一个选项四星
    driver.find_element(By.XPATH, '//div[@class="controls" and label[@class="radio"]]/label[2]').click()
    # 其他选项全部五星
    labels = driver.find_elements(By.XPATH, '//div[@class="controls" and label[@class="radio"]]/label[1]/div/span/input')[1:]
    for label in labels:
        label.click()
    # 意见填无
    textarea = driver.find_element(By.XPATH, '//*[@id="pjnr"]/li[7]/fieldset/ol/li/div[3]/div/textarea')
    textarea.send_keys('无')
    submit_button = driver.find_element(By.XPATH, '//*[@id="pjsubmit"]')
    submit_button.click()
    time.sleep(1)
    # 评教成功后关闭弹窗
    close_button = driver.find_element(By.XPATH, '//*[@id="finishDlg"]/div[2]/button')
    close_button.click()


def pingjia_per_page(driver: Chrome, all_pingjiaed: bool, count: int) -> int:
    # 修改办法，通过INDEX获取未评价的下标
    length = len(driver.find_elements(By.XPATH, '//*[@id="pjkc"]/tr'))
    for i in range(length):
        kcs = driver.find_elements(By.XPATH, '//*[@id="pjkc"]/tr')  # 重复获取页面，避免出现element刷新
        if not all_pingjiaed:
            break
        # time.sleep(3)
        if kcs[i].find_element(By.XPATH, 'td[5]').text == '已评价':  # 查看是否评价
            continue
        kcs[i].find_element(By.XPATH, 'td[6]/a').click()  # 找不到元素
        pingjia(driver)
        # driver.refresh()
        all_pingjiaed = True
        count += 1
        time.sleep(3)
    return count


@click.command()
@click.option('--username', prompt='信息门户账号（学号/手机号）')
@click.option('--password', prompt='信息门户密码')
def pingjiao(username: str, password: str) -> int:
    count = 0
    driver = init_driver()
    login_status = login(driver, username, password)
    if not login_status:
        print("用户名或密码错误")
        return 0

    all_pingjiaed = False

    while not all_pingjiaed:
        all_pingjiaed = True
        driver.get('https://ugsqs.whu.edu.cn/studentpj')
        driver.find_element(By.XPATH, '//*[@id="task-list"]/li').click()
        # 首页
        count = pingjia_per_page(driver, all_pingjiaed, count)
        if not all_pingjiaed:
            continue
        # 剩余页
        pages = driver.find_elements(By.XPATH, '//*[@id="tb1_wrapper"]/div/ul/li/a')[2:-1]
        for page in pages:
            if not all_pingjiaed:
                break
            page.click()
            time.sleep(3)
            count = pingjia_per_page(driver, all_pingjiaed, count)

    print(f'共评价了 {count} 门课程')
    print("感谢使用，若有版本问题请自行处理或维护!")
    return count


if __name__ == '__main__':
    pingjiao()

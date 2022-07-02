#!/usr/bin/env python3
import pandas as pd
from bs4 import BeautifulSoup
import argparse, logging, sys, os
from itertools import product

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
COUNT = dict()
SORT_COUNT = dict()
PASSWORD = set()
USERNAME = set()
LEET_REPLACE_SMALE = {'a': '@', 'A': '@'}
LEET_REPLACE_MEDIUM = {
        'e': '3', 'E': '3',
        'a': '@', 'A': '@',
        'i': '!', 'I': '!',
        's': '$', 'S': '$',
        'o': '0', 'O': '0'
    }
LEET_REPLACE = LEET_REPLACE_SMALE
SPECIAL_CHAR_SMALE = ['!']
SPECIAL_CHAR_MEDIUM = ['!','?','$','&','%']
SPECIAL_CHAR = SPECIAL_CHAR_SMALE

def write_file(f_name, liste):
    file = f'{f_name}_{str(len(liste))}.lst'
    with open(file, 'w') as f:
        for item in liste:
            f.write(item.strip()+'\n')
        f.close()
        logging.info(f'Crated file: {file}')

def create_pd():
    df = pd.DataFrame(SORT_COUNT, index=['Count']).T.rename_axis('Word').reset_index()
    df.index += 1
    df.head()
    print(df)
    # Crate a .csv file with colum index, word and count
    file = f'{args.outputCvs}_{str(len(SORT_COUNT))}.csv'
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    df.to_csv(file, sep='\t', encoding='utf-8')
    logging.info(f'Crated file: {file}')

def check_len(word):
    if len(word) >= args.length[0] and len(word) <= args.length[1]:
        return word
    return None

def get_username(soup):
    global USERNAME
    # author 
    tag_list = soup.find_all('p', class_="wp-block-post-author__name")
    # commentator
    tag_list += soup.find_all('b', class_="fn")
    if tag_list:
        for name in tag_list:
            USERNAME.add(name.text)

def get_password(soup):
    global COUNT
    for word in soup.split(' '):
        word = word.strip().replace('\n','')
        if word != '': # and word.isalpha():
            if word[-1] in ".,!?:;":
                word = word[:-1]
            if word.isalpha():
                if check_len(word):
                    if word in COUNT:
                        COUNT[word] += 1
                    else:
                        COUNT[word] = 1

def load_html(rootpath):
    for page in os.listdir(rootpath):
        if os.path.isdir(rootpath+'/'+page):
            html_path = f'{rootpath}/{page}/HTML/'
            for file in os.listdir(html_path):
                with open(html_path+file) as f:
                    html_code = f.read()
                soup = BeautifulSoup(html_code, "lxml")
                get_username(soup)
                get_password(soup.text)
                
def leetspeak():
    global PASSWORD
    tmp = set()
    for word in PASSWORD:
        leet_words = [''.join(letters) for letters in product(*({c, LEET_REPLACE.get(c, c)} for c in word))]
        tmp.update(leet_words)
    PASSWORD.update(tmp)

def special_char():
    global PASSWORD
    tmp = set()
    for word in PASSWORD:
        for char in SPECIAL_CHAR:
            tmp.add(word+char)
    PASSWORD.update(tmp)

def user_input(average, min_frequency, max_frequency):
    try:
        symbole, option, num = '','',1
        print(f'The words have a frequency of {min_frequency} to {max_frequency}')
        print(f'Most words appear {average} times on average')
        print('[?] Input Form: \n  - All Words = 0\n  - Words with [<,>,=] number\n  - Count Words with frequency = ? number\n')
        while option.lower() != 'exit':
            option = input("Input: ")
            try:
                symbole = option.split(' ')[0]
                num = option.split(' ')[1]
                if symbole == '?':
                    print(f'[?] There are {len([value for key,value in SORT_COUNT.items() if value==int(num)])} words that appear {num} times')
                    continue
                option = num            
            except:
                continue
            if option.isdigit() and symbole != '?':
                num = option
                break
    except KeyboardInterrupt:
        print("\nExit")
        exit()
    return num, symbole

def crate_pw_list(min_frequency, max_frequency):
    global PASSWORD
    average = round(sum(SORT_COUNT.values())/len(SORT_COUNT), 2)
    create_pd()
    num, symbole = user_input(average, min_frequency, max_frequency)
    if int(num) == 0:
        for key,value in SORT_COUNT.items():
            PASSWORD.add(key)
    elif symbole == '=' or symbole == '==':
        for key,value in SORT_COUNT.items():
            if  value == int(num):
                PASSWORD.add(key)
    elif symbole == '<':
        for key,value in SORT_COUNT.items():
            if  value < int(num):
                PASSWORD.add(key)
    elif symbole == '>':
        for key,value in SORT_COUNT.items():
            if  value > int(num):
                PASSWORD.add(key)
    elif symbole == '<=':
        for key,value in SORT_COUNT.items():
            if  value <= int(num):
                PASSWORD.add(key)
    elif symbole == '>=':
        for key,value in SORT_COUNT.items():
            if  value >= int(num):
                PASSWORD.add(key)
    else:
        print("\nExit")
        exit()

def main():
    print("\n| Start Data exfiltration Script")
    for password_list in args.passwordlist:
        for word in open(password_list):
            word = word.replace('\n','')
            if check_len(word):
                PASSWORD.add(word)
    if args.rootpath:
        load_html(args.rootpath.rstrip('/'))
        # sorted words from most to least
        for key in sorted(COUNT, key=COUNT.get, reverse=True):
            SORT_COUNT[key] = COUNT[key]
        write_file(args.outputUser, USERNAME)
        crate_pw_list(min(SORT_COUNT.values()), max(SORT_COUNT.values()))
    if args.leetspeak:
        leetspeak()
    if args.specialchar:
        special_char()
    write_file(args.outputPw, PASSWORD)
    print("\n| End")
   
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = '')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-rp', '--rootpath', type=str, help='Absolute path to /root/ Directory')
    group.add_argument('-p', '--passwordlist', nargs='*', default=[], type=str, help='One or more lists with Passwords')
    parser.add_argument('-sc', '--specialchar', action='store_true', default=False, help='Flag special character')
    parser.add_argument('-ls', '--leetspeak', action='store_true', default=False, help='Flag Leetspeak')
    parser.add_argument('-l', '--length', nargs=2, default=[8,16], type=int, help='Min and Max Word length in Passwordlist')
    parser.add_argument('-op', '--outputPw', nargs='?', default='wordlist', help='Output File Name for Passwords')
    parser.add_argument('-ou', '--outputUser', nargs='?', default='username', help='Output File Name for Usernames')
    parser.add_argument('-ocvs', '--outputCvs', nargs='?', default='count', help='Output File Name for Counted Words overview')
    parser.add_argument('-log', '--level', default=20, type=int, help='Set Logging Level')
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    main()



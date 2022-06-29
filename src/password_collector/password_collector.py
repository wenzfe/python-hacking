#!/usr/bin/env python3
import pandas as pd
from bs4 import BeautifulSoup
import argparse, logging, sys, os, re
from itertools import product

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
COUNT = dict()
SORT_COUNT = dict()
PASSWORD_LIST = set()
LEET_REPLACE_SMALE = {
        'a': '@', 'A': '@',
    }
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

def pw_output():
    file = f'{args.outputPw}_{str(len(PASSWORD_LIST))}.lst'
    with open(file, 'w') as f:
        for word in PASSWORD_LIST:
            f.write(word+'\n')
        f.close()
    logging.info(f'Crated file: {file}')

def pd_output(df):
    file = f'{args.outputCvs}_{str(len(SORT_COUNT))}.csv'
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    df.to_csv(file, sep='\t', encoding='utf-8')
    logging.info(f'Crated file: {file}')

def check_len(word):
    if len(word) >= args.length[0] and len(word) <= args.length[1]:
        return word
    return None

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
                    with open(html_path+file) as f:
                        html_code = f.read()
                    soup = BeautifulSoup(html_code, "html.parser").text
                    
                    for word in soup.split(' '):
                        word = word.strip().replace('\n','')
                        if word != '' and word.isalpha():
                            if word[-1] in ".,!?:;":
                                word = word[:-1]
                            if check_len(word):
                                word_count(word)
                
def leetspeak():
    global PASSWORD_LIST
    tmp = set()
    for word in PASSWORD_LIST:
        leet_words = [''.join(letters) for letters in product(*({c, LEET_REPLACE.get(c, c)} for c in word))]
        tmp.update(leet_words)
    PASSWORD_LIST.update(tmp)

def special_char():
    global PASSWORD_LIST
    tmp = set()
    for word in PASSWORD_LIST:
        for char in SPECIAL_CHAR:
            tmp.add(word+char)
    PASSWORD_LIST.update(tmp)

def crate_pw_list(min_frequency, max_frequency):
    global PASSWORD_LIST
    average = sum(SORT_COUNT.values())/len(SORT_COUNT)
    average = round(average, 2)
    df = pd.DataFrame(SORT_COUNT, index=['Count']).T.rename_axis('Word').reset_index()
    df.index += 1
    df.head()
    print(df)
    pd_output(df)
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
        if option.isdigit() and symbole != '?': # and not symbole.isdigit():
            num = option
            break
    if int(num) == 0:
        for key,value in SORT_COUNT.items():
            PASSWORD_LIST.add(key)
    elif symbole == '=' or symbole == '==':
        for key,value in SORT_COUNT.items():
            if  value == int(num):
                PASSWORD_LIST.add(key)
    elif symbole == '<':
        for key,value in SORT_COUNT.items():
            if  value < int(num):
                PASSWORD_LIST.add(key)
    elif symbole == '>':
        for key,value in SORT_COUNT.items():
            if  value > int(num):
                PASSWORD_LIST.add(key)
    elif symbole == '<=':
        for key,value in SORT_COUNT.items():
            if  value <= int(num):
                PASSWORD_LIST.add(key)
    elif symbole == '>=':
        for key,value in SORT_COUNT.items():
            if  value >= int(num):
                PASSWORD_LIST.add(key)
    else:
        exit()

def main():
    for password_list in args.passwordlist:
        print(password_list)
        for word in open(password_list):
            word = word.replace('\n','')
            if check_len(word):
                PASSWORD_LIST.add(word)

    print("\n| Start Selenium Script")
    if args.dirpath:
        args.dirpath = args.dirpath.rstrip('/')
        parse_html()
        for k in sorted(COUNT, key=COUNT.get, reverse=True): #sort dict
            SORT_COUNT[k] = COUNT[k]
        crate_pw_list(min(SORT_COUNT.values()), max(SORT_COUNT.values()))

    if args.leetspeak:
        leetspeak()
    if args.specialchar:
        special_char()

    #print("\n--- PASSWORD LIST ---")
    #print(PASSWORD_LIST)

    pw_output()

    print("\n| End")
   
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = '')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-dp', '--dirpath', type=str, help='Absolute path to /root/ Directory')
    group.add_argument('-p', '--passwordlist', nargs='*', default=[], type=str, help='One or more lists with Passwords')

    parser.add_argument('-sc', '--specialchar', action='store_true', default=False, help='Flag special character')
    parser.add_argument('-ls', '--leetspeak', action='store_true', default=False, help='Flag Leetspeak')
    parser.add_argument('-l', '--length', nargs=2, default=[8,16], type=int, help='Min and Max Word length in Passwordlist')

    parser.add_argument('-opw', '--outputPw', nargs='?', default='wordlist', help='Output File Name for Passwordlist')
    parser.add_argument('-ocvs', '--outputCvs', nargs='?', default='count', help='Output File Name for Counted Words overview')
    parser.add_argument('-log', '--level', default=20, type=int, help='Set Logging Level')
    
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    main()



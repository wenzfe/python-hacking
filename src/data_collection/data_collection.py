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

# Crate .csv output file with count words
def create_pd():
    df = pd.DataFrame(SORT_COUNT, index=['Count']).T.rename_axis('Word').reset_index()
    df.index += 1
    df.head()
    print(df)
    # Crate a .csv file with colum index, word and count
    file = f'count_{str(len(SORT_COUNT))}.csv'
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    df.to_csv(file, sep='\t', encoding='utf-8')
    logging.info(f'Crated file: {file}')

# give words that have the right length
def check_len(word):
    if len(word) >= args.length[0] and len(word) <= args.length[1]:
        return word
    return None

def collect_username(soup):
    '''
    Serach for username in HTML source code by tags
    '''
    global USERNAME
    # author name
    tag_list = soup.find_all('p', class_="wp-block-post-author__name")
    # commentator names
    tag_list += soup.find_all('b', class_="fn")
    if tag_list:
        for name in tag_list:
            USERNAME.add(name.text)

# take all words from html.text and count them
def collect_word(soup):
    global COUNT
    for word in soup.split(' '):
        word = word.strip().replace('\n','')
        if word != '':
            if word[-1] in ".,!?:;":
                word = word[:-1]
            if word.isalpha():
                if check_len(word): # only words with predetermined length
                    # count number of word in all html pages
                    if word in COUNT:
                        COUNT[word] += 1
                    else:
                        COUNT[word] = 1

# Load all html pages from root path
def load_html(rootpath):
    for page in os.listdir(rootpath):
        if os.path.isdir(rootpath+'/'+page):
            html_path = f'{rootpath}/{page}/HTML/'
            for file in os.listdir(html_path):
                with open(html_path+file) as f:
                    html_code = f.read()
                soup = BeautifulSoup(html_code, "lxml")
                collect_username(soup)
                collect_word(soup.text)

# apply leepsepak to the words in the passwordlist
def leetspeak():
    global PASSWORD
    l_befor = len(PASSWORD)
    tmp = set()
    for word in PASSWORD:
        leet_words = [''.join(letters) for letters in product(*({c, LEET_REPLACE.get(c, c)} for c in word))]
        tmp.update(leet_words)
    PASSWORD.update(tmp)
    print(f"[?] Apply {len(PASSWORD)-l_befor} Lettspeak Passwords")

# apply special character at the end of the words in passwordlist
def special_char():
    global PASSWORD
    l_befor = len(PASSWORD)
    tmp = set()
    for word in PASSWORD:
        for char in SPECIAL_CHAR:
            tmp.add(word+char)
    PASSWORD.update(tmp)
    print(f"[?] Apply {len(PASSWORD)-l_befor} Special character Passwords")

# Ask the user for input, which creates the password list
def user_input(average, min_frequency, max_frequency):
    try:
        symbole, option, num = '','',1
        print(f'[?] Collect {len(SORT_COUNT)} words')
        print(f'[?] The words have a frequency of {min_frequency} to {max_frequency}')
        print(f'[?] Most words appear {average} times on average')
        print('Input Form: \n  - All Words: = 0\n  - Words with: [<,>,=] number\n  - Count Words with frequency: ? number\n')
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

# Crate password list from count words with
def crate_pw_list(min_frequency, max_frequency):
    global PASSWORD
    average = round(sum(SORT_COUNT.values())/len(SORT_COUNT), 2)
    create_pd()
    # only use words that match the user input
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
    global SORT_COUNT
    print("\n| Start Data exfiltration Script")
    print(f"[?] Take words with length {args.length[0]} to {args.length[1]}")
    # Add all passwords from passwordlist
    for password_list in args.passwordlist:
        for word in open(password_list):
            word = word.replace('\n','')
            if check_len(word): # only words with predetermined length
                PASSWORD.add(word)
    # Use HTML from root path
    if args.rootpath:
        load_html(args.rootpath.rstrip('/'))
        # sorted words from most to least
        for key in sorted(COUNT, key=COUNT.get, reverse=True):
            SORT_COUNT[key] = COUNT[key]
        write_file(args.outputUser, USERNAME) # write output file with usernames 
        print(f"[?] Collect {len(USERNAME)} usernames")
        crate_pw_list(min(SORT_COUNT.values()), max(SORT_COUNT.values()))
        print(f"[?] Got {len(PASSWORD)} Passwords")
    if args.leetspeak:
        leetspeak()
        print(f"[?] Got {len(PASSWORD)} Passwords")
    if args.specialchar:
        special_char()
        print(f"[?] Got {len(PASSWORD)} Passwords")
    write_file(args.outputPw, PASSWORD) # write output file with passwords
    print("\n| End")
   
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Collect usernames and words for passwords from local HTML pages. Filter by word length and uses leetspeak and special character at the end of the word')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-rp', '--rootpath', type=str, help='Absolute path to /root/ Directory, see Spider output')
    group.add_argument('-p', '--passwordlist', nargs='*', default=[], type=str, help='One or more lists with Passwords')
    parser.add_argument('-sc', '--specialchar', action='store_true', default=False, help='Use special character')
    parser.add_argument('-ls', '--leetspeak', action='store_true', default=False, help='Use Leetspeak')
    parser.add_argument('-l', '--length', nargs=2, default=[8,16], type=int, help='Min and max word length')
    parser.add_argument('-op', '--outputPw', nargs='?', default='wordlist', help='Output filename for passwords')
    parser.add_argument('-ou', '--outputUser', nargs='?', default='username', help='Output File Name for Usernames')
    parser.add_argument('-log', '--level', default=20, type=int, help='Set Logging Level')
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    main()



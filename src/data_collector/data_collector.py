#!/usr/bin/env python3
import pandas as pd
from bs4 import BeautifulSoup
import argparse, logging, sys, os
from itertools import product

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]' # logging
COUNT = dict() # word frequency
SORT_COUNT = dict() # word frequency sorted in descending order
PASSWORD = set() # includes generated passwords
USERNAME = set() # contains found usernames
# optional extension of the password. (small is intended for the presentation)
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
    '''
    Writes the contents of the list to a file.
    These are later the found user names or the generated password
    '''
    file = f'{f_name}_{str(len(liste))}.lst'
    with open(file, 'w') as f:
        for item in liste:
            f.write(item.strip()+'\n')
        f.close()
        logging.info(f'Crated file: {file}')

def create_pd():
    '''
    Outputs a .csv file that shows the frequency of the occurring words.
    '''
    df = pd.DataFrame(SORT_COUNT, index=['Count']).T.rename_axis('Word').reset_index()
    df.index += 1
    df.head()
    print(df)
    # Crate a .csv file with colum index, word and count
    file = f'count_{str(len(SORT_COUNT))}.csv'
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    df.to_csv(file, sep='\t', encoding='utf-8')
    logging.info(f'Crated file: {file}')

def check_len(word):
    '''
    Checks whether the word has the minimum and maximum length, which was previously determined.
    '''
    if len(word) >= args.length[0] and len(word) <= args.length[1]:
        return word
    return None

def collect_username(soup):
    '''
    Serach for username in HTML source code by tags.
    It can only be author or commenter names.
    '''
    global USERNAME
    # author name
    tag_list = soup.find_all('p', class_="wp-block-post-author__name")
    # commentator names
    tag_list += soup.find_all('b', class_="fn")
    if tag_list:
        for name in tag_list:
            USERNAME.add(name.text)

def filter(word):
    '''
    Special word filter, serves for a short and clear output. 
    (intended for presentation)
    '''
    word = word.strip().replace('\n','')
    if word != '':
        if word[-1] in ".,!?:;":
            word = word[:-1]
        # only letters in the word
        if word.isalpha(): 
            return word
    return ''

def collect_word(text):
    '''
    Takes all words from the text and counts their frequency.
    A filter only allows certain words.
    '''
    global COUNT
    for word in text.split(' '):
        word = filter(word)
        if check_len(word): # only words with predetermined length
            # count number of word in all html pages
            if word in COUNT:
                COUNT[word] += 1
            else:
                COUNT[word] = 1

def load_html(rootpath):
    '''
    Gets all html files from the root path. 
    Calls the functions collect_username and collect_word, that process html or plain text.
    '''
    for page in os.listdir(rootpath):
        if os.path.isdir(rootpath+'/'+page):
            html_path = f'{rootpath}/{page}/HTML/'
            for file in os.listdir(html_path):
                with open(html_path+file) as f:
                    html_code = f.read()
                soup = BeautifulSoup(html_code, "html.parser")
                collect_username(soup)
                collect_word(soup.text)

def leetspeak():
    '''
    Applies all possible variants of leetspeak to the password.
    '''
    global PASSWORD
    l_befor = len(PASSWORD) # number of current passwords
    leets_list = set() # all leetspeak variants
    for password in PASSWORD:
        # crate all leetspeak variants
        leet_words = [''.join(letters) for letters in product(*({c, LEET_REPLACE.get(c, c)} for c in password))]
        leets_list.update(leet_words)
    PASSWORD.update(leets_list) # add all leetspeak variants to the password list
    print(f"[?] Apply {len(PASSWORD)-l_befor} lettspeak passwords")

def special_char():
    '''
    Adds the special characters at the end of the password.
    '''
    global PASSWORD
    l_befor = len(PASSWORD) # number of current passwords
    schar_list = set()
    for word in PASSWORD:
        for char in SPECIAL_CHAR:
            schar_list.add(word+char)
    PASSWORD.update(schar_list) # add password with special characters to the password list
    print(f"[?] Apply {len(PASSWORD)-l_befor} special character passwords")

def user_input(average, min_frequency, max_frequency):
    '''
    Ask the user for input, which creates the password list.
    Only operations like <,<=,>,>=,= permitted.
    If = 0, all words are added to the password list.
    With ? number returns how many words occur with this number.
    '''
    try:
        symbole, option, num = '','',1
        print(f'[?] Collect {len(SORT_COUNT)} words')
        print(f'[?] The words have a frequency of {min_frequency} to {max_frequency}')
        print(f'[?] Most words appear {average} times on average')
        print('Input Form: \n  - All Words: = 0\n  - Words with: [<,<=,>,>=,=] number\n  - Count Words with frequency: ? number\n')
        # wait for user input
        while option.lower() != 'exit':
            option = input("Input: ")
            try:
                symbole = option.split(' ')[0]
                num = option.split(' ')[1]
                # count words with frequency of the given number
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
    '''
    Creates a password list from the words selected by user input.
    '''
    global PASSWORD
    average = round(sum(SORT_COUNT.values())/len(SORT_COUNT), 2)
    create_pd()
    num, symbole = user_input(average, min_frequency, max_frequency)
    # check user input and only use words that match
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

def read_password_list(p_list):
    '''
    Reads all passwords from the specified password lists and saves them as a password.
    Only passwords of the specified length are used.
    '''
    for password_list in p_list:
        for password in open(password_list):
            passwod = password.replace('\n','')
            if check_len(password): # only passwords with predetermined length
                PASSWORD.add(password)

def main():
    global SORT_COUNT
    print("\n| Start Data Collector Script")
    print(f"[?] Take words with length {args.length[0]} to {args.length[1]}")
    # Use HTML from root path
    read_password_list(args.passwordlist)
    if args.rootpath:
        load_html(args.rootpath.rstrip('/'))
        # sorted words from most to least
        for key in sorted(COUNT, key=COUNT.get, reverse=True):
            SORT_COUNT[key] = COUNT[key]
        if USERNAME:
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
    group.add_argument('-rp', '--rootpath', type=str, help='Absolute path to /root/ directory, see spider output')
    group.add_argument('-p', '--passwordlist', nargs='*', default=[], type=str, help='One or more lists with passwords')
    parser.add_argument('-sc', '--specialchar', action='store_true', default=False, help='Use special character')
    parser.add_argument('-ls', '--leetspeak', action='store_true', default=False, help='Use Leetspeak')
    parser.add_argument('-l', '--length', nargs=2, default=[8,16], type=int, help='Min and max word length')
    parser.add_argument('-op', '--outputPw', nargs='?', default='wordlist', help='Output filename for passwords')
    parser.add_argument('-ou', '--outputUser', nargs='?', default='username', help='Output filename for usernames')
    parser.add_argument('-log', '--level', default=20, type=int, help='Set Logging Level')
    args = parser.parse_args()
   
    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    main()



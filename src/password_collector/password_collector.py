#!/usr/bin/env python3

from bs4 import BeautifulSoup
import os, re
import argparse, logging, sys

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
COUNT = dict()
REGEX = "[.\S]{6,14}"

def word_count(word):
    global COUNT
    if word in COUNT:
        COUNT[word] += 1
    else:
        COUNT[word] = 1

def parse_html():
    for page in os.listdir(args.path):
        html_path = f'{args.path}/{page}/HTML/'
        for file in os.listdir(html_path):
            if os.path.isfile(html_path+file):
                if '.html' in file:
                    print(file)
                    with open(html_path+file) as f:
                        html_code = f.read()
                    regex_passwords_html = re.compile(REGEX)
                    soup = BeautifulSoup(html_code, "html.parser")
                    for password in  regex_passwords_html.findall(soup.text):
                        word_count(password)
                        
def main():
    print("\n| Start Selenium Script")
    parse_html()
    print("\n\n")
    print(COUNT)
    print("\n| End")
    exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = '')
    parser.add_argument('-p', '--path', required=True, type=str, help='Absolute path to /root/ Directory')
  
    parser.add_argument('-log', '--level', default=20, type=int, help='Set Logging Level')
    args = parser.parse_args()
    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    args.path = args.path.rstrip('/')
    main()




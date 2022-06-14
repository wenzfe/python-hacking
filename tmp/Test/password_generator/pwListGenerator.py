#! /usr/bin/python3
import json
import re
import sys
#from concurrent.futures import ThreadPoolExecutor
from rules import check_rule
from args import get_args

def crate_List(pwList_filter):
    f = open("password.txt", "w")
    #print("\n> password.dict: "+str(pwList_filter))
    print("\n-> "+str(len(pwList_filter))+ " Wörter in password.txt")
    for word in pwList_filter:
        f.write(word+"\n")
    f.close()
    f = open("nummber.txt", "w")
    #print("\n> password.dict: "+str(pwList_filter))
    print("\n-> "+str(len(num_List))+ " Wörter in nummber.txt")
    for num in num_List:
        f.write(num+"\n")
    f.close()
    return

def get_item(item):
    # name, beschreibung, description
    output_str = set()
    output_int =  set()
    if item: # nicht None
        for i in str(item).split():
            i = i.lower()
            c1 = re.sub('\W+',' ', i).split() # all special characters
            for w in c1:
                if w.isnumeric():
                    #if len(str(w)) >=2: #keine einstelligen zahlen
                    output_int.add(w)
                elif w.isalpha():
                    output_str.add(w)

                #c2 = re.findall('[A-Z][^A-Z]*', w.strip()) # Trenn bei upper "AbcDfg" -> "Abc Dfg"
        
    str_List.update(output_str)
    num_List.update(output_int)
    return output_str, output_int

def worker(dict_args):
    date = set()
    with open(dict_args["filename"], 'r') as outfile:
        dict_object = json.load(outfile)
    for item in dict_object["data"]:
        # add name
        get_item(item["name"])
        # linktarget
        get_item(item["linktarget"])
        # logo
        get_item(item["logo"])
        # websiete
        get_item(item["webseite"])
        # add text
        if dict_args["language"] == "de":
            get_item(item["beschreibung"])
        elif dict_args["language"] == "en":
            get_item(item["description"])
        else:
            get_item(item["beschreibung"])
            get_item(item["description"])
           
        get_item(item["mitarbeiteranzahl"])
        date.update(get_item(item["gründungsjahr"])[1])
        
        # add postadresse, besucheradresse
        get_item(item["postadresse"])
        get_item(item["besucheradresse"])
        
        # alles aus numList muss str sein!
        #pwList.update(numList)
    if dict_args["rule"] != "":
        pwList_rule = check_rule(str_List, num_List, date, dict_args)
    else: 
        pwList_rule = str_List

    # Check min and max
    list_filter = set()
    for word in pwList_rule:
        if len(word) >= int(dict_args["min_length"]) and len(word) <= int(dict_args["max_length"]):
            list_filter.add(word)
    return crate_List(list_filter)

str_List = set()
num_List = set()
def main():
    dict_args = get_args(sys.argv) #args.py
    print("Args: "+str(dict_args) +"\n")
    worker(dict_args)

    print("\n...End")
    return

if __name__ == "__main__":
    main()

import string 
# --- Rules ---
def last_int(rule_List, num_List):
    output = set()
    for word in rule_List:
        for num in num_List:
            output.add(word+str(num))
    return output

def first_int(rule_List, num_List):
    output = set()
    for word in rule_List:
        for num in num_List:
            output.add(str(num)+word)
    return output


def last_spec_chars(rule_List):
    output = set()
    # s_chars = "[@_!#$%^&*()<>?|}{~:]"
    s_chars = "[@!#$^&*?:"
    for word in rule_List:
        for s in s_chars:
            output.add(word+s)
    return output

def first_spec_chars(rule_List):
    output = set()
    s_chars = string.punctuation
    #s_chars = "[@!#$^&*?:"
    for word in rule_List:
        for s in s_chars:
            output.add(s+word)
    return output

def first_up(rule_List):
    output = set()
    for word in rule_List:
        output.add(word.capitalize())
    return output

def last_date(rule_List, date):
    output = set()
    for word in rule_List:
        for d in date:
            output.add(word+str(d))
    return output

def leetspeak(rule_List):
    output = set()
    low_letters = "abeghiloprstz"
    up_letters = "ABEGHILOPRSTZ"
    chars = "4836#11092572"
    for word in rule_List:
        l_word = word
        for i in range(0,len(low_letters)):
            l_word = l_word.replace(low_letters[i],chars[i])
            l_word = l_word.replace(up_letters[i],chars[i])
            if l_word != word:
                output.add(l_word)
    return output
# ---

def use_filter(str_List):
    output = set()
    for word in str_List:
        if len(word) > 3:
            output.add(word)
    return output

# main
def check_rule(str_List, num_List, date, dict_args):
    str_List = use_filter(str_List)
    ony_rule_List = str_List # wird geupdatet wenn nur rule ausgegeben werden soll
    for r in dict_args["rule"]:
        if r == "1":                   
            ony_rule_List.update(last_int(ony_rule_List, num_List))             #1
        elif r == "2":                   
            ony_rule_List.update(first_int(ony_rule_List, num_List))            #2
        elif r == "3":
            ony_rule_List = last_spec_chars(ony_rule_List)                      #3
        elif r == "4":
            ony_rule_List = first_spec_chars(ony_rule_List)                     #4
        elif r == "5":
            ony_rule_List = first_up(ony_rule_List)                             #5
        elif r == "6":
            ony_rule_List = last_date(ony_rule_List, date)                      #6

        elif r == "9":
            ony_rule_List = leetspeak(ony_rule_List)                            #9
        else: 
            print("Wrong Rule Input!")


    if len(ony_rule_List) == 0:
        return str_List
    else:
        return ony_rule_List



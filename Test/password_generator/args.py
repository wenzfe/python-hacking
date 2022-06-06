import sys

def get_args(args):
    dict_args = dict()
    dict_args = set_default(dict_args)
    if len(args) == 1:
        print("Use: ./pwGenerator.py -h (HELP) -d (DEFAULT)")
        sys.exit()
    for i in range(1,len(args)):
        if "-" in args[i]:
            opt = args[i][1:]
            print(opt)
            if opt == "h":
                show_help()
            elif opt == "d": #default
                break
            elif opt == "i":
                dict_args["filename"] = args[i+1]
            elif opt == "o":
                dict_args["output"] = args[i+1]
            elif opt == "min":
                dict_args["min_length"] = args[i+1]
            elif opt == "max":
                dict_args["max_length"] = args[i+1]
            elif opt == "l":
                if args[i+1] == "de":
                    dict_args["language"] = "de"
                elif args[i+1] == "en":
                    dict_args["language"] = "en"
                else:
                    dict_args["language"] = "both"
            # Rules
            elif opt == "r":
                dict_args["rule"] = args[i+1]
          
    return dict_args


def show_help():
    print("Usage: ./pwGenerator.py -i [INPUT FILE] -l [Language] -min -max -r [Rule]")
    print("-i INPUT FILE:       Input file .json")
    print("-l Language:         de=german, en=english, both")
    print("-r RULES:")
    print("  Zahl_Ende          :    1")
    print("  Zahl_Anfang        :    2")
    print("  Sonderz._Ende      :    3")
    print("  Sonderz._Anfang    :    4")
    print("  Anfangsb. groß     :    5")
    print("  Datum_Ende         :    6")
    print("")
    print("  Leetspeak          :    9")
    print("")
    print("-d DEFAULT:")
    print("  -i ../fast_output.json -l both -min 5 -max 20 -o password.txt")
    #EXAMPLES:
    return sys.exit()

def set_default(dict_args):
    rules = dict()

    dict_args["filename"] = "../fast_output.json"
    dict_args["language"] = "both"
    dict_args["min_length"] = 5
    dict_args["max_length"] = 20

    # Rules ---
    dict_args["rule"] = ""

    # uppercase_lowercase

    # common_pattern

    return dict_args

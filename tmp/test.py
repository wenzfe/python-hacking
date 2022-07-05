

T= "/tmp/dump_DB.txt"


def get_path(f_name):
    f_path = False
    breaker = False
    try:
        for root, dirs, files in os.walk('/',topdown=True):
            for name in files:
                if name == f_name:
                    f_path = os.path.abspath(os.path.join(root, name))
                    breaker = True 
                    #print("[+] File Path: " + f_path) # 1.W QUEUE
                    return f_path
            if breaker:
                break   
    except:
        pass
    return f_path 
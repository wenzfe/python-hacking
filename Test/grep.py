#!/usr/bin/python3
import argparse
import requests
import json
import re
import concurrent.futures
from urllib.parse import urlparse
import logging
import os
import requests
import zipfile, io
import ast

JOB_LIST = []
BUILD_LIST = []
WS_ZIP_LIST = []
WS_FILE_LIST = []
OUTPUT_JSON = {}
OUTPUT_JSON['build'] = []
OUTPUT_JSON['workspace'] = []
COUNT_WS = COUNT_FILE_DUMP = COUNT_FOUND = 0

# Read Regex FILE
REGEX_FILE = '/home/erik/Desktop/Jenkins/Workspace_Console_Grep/rating_promising_data_patterns'
PATTERN = []
tmp = []
with open(REGEX_FILE) as pattern_data_1:
    for l in pattern_data_1:
        x = l.strip().rstrip(',')
        tmp.append(x)
    pattern_data_1.close()
tmp = tmp[:-1][1:]
y = 1
for i in tmp:
    l = []
    x = i[:-1][1:]
    l.append(x[0])
    l.append(x[2:][:-1][1:])
    y+=1
    PATTERN.append(l)

EXTENSION_FILE = '/home/erik/Desktop/Jenkins/Workspace_Console_Grep/_promising_file_extensions'
extensions_file = open(EXTENSION_FILE, 'r')
_promising_file_extensions = ast.literal_eval(extensions_file.read())

def sanitize_url(url):
    parsed_url = urlparse(url)
    parsed_original_url = urlparse(BASE_URL)
    if FORCE_SSL:
        sanitized = parsed_url._replace(netloc=parsed_original_url.netloc, scheme='https')
    else:
        sanitized = parsed_url._replace(netloc=parsed_original_url.netloc)
    return sanitized.geturl()

def write_out(): # Write to Output File
    with open(OUTPUT_FILE, 'a') as f:
        f.write(json.dumps(OUTPUT_JSON, indent=2))
        f.close()

def sort_prio(location): # Sort Prio 1-5
    if OUTPUT_JSON[location]:
        workspace_list = []
        for i in OUTPUT_JSON[location]:
            workspace_list.append(i)
        workspace_list = sorted(workspace_list, key=lambda k: k.get('prio', 0), reverse=False)
        OUTPUT_JSON[location] = []
        for i in workspace_list:
            OUTPUT_JSON[location].append(i)
    return 

def check_pattern(type, l_line, loaction):
    global COUNT_FOUND
    data_json = {}
    data_json['found'] = []
    find_json = {}
    for pattern in PATTERN:
        if int(pattern[0]) <= int(PRIO): # Check Prio
            for line in l_line:
                result = re.search("%s" % pattern[1], line.strip())
                if result:
                    index = l_line.index(line)
                    if MORE_LINE:
                        data, s_line, e_line = '','',''
                        if index > 0:
                            s_line = l_line[index-1].strip() + "\\n\\n"
                        if index < len(l_line)-1:
                            e_line = "\\n\\n" + l_line[index+1].strip()
                        data = s_line + line + e_line
                    else:
                        data = line
                    find_json['prio'] = int(pattern[0]) 
                    find_json['regex'] = "%s" % pattern[1]
                    find_json['index'] = int(index)
                    #find_json["File"] = item_path
                    if data_json['found']:
                        redundant = False
                        for i in data_json['found']:
                            if data.strip() in i['text'].strip(): # check redundant
                                redundant = True
                        if not redundant:
                            find_json['text'] = data.strip()
                            data_json['found'].append(find_json)
                            COUNT_FOUND += 1                          
                    else:
                        find_json['text'] = data.strip()
                        data_json['found'].append(find_json)
                        COUNT_FOUND += 1
                    find_json = {}
    if data_json['found']:
        data_json['loaction'] = loaction
        OUTPUT_JSON[type].append(data_json)

def dump_jobs(url):
    try:
        r = SESSION.get(url + '/api/json/', verify=False, auth=AUTH, timeout=20)
        #logging.debug(f'dump_jobs request:{r.text}')
    except requests.exceptions.ConnectTimeout:
        print('[ERROR] Connection to the server timed out. Is the server up?')
        exit(1)
    if 'Authentication required' in r.text:
        print('[ERROR] This Jenkins requires authentication')
        exit(1)
    if 'Invalid password/token' in r.text:
        print('[ERROR] Invalid password/token for user')
        exit(1)
    if 'Missing the Overall/Read permission' in r.text:
        print('[ERROR] User has no read permission')
        exit(1)
    resp = json.loads(r.text)
 
    if 'jobs' in resp:
        for job in resp['jobs']:
            try:
                dump_jobs(job['url']) 
                JOB_LIST.append(job['url']) 
            except requests.exceptions.ReadTimeout:
                logging.debug('[ERROR] Gave up on job {} because of a timeout (server is probably busy)'.format(job['name']))
    if 'builds' in resp:
        for build in resp['builds']:
            BUILD_LIST.append(build['url']) 
            if RECOVER_LAST_BUILD_ONLY == True:
                break

def dump_build(url):
    url = sanitize_url(url)
    try:
        r = SESSION.get(url + '/consoleText', verify=False, auth=AUTH, timeout=20,stream=True)
        logging.debug(f'URL: {url}/api/json')
    except requests.exceptions.ReadTimeout:
        logging.debug(f'[ERROR] Gave up on build {url} because of a timeout (server is probably busy)')
    l_list = []
    for line in r.iter_lines():
        l_list.append(line.decode("utf-8"))
    check_pattern('build', l_list, url)

def download_workspace(url):
    global COUNT_WS
    url = sanitize_url(url)
    project_name = url.rsplit('/', 2)[-2]
    try:
        r = SESSION.get(url+'ws/*zip*/filename.zip', verify=False, auth=AUTH, timeout=20)
        logging.debug(f'URL: {url}ws/')     
    except requests.exceptions.ReadTimeout:
        logging.debug(f'[ERROR] Gave up on WS {url}ws/ because of a timeout (server is probably busy)')
    if r.status_code == 200:
        try:
            z = zipfile.ZipFile(io.BytesIO(r.content))
            #print(z.filelist) # See content of zip file
            size_bytes = sum([zinfo.file_size for zinfo in z.filelist])
            #size_kb = float(size) / 1000 
            if size_bytes < ZIP_SIZE and size_bytes > 0:
                logging.info(f"Zip: {project_name} - Size: {size_bytes} Byte")
                COUNT_WS += 1
                z.extractall(OUTPUT_DIR)
            else:
                logging.debug(f"[!] Zip: {url} > {ZIP_SIZE} Bytes ")
        except:
            print(f'Unzip {url}ws/ Fail!')
    else:
        logging.debug(f"[ERROR] Download WS at {url}ws/ with statuscode {r.status_code}")
    exit()

def select_workspace(path): 
    global COUNT_FILE_DUMP
    for item in os.listdir(path):
        item_path = path+"/"+item
        if os.path.isdir(item_path): # It is a directory
            select_workspace(item_path)
        elif os.path.isfile(item_path): #It is a normal file
            item_extension = item.rsplit('.', 1)[-1]
            WS_FILE_LIST.append(item)
            for i in _promising_file_extensions:
                # i[0] extension Prio
                if item_extension == i[1]:
                    COUNT_FILE_DUMP += 1
                    file = open(item_path, 'r', encoding='latin-1')
                    l_line = []
                    for line in file:
                        l_line.append(line.encode("ascii", "ignore").decode())
                    file.close()
                    check_pattern('workspace', l_line, item_path)
        else:  
            logging.debug("[!] It is a special file (socket, FIFO, device file)" )

parser = argparse.ArgumentParser(description = 'Dump all available info from Jenkins')
parser.add_argument('url', nargs='+', type=str)
parser.add_argument('-u', '--user', type=str)
parser.add_argument('-p', '--password', type=str)
parser.add_argument('-o', '--output_file', type=str, nargs='?', default='out.json', help='Default Outputfile: out.json')
parser.add_argument('-d', '--output_dir', type=str, nargs='?', help='Default Directory: ./ws')
parser.add_argument("--debug", help="Debug", const='Debug', nargs='?')
parser.add_argument('-l', '--last', action='store_true', help='Dump only the last build of each job')
parser.add_argument('-P', '--priority', type=int, choices=[1,2,3,4,5], help='Only use Regex with higher priority')
parser.add_argument('-L', '--lines', action='store_true', help='Nummber of lines befor and after the regex match')
parser.add_argument('-f', '--force-ssl', action='store_true', help='Force usage of SSL if API returns wrong HTTP-only links')

args = parser.parse_args()

SESSION = requests.session()
BASE_URL = args.url[0].rstrip('/') + ''

AUTH = None
if args.user and args.password:
    AUTH = (args.user, args.password)
FORCE_SSL = False
if args.force_ssl:
    FORCE_SSL = True
PRIO = 5
if args.priority:
    PRIO = args.priority
RECOVER_LAST_BUILD_ONLY = False
if args.last:
    RECOVER_LAST_BUILD_ONLY = True
if args.output_file:
    OUTPUT_FILE = args.output_file
    f = open(OUTPUT_FILE,"w")
    f.close()
OUTPUT_DIR = "./ws"
if args.output_dir:
    OUTPUT_DIR = args.output_dir.rstrip('/')
try: 
    os.mkdir(OUTPUT_DIR)
except FileExistsError:
    pass
except OSError as e:
    print(e)
    exit(-1)
MORE_LINE = False
if args.lines:
    MORE_LINE = True

#ZIP_SIZE = 100000 # Byte # 100KB # 0,8MB
ZIP_SIZE = 100000000

# Logging
date_strftime_format = "%d-%b-%y %H:%M:%S"
message_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format= message_format, datefmt= date_strftime_format)
logging.getLogger().setLevel(logging.INFO)
if args.debug:
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug('ON')

##### Program Start
logging.info("Programm start\n")
dump_jobs(BASE_URL)
logging.debug("JOBS_LIST - " + str(JOB_LIST))
logging.debug("BUILD_LIST - " + str(BUILD_LIST))

logging.info('[#] Dumping gathered builds')
with concurrent.futures.ThreadPoolExecutor(max_workers=128) as executor:
    executor.map(dump_build, BUILD_LIST)

logging.info('[#] Dumping gathered workspaces local')
with concurrent.futures.ThreadPoolExecutor(max_workers=128) as executor:
    executor.map(download_workspace, JOB_LIST)

select_workspace(OUTPUT_DIR)

print("\n\n-----------------INFO-----------------------")
logging.info(f'Got {len(BUILD_LIST)} builds to dump')
logging.info(f'Downloaded {COUNT_WS} workspaces')
logging.info(f'Got {len(WS_FILE_LIST)} files and dump {COUNT_FILE_DUMP} of it')
logging.info(f'Got {COUNT_FOUND} founds\n')

sort_prio('build')
sort_prio('workspace')
write_out()

logging.info("Program finished")

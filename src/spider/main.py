
import concurrent.futures as cf
from threading import Lock
from queue import Queue
from sys import stdout
from time import sleep
import argparse
import logging
import sys
import os

# import code
from worker import thread_worker


# ToDo: define Request Header

# Thread based Crawler

MAX_WORKERS = 5
REQUEST_TIMEOUT = 60
LOG_LEVEL = 10
FORMAT = '[%(asctime)s] [%(thread)-6d] [%(threadName)-25s] [%(funcName)-15s] [%(levelname)-8s] [%(message)s]'
queue_urls = Queue()


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
            logging.info(f"Current queue size: {queue_urls.qsize()}")

            # check Thread's for errors and log them
            # use list [e.result() for e in res]
            executor.submit(thread_worker, next_url, REQUEST_TIMEOUT, queue_urls, visited, lock_for_Set, PATH)



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

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
    A multithreaded Web Crawler / Spider

        """,
        epilog="""
    Level     | Numeric value 
    --------------------------
    CRITICAL  |   50
    ERROR     |   40
    WARNING   |   30
    INFO      |   20
    DEBUG     |   10
    NOTSET    |    0
        """

    )

    # Software Version
    parser.add_argument('-v', '--version', action='version', 
        version='%(prog)s version: 1.0 \n  https://www.github.com/wenzfe/python-hacking'
    )

    # Number of workers
    parser.add_argument('-w', '--worker',
        default=5,
        type=int,
        metavar='N',
        help='Number of workers / threads to use (default: %(default)s)',
    )

    # Visit external URL's
    parser.add_argument('-visit-ext',
        action=argparse.BooleanOptionalAction,
        type=bool,
        default=False,
        help='Set flag to visit external URLs (default: %(default)s)'
    )

    # Path Data Storage
    parser.add_argument('-p', '--path',
        default=os.getcwd(),
        nargs='?',
        help='The location on your system to store the data (default: %(default)s)'
    )

    # Log level
    parser.add_argument('--log-lvl',
        default=30,
        type=int,
        help='The logging level of the script, control the verbosity of output (default: %(default)s)'
    )

    # Log destination file or console
    parser.add_argument('--log-output',
        nargs='?',
        default=sys.stdout,
        type=argparse.FileType('w'),
        help='The logging output destination (default: stdout)'
    )

    parser.add_argument('-urls',
        nargs='+',
        # required=True,
        metavar='URL',
        type=str,
        help="The URL's to be crawled, in the form http://example.com:80"
    )

    parser.add_argument('--url-paths',
        nargs='+',
        type=str,
        metavar='PATH',
        help='The paths to also use when starting to performe the crawl. Can be absolute or relative'
    )

    parser.add_argument('--request-timeout',
        type=int,
        metavar='SEC',
        default=60,
        help='Number of seconds before request timeout (default: %(default)s)'
    )

    parser.add_argument('--request-proxy',
        type=str,
        metavar="IP",
        help="Specify a proxy to use as a intermediate for requests"
    )

    parser.add_argument('--store-data', # allows multiple times the same value!
        nargs='+',
        choices=['OTHER', 'HTML', 'JS', 'CSS', 'IMAGE'],
        default=['OTHER', 'HTML', 'JS', 'CSS', 'IMAGE'],
        help='Select the data types to be stored'
    )

    args = parser.parse_args()




    logging.basicConfig(filemode="w", filename="spider.log", encoding='utf-8', format=FORMAT, level=LOG_LEVEL)
    # stream=sys.stdout, 
    main()

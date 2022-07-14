
import concurrent.futures as cf
from threading import Lock
from queue import Queue
from sys import stdout
from time import sleep
import argparse
import logging
import os
import json
from urllib.parse import urlparse

# import code
from worker import thread_worker



# ToDo: define Request Header

lock_for_Set = Lock()
visited = set()


def main(max_workers: int, visit_external_url: bool, request_proxy, request_timeout: int, path, store_data: set, urls: list, url_paths: list):
    """
    Main handles URL's and their permutation, spawns threads 
    """
    
    queue_urls = Queue()

    logging.info(f"Using Configuration max_workers: {max_workers} | request-timeout: {request_timeout} | proxys: {request_proxy} | visit-external-url: {visit_external_url}")

    for url in urls:            # add URL's to queue
        queue_urls.put(url)

    for url_path in url_paths:      # add paths to URL's and add them to the queue
        for url in urls:
            assemble_url = urlparse(url)._replace(path=urlparse(url_path).path).geturl()
            queue_urls.put(assemble_url)


    try:
        with cf.ThreadPoolExecutor(max_workers=max_workers) as executor:

            future = []
            while queue_urls.qsize():

                next_url = queue_urls.get()
                logging.info(f"Next job for worker: {next_url}")
                logging.info(f"Number of visited URLs: {len(visited)}")
                logging.info(f"Current queue size: {queue_urls.qsize()}")

                with open(os.path.join(path, 'visited_urls.log'), 'a') as f:
                    f.write(next_url)
                    f.write("\n")
                # check Thread's for errors and log them
                # use list [e.result() for e in res]

                future.append(executor.submit(thread_worker, next_url, request_proxy, request_timeout, queue_urls, visited, lock_for_Set, path, store_data, visit_external_url))
                
                for future_element in cf.wait(future, return_when=cf.FIRST_COMPLETED)[0]: # clean list from finished tasks
                    future.remove(future_element)


    except Exception as exc_main:
        logging.critical(f"main crashed {exc_main}")


def commandline_input():
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

    parser.add_argument('--urls',
        nargs='+',
        required=True,
        metavar='URL',
        type=str,
        help="The URL's to be crawled, in the form http://example.com:80"
    )


    parser.add_argument('--url-paths',
        nargs='?',
        type=str,
        metavar='PATH',
        default=None,
        help='A file containing the paths to use when starting to performe the crawl.'
    )


    # Visit external URL's
    parser.add_argument('--visit-ext',
        action=argparse.BooleanOptionalAction,
        type=bool,
        default=False,
        help='Set flag to visit external URLs (default: %(default)s)'
    )


    # Number of workers
    parser.add_argument('-w', '--worker',
        default=5,
        type=int,
        metavar='N',
        help='Number of workers / threads to use (default: %(default)s)',
    )


    # Path Data Storage
    parser.add_argument('-p', '--path',
        default=os.getcwd(),
        nargs='?',
        help='The location on your system to store the data (default: %(default)s)'
    )


    parser.add_argument('--store-data', # allows multiple times the same value!
        nargs='*',
        choices=['OTHER', 'HTML', 'JS', 'CSS', 'IMAGE', 'LINK'],
        default=['OTHER', 'HTML', 'JS', 'CSS', 'IMAGE', 'LINK'],
        help='Select the data types to be stored (default: %(default)s)'
    )


    # Log level
    parser.add_argument('--log-lvl',
        default=20,
        type=int,
        help='The logging level of the script, control the verbosity of output (default: %(default)s)'
    )


    # Log destination file or console
    parser.add_argument('--log-output',
        nargs='?',
        default='-',
        type=argparse.FileType('w'),
        help='The logging output destination (default: stdout)'
    )


    parser.add_argument('--request-timeout',
        type=int,
        metavar='SEC',
        default=60,
        help='Number of seconds before request timeout (default: %(default)s)'
    )


    parser.add_argument('--request-proxy',
        type=str,
        metavar="JSON",
        help="Specify a json file containing the proxy to use as a intermediate for requests"
    )


    # Software Version
    parser.add_argument('-v', '--version', action='version', 
        version='%(prog)s version: 1.0 \n  https://www.github.com/wenzfe/python-hacking'
    )

    return parser.parse_args()



if __name__ == '__main__':

    args = commandline_input()
    
    FORMAT = '[%(asctime)s] [%(thread)-6d] [%(threadName)-25s] [%(funcName)-15s] [%(levelname)-8s] [%(message)s]'
    logging.basicConfig(stream=args.log_output, encoding='utf-8', format=FORMAT, level=args.log_lvl)

    logging.debug(f"Supplied command line arguments: {args}")

    # if specified read url-path file
    url_paths = []
    if args.url_paths != None:
        with open(args.url_paths, "r") as f:
            url_paths = f.read().splitlines()
    
    # if specified read proxy file
    proxy = None
    if args.request_proxy != None:
        with open(args.request_proxy, "r") as f:
            proxy = json.loads(f.read())
        

    main(args.worker, args.visit_ext, proxy, args.request_timeout, args.path, set(args.store_data), args.urls, url_paths)

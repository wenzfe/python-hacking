
import concurrent.futures as cf
from threading import Lock
from queue import Queue
from sys import stdout
from time import sleep
import argparse
import logging
import os

# import code
from worker import thread_worker



# ToDo: define Request Header

lock_for_Set = Lock()
visited = set()


def main(max_workers, visit_external_url, request_proxy, request_timeout, path, urls, url_paths):
    queue_urls = Queue()

    logging.info(f"Using Configuration max_workers: {max_workers} | request-timeout: {request_timeout} | visit-external-url: {visit_external_url}")

    for e in urls:
        queue_urls.put(e)

    try:
        with cf.ThreadPoolExecutor(max_workers=max_workers) as executor:

            future = []
            while queue_urls.qsize():

                next_url = queue_urls.get()
                logging.info(f"Next job for worker: {next_url}")
                logging.info(f"Number of visited URLs: {len(visited)}")
                logging.info(f"Current queue size: {queue_urls.qsize()}")

                # check Thread's for errors and log them
                # use list [e.result() for e in res]

                future.append(executor.submit(thread_worker, next_url, request_timeout, queue_urls, visited, lock_for_Set, path, visit_external_url))
                
                future_completed_iterator = cf.wait(future, return_when=cf.FIRST_COMPLETED)[0]
                print(future_completed_iterator, "z47")

                for future_element in cf.wait(future, return_when=cf.FIRST_COMPLETED)[0]: # clean list from finished tasks
                    future.remove(future_element)
                logging.info(f"Current queue size: (z60) {queue_urls.qsize()}")


    except Exception as exc_main:
        logging.critical(f"main crashed {exc_main}")


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
    parser.add_argument('--visit-ext',
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
        default=0,
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


    parser.add_argument('--urls',
        nargs='+',
        required=True,
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
    print(args)


    FORMAT = '[%(asctime)s] [%(thread)-6d] [%(threadName)-25s] [%(funcName)-15s] [%(levelname)-8s] [%(message)s]'
    logging.basicConfig(stream=args.log_output, encoding='utf-8', format=FORMAT, level=args.log_lvl)


    main(args.worker, args.visit_ext, args.request_proxy, args.request_timeout, args.path, args.urls, args.url_paths)

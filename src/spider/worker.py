from urllib.parse import urlparse
from requests_html import HTMLSession
from threading import Lock
from queue import Queue
import logging
from typing import TypedDict, List

from re import fullmatch, match

# import asyncio

class Crawled(TypedDict):
    html: str
    links: List[str]
    css: List[str]
    js: List[str]
    images: List[str]
    images_data: List[str]

def crawl_page(url: str) -> Crawled:
    """
    Crawl the specivied url, extract html and embedded images and also urls and urls for css, js, images resources. 
    """

    session = HTMLSession()
    r = session.get(url)

    return {
        'html': r.html.html,
        'links': r.html.absolute_links,
        'css': [e.attrs['href'] for e in r.html.find('link[href$=".css"]')],
        'js': [e.attrs['src'] for e in r.html.find('script[src]')],
        'images': [e.attrs['src'] for e in r.html.find('img[src^="http"]')], 
        'images_data': [e.attrs['src'] for e in r.html.find('img[src^="data:"]')]
    }

def fill_queue(origin_url: str, new_urls: List[str], queue: Queue, visited: set, visit_external_url=False):
    logging.info(f"[{origin_url}] found {len(new_urls)} urls")
    for current_link in new_urls:
        link = urlparse(current_link)
        next_url_candidate = f"{link.scheme}://{link.netloc}{link.path}"
        if next_url_candidate not in visited:   # prevent revisiting of a url
            if visit_external_url == True or urlparse(origin_url).netloc == link.netloc:
                logging.debug(f"{origin_url} new queue entry: {next_url_candidate}")
                queue.put(next_url_candidate)    # add new elements to queue

def thread_worker( url: str, timeout: int, queue: Queue, visited: set, lock: Lock, visit_external_url=False):
        logging.info(f"[{url}] Start working")
        input_url = urlparse(url)
        input_url = f"{input_url.scheme}://{input_url.netloc}/"
        try:                    # crawl the page at the specified url
            result_page = crawl_page(url) 
        except Exception as exc_crawl_page:
            logging.error(exc_crawl_page)
        else:
            try:                # fill queue
                fill_queue(url, result_page['links'], queue, visited, visit_external_url)                
            except Exception as exc_fill_queue:
                logging.error(exc_fill_queue)
            else:
                pass                                                        
                                    # download & store

            with lock:              # update blacklist
                visited.add(url)        # mark url as visited


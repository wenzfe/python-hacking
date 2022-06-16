import collections
from pkgutil import extend_path
from urllib.parse import urlparse
from requests_html import HTMLSession
from threading import Lock
from queue import Queue
import logging
from typing import TypedDict, List
from re import fullmatch, match
from requests import get
from uuid import uuid4
import os

from collections.abc import Iterator 

import asyncio

class Crawled(TypedDict):
    html: List[str]
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
        'html': [r.html.html],
        'links': r.html.absolute_links,
        'css': [e.attrs['href'] for e in r.html.find('link[href$=".css"]')],
        'js': [e.attrs['src'] for e in r.html.find('script[src]')],
        'images': [e.attrs['src'] for e in r.html.find('img[src^="http"]')], 
        'images_data': [e.attrs['src'] for e in r.html.find('img[src^="data:"]')]
    }


def fill_queue(origin_url: str, new_urls: List[str], queue: Queue, visited: set, visit_external_url=False):
    logging.info(f"{origin_url} found {len(new_urls)} URLs")
    for current_link in new_urls:
        link = urlparse(current_link)
        next_url_candidate = f"{link.scheme}://{link.netloc}{link.path}"
        if next_url_candidate not in visited:   # prevent revisiting of a url
            if visit_external_url == True or urlparse(origin_url).netloc == link.netloc:
                queue.put(next_url_candidate)    # add new elements to queue


def store_stream(chunk_iterator: Iterator, name: str, path: str):
    try:
        with open(os.path.join(path, name), "wb") as file:
            for chunk in chunk_iterator:
                file.write(chunk)
    except Exception as ecx_write_file:
        logging.error(ecx_write_file)


def store_data(data: str, name: str, path: str):
    try:
        with open(os.path.join(path, name), "w") as file:
            file.write(data)
    except Exception as ecx_write_file:
        logging.error(ecx_write_file)    
    

def download_file(url: str, chunk_size=128) -> Iterator: 
    scheme_http = "http:"
    scheme_https = "https:"
    if not url.startswith(scheme_http) and not url.startswith(scheme_https):
        logging.warning(f"Missing scheme for {url} trying with {scheme_http}")
        url = scheme_http + url
    try:
        r = get(url)
    except Exception as exc_download:
        logging.error(exc_download)
    else:
        return r.iter_content(chunk_size=chunk_size)


def store_data_type_by_url(objects: list, path: str, dir: str):
    """
    Creates a directory and stores the passed data in it.
    """
    extend_path = os.path.join(path, dir)
    os.makedirs(extend_path, exist_ok=True)   # Create Directory for data type

    for element in objects:
        store_stream(download_file(element), str(uuid4()), extend_path)


def store_data_type_by_data(objects: list, path: str, dir: str, file_extension: str):
    """

    """
    extend_path = os.path.join(path, dir)
    os.makedirs(extend_path, exist_ok=True)   # Create Directory for data type

    for element in objects:
        # specify file name + type
        store_data(element, str(uuid4()) + file_extension, extend_path)
        


def thread_worker( url: str, timeout: int, queue: Queue, visited: set, lock: Lock, base_path: str, visit_external_url=False):
        logging.info(f"{url} Start working")
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

                try:
                    dirname = uuid4()
                    extended_path = os.path.join(base_path, str(dirname))
                    os.makedirs(extended_path, exist_ok=True)


                    # store_data_type(XdataX, "OTHER")
                    store_data_type_by_data(result_page['html'], extended_path, "HTML", ".html")
                    store_data_type_by_url(result_page['css'], extended_path, "CSS")
                    store_data_type_by_url(result_page['js'], extended_path, "JS")
                    store_data_type_by_url(result_page['images'], extended_path, "IMAGE")
                    # 
                except Exception as exc_store_data:
                    logging.error(exc_store_data)
                else:
                    with lock:                  # update blacklist
                        visited.add(url)        # mark url as visited


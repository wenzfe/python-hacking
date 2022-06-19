from urllib.parse import urlparse, urlsplit
from requests_html import HTMLSession
from collections.abc import Iterator 
from typing import TypedDict, List
from threading import Lock
from queue import Queue
import mimetypes
import logging
from re import fullmatch, match
from requests import get
from uuid import uuid4
import os



class Crawled(TypedDict):       # Return type of function: crawl_page
    html: List[str]
    links: List[str]
    css: List[str]
    js: List[str]
    images: List[str]
    images_data: List[str]


def resolve_url(src_url: str, url: str):
    """
    Take a source URL and resolve other missing parts on the other URL 
    """
    
    src = urlsplit(src_url)._replace(path="")._replace(query="")._replace(fragment="")
    target = urlsplit(url)

    if target.netloc == '':     # missing domain
        target = target._replace(netloc=src.netloc)
    
    if target.scheme == '':     # missing protocol
        target = target._replace(scheme=src.scheme)

    return  target.geturl()


def crawl_page(url: str, timeout: int, proxy: dict) -> Crawled:
    """
    Crawl the specivied URL. Extract html and embedded images also URLs to other Pages / Websites and URLs to css, js, images resources. 
    """

    session = HTMLSession()
    r = session.get(url)

    return {
        'html': [r.html.html],
        'links': r.html.absolute_links,
        'css': [resolve_url(url, e.attrs['href']) for e in r.html.find('link[href$=".css"]')],
        'js': [resolve_url(url, e.attrs['src']) for e in r.html.find('script[src]')],
        'images': [resolve_url(url, e.attrs['src']) for e in r.html.find('img[src^="http"]')],
        'images_data': [e.attrs['src'] for e in r.html.find('img[src^="data:"]')]
    }


def fill_queue(origin_url: str, new_urls: List[str], queue: Queue, visited: set, lock: Lock, visit_external_url=False):
    logging.debug(f"{origin_url} found {len(new_urls)} URLs")
    try:
        for current_link in new_urls:
            link = urlparse(current_link)
            next_url_candidate = f"{link.scheme}://{link.netloc}{link.path}"

            with lock:
                is_next_url_candidate_in_visited = next_url_candidate not in visited
                is_subdomain = link.netloc.endswith(urlparse(origin_url).netloc)

                add_entry = ( is_next_url_candidate_in_visited and ( visit_external_url or is_subdomain ) )
                logging.info(f"Checking {next_url_candidate} adding {add_entry}: is visited: {is_next_url_candidate_in_visited} AND ( allow external URL: {visit_external_url} OR is subdomain: {is_subdomain} )")
                # prevent revisiting of a URL   AND   ( external URL    OR  subdomain )
                if add_entry:
                    queue.put(next_url_candidate)    # add new elements to queue



    except Exception as exc_fill_queue:
        logging.critical(f"Encountered error while trying to fill the queue {exc_fill_queue}")


def store_stream(chunk_iterator: Iterator, name: str, path: str):
    try:
        with open(os.path.join(path, name), "wb") as file:
            for chunk in chunk_iterator:
                file.write(chunk)
    except Exception as ecx_write_file:
        logging.error(ecx_write_file)


def store_data(data: str, name: str, path: str):
    try:
        with open(os.path.join(path, name), "bw") as file:
            file.write(data.encode())
    except Exception as ecx_write_file:
        logging.error(ecx_write_file)    


def download_file(url: str, timeout: int, proxy: dict, chunk_size=128) -> Iterator: 
    """
    (mimetype, stream iterator)
    """
    scheme_http = "http:"
    scheme_https = "https:"
    logging.info(f"Attempt download of {url}")
    if not url.startswith(scheme_http) and not url.startswith(scheme_https):
        logging.warning(f"Missing scheme for {url} trying with {scheme_http}")
        url = scheme_http + url
    try:
        r = get(url)
    except Exception as exc_download:
        logging.error(exc_download)
    else:
        content_type = r.headers.get('content-type').split(";")[0]
        guess_mime_type = mimetypes.guess_extension(content_type)

        if guess_mime_type == None:
            guess_mime_type = ".unknown"
            logging.warning(f"Encountered unknown mimetype from content-type {content_type} at {url}")

        return (guess_mime_type, r.iter_content(chunk_size=chunk_size))


def store_data_type_by_url(objects: list, path: str, dir: str, timeout, proxy):
    """
    Creates a directory and stores the passed data in it.
    """
    try:
        extend_path = os.path.join(path, dir)
        os.makedirs(extend_path, exist_ok=True)   # Create Directory for data type
    except Exception as exc_create_dir:
        logging.critical(f"Encountered error while attempting to create a directory: {exc_create_dir}")
    else:

        for element in objects:
            mimetype, iterator = download_file(element, timeout, proxy)
            store_stream(iterator, str(uuid4()) + mimetype, extend_path)


def store_data_type_by_data(objects: list, path: str, dir: str, file_extension: str):
    """

    """
    try:
        extend_path = os.path.join(path, dir)
        os.makedirs(extend_path, exist_ok=True)   # Create Directory for data type
    except Exception as exc_create_dir:
        logging.critical(f"Encountered error while attempting to create a directory: {exc_create_dir}")
    else:
        for element in objects:
            # specify file name + type
            store_data(element, str(uuid4()) + file_extension, extend_path)


def thread_worker( url: str, proxy: dict, timeout: int, queue: Queue, visited: set, lock: Lock, base_path: str, store_data: set, visit_external_url=False):
        logging.info(f"{url} Start working")
        input_url = urlparse(url)
        input_url = f"{input_url.scheme}://{input_url.netloc}/"
        try:                    # crawl the page at the specified url
            result_page = crawl_page(url, timeout, proxy) 
        except Exception as exc_crawl_page:
            logging.error(exc_crawl_page)
        else:
            try:                # fill queue
                fill_queue(url, result_page['links'], queue, visited, lock, visit_external_url)                
            except Exception as exc_fill_queue:
                logging.error(exc_fill_queue)
            else:

                try:

                    if len(store_data) != 0:
                        dirname = uuid4()
                        extended_path = os.path.join(base_path, str(dirname))
                        os.makedirs(extended_path, exist_ok=True)

                    if 'LINK' in store_data:
                        with open(os.path.join(extended_path, "page.txt"), "w") as file:
                            file.write(url)

                    # store_data_type(XdataX, "OTHER")

                    if 'HTML' in store_data:
                        store_data_type_by_data(result_page['html'], extended_path, "HTML", ".html")

                    if 'CSS' in store_data:
                        store_data_type_by_url(result_page['css'], extended_path, "CSS", timeout, proxy)

                    if 'JS' in store_data:
                        store_data_type_by_url(result_page['js'], extended_path, "JS", timeout, proxy)

                    if 'IMAGE' in store_data:
                        store_data_type_by_url(result_page['images'], extended_path, "IMAGE", timeout, proxy)


                except Exception as exc_store_data:
                    logging.error(exc_store_data)
                else:
                    with lock:                  # update blacklist
                        visited.add(url)        # mark url as visited


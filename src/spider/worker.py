from urllib.parse import urlparse
from requests_html import HTMLSession
from threading import Lock
from queue import Queue
import logging
from typing import TypedDict, List

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
    Crawl a url
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



def thread_worker( url: str, timeout: int, queue: Queue, visited: set, lock: Lock, visit_external_url=False):
        logging.info(f"[{url}] Start working")
        result_page = crawl_page(url) # crawl the page at the specified url

        # fill Queue 
        for current_link in result_page['links']:
            parsed_link = urlparse(current_link)
            parsed_url = f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}"
            if parsed_url not in visited: # prevent re visiting of a url
                if visit_external_url == True or urlparse(url).netloc in parsed_url :
                    logging.debug(f"[{url}] new queue entry: {parsed_url}")
                    queue.put(parsed_url)    # add new elements to queue            
                
        # download & store


        # update blacklist
        with lock:
            visited.add(url)    # mark url as visited
        


    

if __name__ == '__main__':
    res = crawl_page("http://www.google.com")
    for e in res['links']:
        print(e)



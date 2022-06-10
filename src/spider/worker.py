from requests_html import HTMLSession
from typing import TypedDict

import asyncio

class Crawled(TypedDict):
    html: str
    links: List[str]
    css: List[str]
    js: List[str]
    images: List[str]
    images_data: List[str]

def crawl(url: str) -> Crawled:
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


if __name__ == '__main__':
    res = crawl("http://domain.example")

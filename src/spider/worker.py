from requests_html import HTMLSession
import asyncio


def crawl(url: str):
    """
    Crawl a url
    Arguments:
        url: string
    Returns:
        Dictionary with links: [URLs], html: [code], css: [URLs], js: [URLs], images; [URLs | data}
    """

    session = HTMLSession()
    r = session.get(url)

    return {
        'html': r.html.html,
        'links': r.html.links,
        'css': [e.attrs['href'] for e in r.html.find('link[href$=".css"]')],
        'js': [e.attrs['src'] for e in r.html.find('script[src]')],
        'images': [e.attrs['src'] for e in r.html.find('img[src]')] # can contain encoded data e.g src="data:image/png;base64(...)"
    } 


if __name__ == '__main__':
    res = crawl()


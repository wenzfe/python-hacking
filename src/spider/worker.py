from requests_html import AsyncHTMLSession
import asyncio
import json


async def crawl(url):
    """
    Crawl a url
    Arguments:
        url: string
    Returns:
        JSON Object with links, html, css, js, images
    """

    asession = AsyncHTMLSession()
    
    r = await asession.get(url)
    for e in r.html.find('style'): # Link tag geht auch
        print(e)




    return {
        'links': r.html.links,
        'html': r.html.html,
        'css': None,
        'js': None,
        'images': None
    } 


if __name__ == '__main__':
    asyncio.run(crawl("www.google.com"))

#!/usr/bin/python3

#from queue import Queue
import argparse
import asyncio
import json
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession  # Install

# async def crawl(s,url):
#     # """
#     # Crawl a url
#     # Arguments:
#     #     url: string
#     # Returns:
#     #     JSON Object with links, html, css, js, images
#     #""""
#     r = await s.get(url)
#     soup = BeautifulSoup(r.content, features='lxml')
#     soup_script = soup.find_all('script', src=True)
#     for i in soup_script:
#         print(i['src'])
#     soup_link = soup.find_all('link', href=True)
#     for i in soup_link:
#         print(i['href'])

async def spider(s,post_link):
    print(post_link)


def save_json(dict_output):
    with open('post_output.json', 'w') as outfile:
        json.dump(dict_output, outfile,  indent=2, ensure_ascii=False)

async  def main():
    s = AsyncHTMLSession()
    url_posts = URL + "/wp-json/wp/v2/posts?per_page=100"
    posts = await s.get(url_posts)
    posts_json = json.loads(posts.text)
    #print(json.dumps(posts_json, indent=2, sort_keys=True))
    save_json(posts_json)
    list_linktarget = []
    for p in posts_json:
        #print(p['link'])
        list_linktarget.append(p['link'])
        pass
    #exit()
    print(f"Nummber of Total Posts: {len(list_linktarget)}")
    tasks = (spider(s, post_link) for post_link in list_linktarget)
    
    return await asyncio.gather(*tasks)


if __name__ == '__main__':
    global BASE_URL
    print("Start...")
    parser = argparse.ArgumentParser(description = 'Dump all available info from Jenkins')
    parser.add_argument('--url', required=True, type=str, help='Start Url')
    args = parser.parse_args()

    URL = args.url.rstrip('/')

    asyncio.run(main())
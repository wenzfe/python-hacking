from requests_html import AsyncHTMLSession
import asyncio






async def main():
    # input url
    url = "https://www.google.com"
    print("----")

    asession = AsyncHTMLSession()
    r = await asession.get(url)
    print(r.html.links)

    # output [ html, css, js, images ]    
    return


if __name__ == '__main__':
    asyncio.run(main())

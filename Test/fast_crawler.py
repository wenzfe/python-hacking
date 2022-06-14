#! /usr/bin/python3
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession
import asyncio
import json
import re

#Spider on /standort-detailseite-XXXXX.html
async def spider(s, linktarget):
    dict_infos = dict()
    #if linktarget[0] == "https://group.mercedes-benz.com/karriere/ueber-uns/standorte/standort-detailseite-5242.html":

    linktarget_de = linktarget[0]
    linktarget_en = linktarget[1]
    
    page = await s.get(linktarget_de)
    soup = BeautifulSoup(page.text, 'lxml')
    lists = soup.find('div', class_="location-detail-wrapper")
    dict_infos["linktarget"] = linktarget_de

    # Stadtname
    city = soup.find('h1').text
    dict_infos["name"] = city.strip()
    print("> "+dict_infos["name"])
    
    # Company-logo
    logo = lists.find('img')
    if (logo is None) != True:
        dict_infos["logo"] = logo['src']
    else:
        dict_infos["logo"] = None
    
    # Mitarbeiteranzahl, Grundungsjahr, Offene Stellen, Benefits
    all_info = lists.find_all('div', class_="info-item")
    given=["offene stellen","benefits","gründungsjahr", "mitarbeiteranzahl"]
    for i in all_info:
        info = i.find_all('p')
        name = info[0].text.lower().replace(":","")
        if name == "offene stellen":
            href = info[1].find_all('a', href=True)
            dict_infos[name] = href[0]['href']
            given.remove(name)
        elif name == "benefits":
            all_benefits = lists.find_all('div', class_="benefit-icon")  
            list_benefits = []
            for benefit in all_benefits:
                list_benefits.append(benefit['data-benefit'].replace("\xad",""))
            dict_infos[name] = list_benefits
            given.remove(name)
        elif name == "gründungsjahr" or name == "werksgründung":
            dict_infos["gründungsjahr"] = int(info[1].text)
            given.remove("gründungsjahr")
        elif name == "mitarbeiteranzahl" or "mitarbeiter" in name:
            num = re.findall(r'\b\d+\b',info[1].text.replace(".","")) # Zahl aus "< 700" oder "~ 100" ziehen
            dict_infos['mitarbeiteranzahl'] = int(num[0])
            given.remove("mitarbeiteranzahl")
    for i in given:
        dict_infos[i] = None

    # Besucheradresse, Postadresse
    all_address = lists.find_all('div', class_="address-item")
    for i in all_address:
        address = i.find_all('p')
        dict_infos[address[0].text.lower()] = address[1].text.replace("\n",' ').strip()    

    # Webseite Link
    link = lists.find('a', class_="wb-link wb-link--inline")
    if (link is None) != True:
        dict_infos["webseite"] = link['href']
    else:
        dict_infos["webseite"] = None

    # Beschreibungstext
    container_text = soup.find_all('div', class_="article-copy body-template-container")
    if container_text: # items in list
        str_beschreiung = ""
        for i in container_text:
            str_beschreiung+= i.text.replace("\n","").strip()
        dict_infos["beschreibung"] = str_beschreiung
        # English Description
        page_en = await s.get(linktarget_en)
        soup_en = BeautifulSoup(page_en.text, 'lxml')
        container_text = soup_en.find_all('div', class_="article-copy body-template-container")
        str_beschreiung = ""
        for i in container_text:
            str_beschreiung+= i.text.replace("\n","").strip()
        dict_infos["description"] = str_beschreiung
    else: 
        dict_infos["beschreibung"] = None
        dict_infos["description"] = None

    # bilder-links in beschreibung
    container_main = soup.find("div", class_="page-main-inner-content")
    container_img = container_main.find_all("noscript")
    if container_img: # items in list
        img_links = []
        for i in container_img:
            img_links.append(i.img['src'])
        dict_infos["bilder"] = img_links
    else:
        dict_infos["bilder"] = None
    
    #dict in form bringen
    key_order= ['name', 'logo', 'linktarget', 'mitarbeiteranzahl','gründungsjahr','postadresse','besucheradresse',
    'benefits', 'offene stellen', 'webseite','bilder', 'beschreibung', 'description']
    for k in key_order:
        dict_infos[k] = dict_infos.pop(k)

   
    return result["data"].append(dict_infos)

def save_json(dict_output):
    with open('fast_output.json', 'w') as outfile:
        json.dump(dict_output, outfile,  indent=2, ensure_ascii=False)

async def main(target_url):
    s = AsyncHTMLSession()
    page = await s.get(target_url)
    soup = BeautifulSoup(page.text, 'lxml')

    # grep locationsObj
    lists = soup.find(lambda tag:tag.name=="script" and "locationsObj" in tag.text)
    locationObj = lists.text.replace("<br />", "").strip()[19:]
    dict_locationObj = json.loads(locationObj)
    list_linktarget = []
    for locations in dict_locationObj['locations']:
        for countries in locations['countries']:
            for cities in countries['cities']:
                num = re.findall(r'\b\d+\b',cities["linktarget"])
                linktarget_de = "https://group.mercedes-benz.com/karriere/ueber-uns/standorte/standort-detailseite-"+str(num[0])+".html"
                linktarget_en = "https://group.mercedes-benz.com/careers/about-us/locations/location-detail-page-"+str(num[0])+".html"
                list_linktarget.append((linktarget_de,linktarget_en))
                
    tasks = (spider(s, url) for url in list_linktarget)

    return await asyncio.gather(*tasks)

result = {'data' : []}

if __name__ == '__main__':
    target_url = "https://group.mercedes-benz.com/karriere/ueber-uns/standorte/"
    asyncio.run(main(target_url))

    save_json(result)
    print("\n...End")
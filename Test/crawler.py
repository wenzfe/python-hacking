#! /usr/bin/python3
from bs4 import BeautifulSoup
import requests
import json
import re
#from concurrent.futures import ThreadPoolExecutor
#import concurrent.futures as futures

#Spider on /standort-detailseite-XXXXX.html
def spider(linktarget, s):
    linktarget_de = linktarget
    num = re.findall(r'\b\d+\b',linktarget_de)
    linktarget_en = "https://group.mercedes-benz.com/careers/about-us/locations/location-detail-page-"+str(num[0])+".html"
    print("---> linktarget: "+linktarget_de)
    dict_infos = dict()
    page = s.get(linktarget_de)
    soup = BeautifulSoup(page.content, 'lxml')
    lists = soup.find('div', class_="location-detail-wrapper")

    # Titel - Stadtname
    # city = soup.find('h1').text
    # dict_infos["Stadtname"] = city.strip()

    # Company-logo
    logo = lists.find('img')
    if (logo is None) != True:
        dict_infos["logo"] = logo['src']
    else:
        dict_infos["logo"] = None

    # Infos - Mitarbeiteranzahl, Grundungsjahr, Offene Stellen, Benefits
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
        elif name == "gründungsjahr":
             dict_infos[name] = int(info[1].text)
             given.remove(name)
        elif name == "mitarbeiteranzahl" or name == "mitarbeiter" :
            num = re.findall(r'\b\d+\b',info[1].text.replace(".","")) # Zahl aus "< 700" oder "~ 100" ziehen
            dict_infos['mitarbeiteranzahl'] = int(num[0])
            given.remove("mitarbeiteranzahl")
    for i in given:
        dict_infos[i] = None

    # Besucheradresse, (find_all für Postadresse)
    all_address = lists.find('div', class_="address-item")
    address = all_address.find_all('p')
    dict_infos["besucheradresse"] = address[1].text.replace("\n",' ').strip()       

    # Webseite Link
    link = lists.find('a', class_="wb-link wb-link--inline external")
    if (link is None) != True:
        dict_infos["webseite"] = link.text
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
        page_en = s.get(linktarget_en)
        soup_en = BeautifulSoup(page_en.content, 'lxml')
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
    
    return dict_infos

def edit_json(object_string, s):
    object_dict = json.loads(object_string)
    for locations in object_dict['locations']:
        print("> locations: "+locations["name"])
        for countries in locations['countries']:
            print("=> countries: "+countries["name"])
            for cities in countries['cities']:
                print("==> cities: "+cities['name'])
                # Uberschreiben von Keys
                cities['postadresse'] = cities.pop('address')
                cities['postadresse'] = cities['postadresse'].strip()
                del cities['city']
                if cities['tel'].strip() == "":
                    cities['tel'] = None
                if cities['email'].strip() == "":
                    cities['email'] = None
                cities["linktarget"] = "https://group.mercedes-benz.com"+cities["linktarget"]
                dict_infos = spider(cities["linktarget"], s)
                cities.update(dict_infos)
                # dict in form bringen
                key_order= ['name', 'logo', 'linktarget', 'mitarbeiteranzahl','gründungsjahr','postadresse','besucheradresse',
                'benefits', 'offene stellen', 'webseite','bilder', 'beschreibung', 'description', 'tel', 'email']
                for k in key_order:
                    cities[k] = cities.pop(k)
    return object_dict
   
def get_locationsObj(url):
    s = requests.Session()
    page = s.get(url)
    soup = BeautifulSoup(page.content, 'lxml')
    # grep locationsObj
    lists = soup.find(lambda tag:tag.name=="script" and "locationsObj" in tag.text)
    locationObj = lists.text.replace("<br />", "").strip()[19:]
    return edit_json(locationObj, s) 

def save_json(dict_output):
    with open('output.json', 'w') as outfile:
        json.dump(dict_output, outfile,  indent=2, ensure_ascii=False)

def main():
    target_url = "https://group.mercedes-benz.com/karriere/ueber-uns/standorte/"
    output = get_locationsObj(target_url)
 
    # -- Test
    #test_url1 = "https://group.mercedes-benz.com/karriere/ueber-uns/standorte/standort-detailseite-5114.html"
    #test_url2 = "https://group.mercedes-benz.com/karriere/ueber-uns/standorte/standort-detailseite-5140.html"
    #test_url3 = "https://group.mercedes-benz.com/karriere/ueber-uns/standorte/standort-detailseite-18163.html"
    #output = spider(test_url2)
    #print("\n\n")
    #print(json.dumps(output,indent =4, ensure_ascii=False))

    save_json(output)
    print("\n\n...End")
    return

if __name__ == "__main__":
    main()
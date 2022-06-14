# Daimer-WebCrawler
Der Web-Crawler soll in der Lage sein, alle Informationen über die Standorte, welche sich auf folgender Seite befinden, zu sammeln.
* https://group.mercedes-benz.com/karriere/ueber-uns/standorte/
## Scope :
**Locations:** [ Afrika, Asien, Australien & Pazifik, Europa, Nord- & Mittelamerika, Südamerika ]

**Anzahl cties:** 300

----

## fast_crawler.py
Run time: ~ 0m30

**Informations:** ['name', 'logo', 'linktarget', 'mitarbeiteranzahl','gründungsjahr','postadresse','besucheradresse', 'benefits', 'offene stellen', 'webseite','bilder', 'beschreibung', 'description']
### Usage:
````
python3 fast_crawler.py
````
#### fast_output.json
```json
{
  "data": [
<SNIP>
   {
    "name": "Ulm, Daimler TSS GmbH",
    "logo": "/bilder/karriere/logos/daimler-tss-logo-w180xh100.jpg",
    "linktarget": "https://group.mercedes-benz.com/karriere/ueber-uns/standorte/standort-detailseite-5074.html",
    "mitarbeiteranzahl": 450,
    "gründungsjahr": 1998,
    "postadresse": "Wilhelm-Runge-Str. 11 89081 Ulm",
    "besucheradresse": "Wilhelm-Runge-Str. 11 89081 Ulm",
    "benefits": [
      "Gute Anbindung",
      "Parkplatz",
      "Kantine",
      "Barrierefreiheit",
      "Betriebsarzt",
      "Mitarbeiter Events",
      "Gesundheitsmaßnahmen",
      "Homeoffice möglich",
      "Mitarbeiterrabatte möglich",
      "Mitarbeiterhandy möglich",
      "Internetnutzung"
    ],
    "offene stellen": "/karriere/jobsuche/?action=doSearch&job_genesis_id=9953&job_location=1705&job_location_name=Ulm%2C+Daimler+TSS+GmbH&job_global_location=DE89081A,DE89081E,DE89081C,",
    "webseite": null,
    "bilder": [
      "/bilder/karriere/ueber-uns/standorte/tss-deutschland-2019-2-w614xh345-cutout-2.jpg",
      "/bilder/karriere/ueber-uns/standorte/tss-deutschland-2019-4-w614xh345-cutout.jpg",
      "/bilder/karriere/ueber-uns/standorte/tss-deutschland-2019-3-w614xh345-cutout.jpg"
    ],
    "beschreibung": "1998 als kleines Software-Spin-off gestartet, gestalten wir heute mit über 1200 Mitarbeitern an den Standorten Ulm, Stuttgart, Berlin, Karlsruhe, Kuala Lumpur (Malaysia) und Peking (China) die IT von morgen. Dabei legen wir großen Wert auf menschliche wie digitale Vernetzung. Leidenschaft für IT und eine nach wie vor familiäre Start-up-Kultur verbinden uns und sorgen für Gemeinschaft und kreativen Freiraum im Arbeitsalltag.Wir denken partnerschaftlich und agil, entscheiden technologieneutral und herstellerunabhängig. Das macht uns frei für neue, innovative Ideen und die Aufnahme wichtiger Trends und Impulse in einer sich rasant wandelnden digitalen Welt. Angetrieben von diesen Ideen wagen wir uns auf der Suche nach den besten Lösungen in unseren diversen Teams immer wieder über Grenzen hinweg und generieren überzeugende Ergebnisse.Durchschnitt? Eher nicht! Typisch Daimler TSS.",
    "description": "Daimler TSS. IT excellence: Comprehensive, innovative, close.Having started as a small software spin-off in 1998, we now shape tomorrow's IT with over 1200 employees at our locations in Ulm, Stuttgart, Berlin and Karlsruhe, as well as at our project hubs in Kuala Lumpur (Malaysia) and Beijing (China). We attach great importance to both human and digital networking in this respect. Passion for IT and a still very intimate start-up culture unite us in these endeavors, ensuring a sense of community and creative freedom in everyday working life.We think and act in a spirit of partnership. We are also agile, technologically neutral and manufacturer-independent. This ensures our openness to new, innovative ideas and the assimilation of significant trends and impulses in a rapidly changing digital world. Driven by these ideas, we always venture across borders with our diverse teams to find the best solutions and generate impressive results.Only average? Definitely not! Typical Daimler TSS."
  },
<SNIP>
````

## crawler.py
Run time: ~ 2m56

**Informations:** ['name', 'logo', 'linktarget', 'mitarbeiteranzahl','gründungsjahr','postadresse','besucheradresse', 'benefits', 'offene stellen', 'webseite','bilder', 'beschreibung', 'description', 'tel', 'email']
### Usage:
````
python3 crawler.py
````
#### output.json
```json
{
  "locations": [
  <SNIP>
  {
    "name": "Europa",
    "countries": [
    <SNIP>
      {
        "name": "Deutschland",
        "cities": [
        <SNIP>
        {
          "name": "Ulm, Daimler TSS GmbH",
          "logo": "/bilder/karriere/logos/daimler-tss-logo-w180xh100.jpg",
          "linktarget": "https://group.mercedes-benz.com/karriere/ueber-uns/standorte/standort-detailseite-5074.html",
          "mitarbeiteranzahl": 450,
          "gründungsjahr": 1998,
          "postadresse": "Wilhelm-Runge-Str. 11 89081 Ulm",
          "besucheradresse": "Wilhelm-Runge-Str. 11 89081 Ulm",
          "benefits": [
            "Gute Anbindung",
            "Parkplatz",
            "Kantine",
            "Barrierefreiheit",
            "Betriebsarzt",
            "Mitarbeiter Events",
            "Gesundheitsmaßnahmen",
            "Homeoffice möglich",
            "Mitarbeiterrabatte möglich",
            "Mitarbeiterhandy möglich",
            "Internetnutzung"
          ],
          "offene stellen": "/karriere/jobsuche/?action=doSearch&job_genesis_id=9953&job_location=1705&job_location_name=Ulm%2C+Daimler+TSS+GmbH&job_global_location=DE89081A,DE89081E,DE89081C,",
          "webseite": null,
          "bilder": [
            "/bilder/karriere/ueber-uns/standorte/tss-deutschland-2019-2-w614xh345-cutout-2.jpg",
            "/bilder/karriere/ueber-uns/standorte/tss-deutschland-2019-4-w614xh345-cutout.jpg",
            "/bilder/karriere/ueber-uns/standorte/tss-deutschland-2019-3-w614xh345-cutout.jpg"
          ],
          "beschreibung": "1998 als kleines Software-Spin-off gestartet, gestalten wir heute mit über 1200 Mitarbeitern an den Standorten Ulm, Stuttgart, Berlin, Karlsruhe, Kuala Lumpur (Malaysia) und Peking (China) die IT von morgen. Dabei legen wir großen Wert auf menschliche wie digitale Vernetzung. Leidenschaft für IT und eine nach wie vor familiäre Start-up-Kultur verbinden uns und sorgen für Gemeinschaft und kreativen Freiraum im Arbeitsalltag.Wir denken partnerschaftlich und agil, entscheiden technologieneutral und herstellerunabhängig. Das macht uns frei für neue, innovative Ideen und die Aufnahme wichtiger Trends und Impulse in einer sich rasant wandelnden digitalen Welt. Angetrieben von diesen Ideen wagen wir uns auf der Suche nach den besten Lösungen in unseren diversen Teams immer wieder über Grenzen hinweg und generieren überzeugende Ergebnisse.Durchschnitt? Eher nicht! Typisch Daimler TSS.",
          "description": "Daimler TSS. IT excellence: Comprehensive, innovative, close.Having started as a small software spin-off in 1998, we now shape tomorrow's IT with over 1200 employees at our locations in Ulm, Stuttgart, Berlin and Karlsruhe, as well as at our project hubs in Kuala Lumpur (Malaysia) and Beijing (China). We attach great importance to both human and digital networking in this respect. Passion for IT and a still very intimate start-up culture unite us in these endeavors, ensuring a sense of community and creative freedom in everyday working life.We think and act in a spirit of partnership. We are also agile, technologically neutral and manufacturer-independent. This ensures our openness to new, innovative ideas and the assimilation of significant trends and impulses in a rapidly changing digital world. Driven by these ideas, we always venture across borders with our diverse teams to find the best solutions and generate impressive results.Only average? Definitely not! Typical Daimler TSS.",
          "tel": null,
          "email": null
        },
<SNIP>
````


# python-hacking

## To-DO

1. Webserver
- Apache Webserver
- WordPress Blog
  - Nutzer
  - Posts (images, etc.)
- SSH, FTP ?
2. Scanning
- Datein (imges, html, css, js, php, etc.)
- WordPress
  - Core Version
  - Plugin Version
  - Username
- Passwordlist erstellen
3. Exploitation Web
- Password BruteForce (WP, SSH)
- Selenium ?
- PHP Backdoor
4. Schadsoftware (SW)
- Upload der SW
- Defacement & Password Change
- Data Mining
  - Transportweg (z.B. DNS-Records, Cookies oder Tweets)
- erschwerte analyse
  - keine Passwörter, Schlüssel IP-Adressen, URLs im Klartext
  - erschwerter Debug
  - Code Obfuskation
- Netzwerkverbindungen arbeitet mit Transportverschlüsselung.
5. Optional 
- SW soll über Netzwerk in seiner Ausführung per Reverse Shell vom Server steuerbar sein
- SW verwendet einen Packer.
- SW verwendet Methoden, die die Ausführung in einer virtuellen Maschinebehindern.
- SW erkennt „feindliche Prozesse“ und reagiert darauf adäquat (exit oder schlafen oder andere unauffällige Aktion)
- SW verwendet Methoden der Rechteausweitung auf dem Server.


---
---

## Projekt: WpScan + Metasploit
Ein Tool soll Schwachstellen in einem Worpress Server ausfindich machen und diese dann ausnutzen.
Dabei können auch Informationen wie Usernames, Passwörter etc. gesammelt werden. 

### Information Wordpress

> WordPress is an open-source Content Management System (CMS) that can be used for multiple purposes. It's often used to host blogs and forums. WordPress is highly customizable as well as SEO friendly, which makes it popular among companies. However, its customizability and extensible nature make it prone to vulnerabilities through third party themes and plugins. WordPress is written in PHP and usually runs on Apache with MySQL as the backend.

### Bedienung 
- Soll in Richtung Metasploit gehen
  - Verwendung von Optionen

### Scanning - Enumeration
- WordPress Core Version 
- Plugins and Themes 
  - wp-content/plugins or themes
- User
  - login page or the [xmlrpc.php](https://the-bilal-rizwan.medium.com/wordpress-xmlrpc-php-common-vulnerabilites-how-to-exploit-them-d8d3c8600b32)
- media and backups

### Explotaion
- Exploit (RCE, LFI, etc.)
- Backdoor via the Theme Editor
  - ```<?php system($_GET['cmd']); ?>```
  - MSF : exploit/unix/webapp/wp_admin_shell_upload
  - Web Forward Shell
- Brute Force

---

Quellen
* https://wpscan.com/statistics








# Schritte

## 1. Defacement auf der Site
1.1 Überschreiben der index.php <br>
1.2 Login mitschneiden via http server in wp-login.php 

## 2. Zugangsdaten ändern
2.1 Tabele wp_users dumpen und in datei speichern (für Daten-Exfiltration) <br>
  * `mysql -u wp_user -D wp_db --password='p@ssword' -e 'select * from wp_users \G;' > wp_dump.txt` <br>
  
2.2 Mysql Creds von wp-config.php verwenden (wp_user:p@ssword) um damit webadmin password zu h@cker ändern. <br>
  * `mysql -u wp_user -D wp_db --password='p@ssword' -e 'UPDATE wp_users SET user_pass="$P$BaksffqAubwsSmUzqQH37A3ngByAy8." WHERE user_login="webadmin";'`
  
## 3. Privilege Escalation
Mysql 4.X/5.X UDF Exploit via mysql user wp_user. <br>
3.1 Dabei wird eine SUID erstellt um root Rechte zu erhalten. (ggf. noch andere Möglichkeiten)

## 4. Daten-Exfiltration
Findet über HTTP Cookies statt, Daten werden base64 encodiert und verschlüsselt (Asy.verschlüsselung) <br>
4.1 SSH Private Key von user root und ggf. anderen usern senden <br>
4.2 Wichtige Datein (shadow, wp_dump.txt, etc.) <br>
4.3 Home Verzeichnisse (debian, root)

## 5. Persistenz
5.1 Private SSH Key von User root <br>
5.2 Rev Shell (via SUID) (in crontab @reboot)
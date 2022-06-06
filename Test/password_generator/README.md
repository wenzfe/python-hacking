# Password-List Generator
Erstellt eine Passowordliste aus einer Json Datei. 

### Usage:
````
$ python3 pwListGenerator.py -h
````
````
Usage: ./pwGenerator.py -i [INPUT FILE] -l [Language] -min -max -r [Rule]
-i INPUT FILE:       Input file .json
-l Language:         de=german, en=english, both
-r RULES:
  Zahl_Ende          :    1
  Zahl_Anfang        :    2
  Sonderz._Ende      :    3
  Sonderz._Anfang    :    4
  Anfangsb. groß     :    5
  Datum_Ende         :    6

  Leetspeak          :    9

-d DEFAULT:
  -i ../fast_output.json -l both -min 5 -max 20
````
### Examples: 
````
$ python3 pwGenerator.py -i data.json -l en -min 4 -max 12 -r 5496
````

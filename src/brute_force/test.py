#!/usr/bin/python3

import sys, time

print("start")
w = "Schreibprogramm – Textverarbeitung in DOCX | Microsoft Word"

for x in range(2):
    for z in w:
        sys.stdout.write('\r'+str(z))
        sys.stdout.flush()
        time.sleep(1)
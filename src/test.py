from time import sleep
import os
import time
import signal


def self_kill():
    my_pid = os.getpid()
    timeout = time.time() + 120
    print("START SELF KILL")
    while time.time() < timeout: # no child in 60 sec
       
        print("Have Child, self kill")
        sleep(5)
        #os.system('kill -9 {my_pid}')
        os.kill(my_pid, signal.SIGKILL)
        exit()

self_kill()
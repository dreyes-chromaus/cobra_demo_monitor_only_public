import csv
import os
import cobra_ops
import cobra_ssh
import random
import time
from multiprocessing import Process, Event, Manager
from datetime import datetime
import socket
import paramiko  # For SSH connection errors
from cobra_function_keys import test_functions_port_1111, test_functions_port_1000, test_functions_port_1100, test_functions_port_1112, test_functions_port_2000, test_functions_port_2100




cobra = cobra_ops.cobra_demo()
cobra.ip_set("192.168.2.105")
cobra.init_cobra(test_functions_port_1111["port"])

while True:
    try:
        cobra.run_commands(test_functions_port_1111["port"], test_functions_port_1111)
    except KeyboardInterrupt as e:
        print(f"[ERROR] test_loop: Communication lost - {e}")
    time.sleep(1)
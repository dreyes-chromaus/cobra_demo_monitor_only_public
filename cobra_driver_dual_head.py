import cobra_ops
import time
import multiprocessing as mp
import csv
from datetime import datetime, date
import threading

"""
def repeat_status():
    cobra.print_status(1)
    cobra.print_status(2)


def cobra_set_temp_hold(set_temp, head_select):
    cobra.change_temp(head_select)
"""


def cobra_demo_run(head_select):
    count = 0
    cobra = cobra_ops.cobra_demo()

    cobra.ip_set("192.168.2.105")
    cobra.init_cobra(head_select)
    while True:
        try:
            count_file = open("act_deact_count.txt", "a")
            print("ACTUATION COUNT: " + str(count))

            time.sleep(3)

            # Actuate and set 25 both heads
            startt = time.time()
            cobra.change_temp(25, head_select)
            time.sleep(5)
            while time.time() - startt < 60:
                cobra.print_status(head_select)

            # cobra.change_temp(25, 1)
            time.sleep(15)
            cobra.actuate(head_select)
            time.sleep(10)

            # Actuate and set 25 both heads
            startt = time.time()
            cobra.change_temp(10, head_select)
            time.sleep(5)
            while time.time() - startt < 60:
                cobra.print_status(head_select)

            cobra.deactuate(head_select)
            # cobra.change_temp(25, 1)
            time.sleep(10)
            count += 1
            count_file.write(str(count))


        except KeyboardInterrupt:
            cobra.disconnect_cobra(1)
            pass


thread1 = threading.Thread(target=cobra_demo_run, args=(1,))
thread2 = threading.Thread(target=cobra_demo_run, args=(2,))

thread1.start()
thread2.start()

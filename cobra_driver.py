import cobra_ops
import time
import multiprocessing as mp
import csv
from datetime import datetime, date


def repeat_status():
    cobra.print_status(1)
    cobra.print_status(2)


def cobra_set_temp_hold(set_temp, head_select):
    cobra.change_temp(25, head_select)


count = 0
cobra = cobra_ops.cobra_demo()

cobra.ip_set("192.168.2.71")
cobra.init_cobra(1)


while True:
    try:
        count_file = open("act_deact_count.txt", "a")
        print("ACTUATION COUNT: " + str(count))

        cobra.actuate(1)

        time.sleep(10)

        # Actuate and set 25 both heads
        startt = time.time()
        cobra.cobram1.set_temp(25)
        while time.time() - startt < 60:
            print(cobra.print_status(1), end='', flush=True)

        cobra.deactuate(1)
        # cobra.change_temp(25, 1)
        time.sleep(10)

        cobra.actuate(1)

        time.sleep(10)

        # Actuate and set 25 both heads
        startt = time.time()
        cobra.cobram1.set_temp(50)
        while time.time() - startt < 60:
            print(cobra.print_status(1), end='', flush=True)

        cobra.deactuate(1)
        # cobra.change_temp(25, 1)
        time.sleep(10)



        count += 1
        count_file.write(str(count))


    except KeyboardInterrupt:
        cobra.disconnect_cobra(1)
        cobra.disconnect_cobra(2)
        pass

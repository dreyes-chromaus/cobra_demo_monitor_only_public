import csv
import os
import sys

import cobra_ops
import cobra_ssh
import random
import time
from multiprocessing import Process, Event, Manager
from datetime import datetime
import socket
import paramiko  # For SSH connection errors
from cobra_function_keys import test_functions_port_1111, test_functions_port_1000, test_functions_port_1100, test_functions_port_1112, test_functions_port_2000, test_functions_port_2100

#TODO: Need to find a way to remove cobra.ip_set() redundancies

def repeat_status(ip_input, head_select, stop_event=None):
    # Create independent cobra object in subprocess
    cobra = cobra_ops.cobra_demo()
    cobra.ip_set(ip_input)  # Set IP once
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            cobra.print_status(head_select)
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] repeat_status: Communication lost - {e}")
            stop_event.set()
        time.sleep(0.5)  # Add delay to avoid flooding

def get_cobra_rt_version(ip_input, head_select, stop_event):
    cobra = cobra_ops.cobra_demo()
    cobra.ip_set(ip_input)
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            print(cobra.get_rt_version(head_select))
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] get_cobra_rt_version: {e}")
            stop_event.set()
        time.sleep(1)

def change_set_temp(ip_input, head_select, set_temp, stop_event):
    # Create independent cobra object in subprocess
    cobra = cobra_ops.cobra_demo()
    cobra.ip_set(ip_input)  # Set IP once
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            cobra.change_temp(set_temp, head_select)
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] change_set_temp: Communication lost - {e}")
            stop_event.set()
        time.sleep(1)


def change_rand_temp(ip_input, head_select, stop_event):
    # Create independent cobra object in subprocess
    cobra = cobra_ops.cobra_demo()
    cobra.ip_set(ip_input)  # Set IP once
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            cobra.change_temp(round(random.uniform(25.1, 25.2), 3), head_select)
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] change_rand_temp: Communication lost - {e}")
            stop_event.set()
        time.sleep(5)

def change_ss_target_50(ip_input, head_select, stop_event):
    cobra = cobra_ops.cobra_demo()
    cobra.ip_set(ip_input)
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            cobra.change_ss_target_50(1, "50")
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] change_ss_target: Communication lost - {e}")
            stop_event.set()
        time.sleep(1)

def change_tsd_gain_1(ip_input, head_select, stop_event):
    cobra = cobra_ops.cobra_demo()
    cobra.ip_set(ip_input)
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            cobra.change_tsd_gain_1(1, "1")
            cobra.change_tsd_gain_1(1)
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] change_tsd_gain: Communication lost - {e}")
            stop_event.set()
        time.sleep(1)


def cobra_set_temp_hold(ip_input, set_temp, head_select):
    # Legacy function for one-time temp hold
    try:
        cobra = cobra_ops.cobra_demo()
        cobra.ip_set(ip_input)  # Set IP once
        cobra.init_cobra(head_select)
        cobra.change_temp(set_temp, head_select)
    except (socket.error, paramiko.SSHException, Exception) as e:
        print(f"[ERROR] cobra_set_temp_hold: Communication lost - {e}")


def running(stop_event):
    start_time = time.time()
    while not stop_event.is_set():
        print("Start Time: " + str(start_time))
        print("Current Time: " + str(datetime.now()))
        print("Time elapsed: {:.2f}".format(time.time() - start_time))
        time.sleep(0.5)

def test_loop(ip_input, test_functions, stop_event):
    cobra = cobra_ops.cobra_demo()
    cobra.ip_set(ip_input)
    cobra.init_cobra(test_functions["port"])

    while not stop_event.is_set():
        try:
            cobra.run_commands(test_functions["port"], test_functions)
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] test_loop: Communication lost - {e}")
            stop_event.set()
        time.sleep(1)

def log_file_monitor(ip_input, stop_event):  # TODO: Code to check on log file count.
    # Check if logfiles are being created and are growing
    som = cobra_ssh.som_com(ip_input)
    while not stop_event.is_set():
        try:
            logfile_list = som.dir_read()
            idx_rcnt_log = 0
            if logfile_list[idx_rcnt_log]['name'].endswith('.tdms') is not True:
                idx_rcnt_log += 1
            print('file count: ' + str(len(logfile_list)))
            print('logfile: ' + logfile_list[0]['name'] + '\t\tsize:' + str(logfile_list[0]['size']))
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] log_file_monitor: Communication lost - {e}")
            stop_event.set()
        time.sleep(10)


def memory_compare(ip_input, stop_event, head_select, fmem_log): #TODO: need to change the name of this function. DECEPTIVE
    # Comment here
    cobra = cobra_ops.cobra_demo()
    #som = cobra_ssh.som_com(ip_input)
    cobra.ip_set(ip_input)  # Set IP once
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            cobra_free = cobra.get_free_memory(head_select) # current format is KB
            cobra_free = cobra_free / 1000 # now MB format
            fmem_log.append(str(cobra_free))
            #delta_free = abs(som_free - cobra_free)
            #print("SOM\t\tCOBRA\t\tDELTA")
            #print(som_free + 'MB\t\t' + cobra_free + 'MB\t\t' + delta_free + 'MB')
            print('Cobra_Free_Memory_OUT: ' + str(cobra_free))
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] memory_compare: Communication lost - {e}")
            stop_event.set()
        time.sleep(1)


def memory_monitor(ip_input, stop_event, umem_log, fmem_log, time_log):
    # Create independent som object in subprocess
    som = cobra_ssh.som_com(ip_input)

    while not stop_event.is_set():
        try:
            total_memory,used_memory,free_memory = som.mem_read_split() # first return was not named correctly
            umem_log.append(used_memory)
            fmem_log.append(free_memory)
            time_log.append(datetime.now().strftime('%H:%M:%S'))
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] memory_monitor: Communication lost - {e}")
            stop_event.set()
        time.sleep(1)
    return umem_log, fmem_log

def memory_monitor_stream(ip_input, stop_event, umem_log, fmem_log, time_log):
    som = cobra_ssh.som_com(ip_input)

    while not stop_event.is_set():
        try:
            total_memory, used_memory, free_memory = som.mem_read_split()
            umem_log.append(used_memory)
            fmem_log.append(free_memory)
            time_log.append(datetime.now().strftime('%H:%M:%S'))
            sys.stdout.write(f"\r[" + datetime.now().strftime('%H:%M:%S') + "] Physical Memory (Available: {free_memory} MB) (Used: {used_memory} MB)")
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] memory_monitor: Communication lost - {e}")
            stop_event.set()
    return umem_log, fmem_log


def store_to_csv(umem_log, fmem_log, cfmem_log, time_log, ip_input):
    print("[INFO] PRINTING DATA TO CSV")
    os.makedirs('mem_logs', exist_ok=True)
    log_create_time = datetime.now().strftime('%Y%m%d-%H%M%S')
    filename = f"cobra_memory_log_{log_create_time}_{ip_input}_m1.csv"
    file_path = os.path.join('mem_logs', filename)

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Time", "Free Memory", "Used Memory", "Cobra Free Memory"])
        while umem_log and fmem_log and cfmem_log and time_log:
            timing = time_log.pop(0)
            fmem = fmem_log.pop(0)
            umem = umem_log.pop(0)
            cfmem = cfmem_log.pop(0)
            writer.writerow([timing, fmem, umem, cfmem])

def main():
    stop_event = Event()

    # Active head IDs — modify this list to add/remove heads
    cobra_ip = ""
    active_heads = []
    head_selected = False
    manager = Manager()
    used_memory_log = manager.list()
    free_memory_log = manager.list()
    cfree_memory_log = manager.list()
    test_time_log = manager.list()
    processes = []

    cobra_ip = input("cobra_ip: ")
    while head_selected is False:
        cobra_head = input("cobra_head: ")
        if cobra_head == '1':
            #active_heads = [test_functions_port_1111] #TODO: convert to ports defined in function_keys
            active_heads = [test_functions_port_1111] #TODO: convert to ports defined in function_keys
            head_selected = True
        elif cobra_head == '2':
            active_heads = [test_functions_port_1112, test_functions_port_1111] #TODO: convert to ports define in function_keys
            head_selected = True
        else:
            print("Invalid cobra head number")
            head_selected = False
    cobra_test = cobra_ops.cobra_demo()
    cobra_test.ip_set(cobra_ip)

    if cobra_test.verify_cobra_connection():
        print("[INFO] COBRA CONNECTION ESTABLISHED AT IP:{ip}".format(ip=cobra_ip))
        print("[INFO] STARTING TEST")
        # Launch change_rand_temp for each head
        '''
        for function_list in active_heads:
            p = Process(target=test_loop, args=(cobra_ip, function_list, stop_event))
            processes.append(p)
        '''
        # Launch timing and memory monitor processes
        processes.append(Process(target=running, args=(stop_event,)))
        processes.append(Process(target=memory_monitor_stream, args=(cobra_ip, stop_event, used_memory_log, free_memory_log, test_time_log)))
        #processes.append(Process(target=change_tsd_gain_1, args=(cobra_ip, 13, stop_event)))
        #processes.append(Process(target=change_ss_target_50, args=(cobra_ip, 13, stop_event)))
        #processes.append(Process(target=memory_monitor, args=(cobra_ip, stop_event, used_memory_log, free_memory_log, test_time_log)))
        processes.append(Process(target=memory_compare, args=(cobra_ip, stop_event, 13, cfree_memory_log)))
        processes.append(Process(target=log_file_monitor, args=(cobra_ip, stop_event)))

        # Start all processes
        for p in processes:
            p.start()
        try:
            while not stop_event.is_set():
                time.sleep(1)
            store_to_csv(used_memory_log, free_memory_log, cfree_memory_log, test_time_log, cobra_ip)
        except KeyboardInterrupt:
            print("\n[INFO] Keyboard interrupt received. Shutting down...")
            store_to_csv(used_memory_log, free_memory_log, cfree_memory_log, test_time_log, cobra_ip)
            stop_event.set()
        finally:
            stop_event.set()  # Signal all processes to stop
            for p in processes:
                p.join()  # Wait for clean exit
            print("[INFO] All processes terminated cleanly.")
    else:
        print("[ERROR] UNABLE TO ESTABLISH CONNECTION TO COBRA")


if __name__ == "__main__":
    main()

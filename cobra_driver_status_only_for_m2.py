import cobra_ops
import cobra_ssh
import random
import time
from multiprocessing import Process, Event
from datetime import datetime
import socket
import paramiko  # For SSH connection errors

#TODO: Need to find a way to remove cobra.ip_set() redundancies

def repeat_status(head_select, stop_event):
    # Create independent cobra object in subprocess
    cobra = cobra_ops.cobra_demo()
    cobra.ip_set("192.168.2.105")  # Set IP once
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            cobra.print_status(head_select)
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] repeat_status: Communication lost - {e}")
            stop_event.set()
        time.sleep(0.5)  # Add delay to avoid flooding

def get_cobra_rt_version(head_select, stop_event):
    cobra = cobra_ops.cobra_demo()
    cobra.ip_set("192.168.2.105")
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            print(cobra.get_rt_version(head_select))
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] get_cobra_rt_version: {e}")
            stop_event.set()
        time.sleep(1)

def change_set_temp(head_select, set_temp, stop_event):
    # Create independent cobra object in subprocess
    cobra = cobra_ops.cobra_demo()
    cobra.ip_set("192.168.2.105")  # Set IP once
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            cobra.change_temp(set_temp, head_select)
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] change_set_temp: Communication lost - {e}")
            stop_event.set()
        time.sleep(1)


def change_rand_temp(head_select, stop_event):
    # Create independent cobra object in subprocess
    cobra = cobra_ops.cobra_demo()
    cobra.ip_set("192.168.2.105")  # Set IP once
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            cobra.change_temp(round(random.uniform(25.1, 25.2), 3), head_select)
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] change_rand_temp: Communication lost - {e}")
            stop_event.set()
        time.sleep(1)


def cobra_set_temp_hold(set_temp, head_select):
    # Legacy function for one-time temp hold
    try:
        cobra = cobra_ops.cobra_demo()
        cobra.ip_set("192.168.2.105")  # Set IP once
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


def log_file_monitor(stop_event):  # TODO: Code to check on log file count.
    # Check if logfiles are being created and are growing
    som = cobra_ssh.som_com('192.168.2.105')
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


def memory_compare(stop_event, head_select):
    # Comment here
    cobra = cobra_ops.cobra_demo()
    #som = cobra_ssh.som_com('192.168.2.105')
    cobra.ip_set("192.168.2.105")  # Set IP once
    cobra.init_cobra(head_select)

    while not stop_event.is_set():
        try:
            #som_free = som.mem_free()
            cobra_free = cobra.get_free_memory(head_select)
            #delta_free = abs(som_free - cobra_free)
            #print("SOM\t\tCOBRA\t\tDELTA")
            #print(som_free + 'MB\t\t' + cobra_free + 'MB\t\t' + delta_free + 'MB')
            print('Cobra_Free_Memory_OUT: ' + str(cobra_free))
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] memory_compare: Communication lost - {e}")
            stop_event.set()
        time.sleep(1)


def memory_monitor(stop_event):
    # Create independent som object in subprocess
    som = cobra_ssh.som_com('192.168.2.105')
    while not stop_event.is_set():
        try:
            som.mem_read_split()
        except (socket.error, paramiko.SSHException, Exception) as e:
            print(f"[ERROR] memory_monitor: Communication lost - {e}")
            stop_event.set()
        time.sleep(1)


def main():
    stop_event = Event()

    # Active head IDs — modify this list to add/remove heads
    active_heads = [2, 20, 22]
    processes = []

    # Launch change_rand_temp for each head
    for head in active_heads:
        p = Process(target=change_rand_temp, args=(head, stop_event))
        processes.append(p)

    # Launch timing and memory monitor processes
    processes.append(Process(target=running, args=(stop_event,)))
    #processes.append(Process(target=memory_monitor, args=(stop_event,)))
    #processes.append(Process(target=memory_compare, args=(stop_event, 13)))
    #processes.append(Process(target=log_file_monitor, args=(stop_event,)))

    # Start all processes
    for p in processes:
        p.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Keyboard interrupt received. Shutting down...")
    finally:
        stop_event.set()  # Signal all processes to stop
        for p in processes:
            p.join()  # Wait for clean exit
        print("[INFO] All processes terminated cleanly.")


if __name__ == "__main__":
    main()

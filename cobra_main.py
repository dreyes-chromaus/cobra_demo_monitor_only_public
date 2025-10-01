# cobra_main.py
import time
from multiprocessing import Process, Event, Manager
from cobra_tasks import memory_monitor_stream, store_to_csv
import cobra_ops
from cobra_function_keys import (
    test_functions_port_1111,
    test_functions_port_1112,
)

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
            active_heads = [test_functions_port_1111]  # TODO: convert to ports defined in function_keys
            head_selected = True
        elif cobra_head == '2':
            active_heads = [test_functions_port_1112, test_functions_port_1111]  # TODO: convert to ports define in function_keys
            head_selected = True
        else:
            print("Invalid cobra head number")
            head_selected = False

    cobra_test = cobra_ops.cobra_demo()
    cobra_test.ip_set(cobra_ip)

    if cobra_test.verify_cobra_connection():
        print("[INFO] COBRA CONNECTION ESTABLISHED AT IP:{ip}".format(ip=cobra_ip))
        print("[INFO] STARTING TEST")

        # Example: Launch memory monitor stream
        processes.append(
            Process(
                target=memory_monitor_stream,
                args=(cobra_ip, stop_event, used_memory_log, free_memory_log, cfree_memory_log, test_time_log),
            )
        )

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

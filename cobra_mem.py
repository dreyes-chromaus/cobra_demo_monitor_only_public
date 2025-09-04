import cobra_ssh
import cobra_tcp_2025
import time
from datetime import datetime, timedelta


class memory:
    def __init__(self, cobra_ip):
        self.corba_tcp = None
        self.is_linux_memlow = False
        self.is_cobra_memlow = False
        self.is_cobra_running = False

        self.som = cobra_ssh.som_com(cobra_ip)
        self.cobra_tcp = cobra_tcp_2025.cobra_thermal_system(cobra_ip, 1111)
        self.save_cobra_run_state()

    def get_cobra_run_state(self):
        cobra_state = self.cobra_tcp.status4().split('\n')[3]
        cobra_state = cobra_state.split('\t')
        print(cobra_state)
        if cobra_state[1] ==  'Run':
            return True
        else:
            return False

    def save_cobra_run_state(self):
        self.is_cobra_running = self.get_cobra_run_state()

    def get_lmem_status(self):
        current_mem = self.som.mem_free()[1]
        if int(current_mem) < 90:
            self.is_linux_memlow = True
        else:
            self.is_linux_memlow = False

    def get_cmem_status(self):
        cobra_free = self.cobra_tcp.som_status().split()[8]  # current format is KB
        cobra_free = int(float(cobra_free) / 1000)  # now MB format
        if int(cobra_free) < 90:
            self.is_cobra_memlow = True
        else:
            self.is_cobra_memlow = False

    def cobra_mem_shutdown_sequence(self):
        # TODO: Implement a blocking solution to allow user to properly prepare
        # before cobra fully shuts down compressor
        if self.cobra_tcp is not None:
            if self.is_cobra_memlow is True and self.is_linux_memlow is True:
                self.corba_tcp.set_temp(25) # Set Temp 25
                start_time = datetime.now()
                while datetime.now() - start_time < timedelta(minutes=1):
                    print(self.cobra_tcp.status1())
                self.cobra_tcp.power(0) # Power off Compressor


#test here
mem_test_class = memory("192.168.2.102")
mem_test_class.get_lmem_status()
mem_test_class.get_cmem_status()

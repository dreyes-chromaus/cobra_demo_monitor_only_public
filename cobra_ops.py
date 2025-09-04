import cobra_tcp_2025
#import telnetlib
import time
import multiprocessing as mp
from datetime import datetime, date
from sys import getsizeof
from cc_head_port_mapping import head_to_attr, head_to_port_attr
from cc_status_mapping import statuses


class cobra_demo:
    def __init__(self):
        self.ipaddr = ''
        self.portM1 = 1000
        self.portM11 = 1111
        self.portM10 = 1100
        self.portM2 = 2000
        self.portM22 = 1112
        self.portM20 = 2100
        self.portM13 = 1300
        self.cobram1 = None
        self.cobram11 = None
        self.cobram2 = None
        self.cobram22 = None
        self.cobram20 = None
        self.cobram10 = None
        self.cobram13 = None

    def verify_cobra_connection(self):
        # TODO: Add a way to Verify/Identify M2
        self.init_cobra(10)
        if self.get_cobra_head(10).connected:
            self.cobram10.close_connection()
            return True
        else:
            self.cobram10.close_connection()
            return False

    def get_status1(self, head_select):
        current_cobra = self.get_cobra_head(head_select)
        print(current_cobra.status1())

    def change_temp(self, temp, head_select):
        current_cobra = self.get_cobra_head(head_select)
        ss_reached = False
        ssm = False
        query = ""

        print(current_cobra.set_temp(temp))
        time.sleep(1)

        #for x in range(0, 600):
            #self.print_status(head_select)
            #time.sleep(0.5)

        """
        while not ss_reached:
            self.print_status(head_select)
            query = current_cobra.status1()
            squery = query.split("\n")
            if ("T_CASE: " + str(set_temp)) in squery:
                ssm = True
            if ssm:
                break
        """

    def change_tsd_gain(self, head_select, gain=None):
        current_cobra = self.get_cobra_head(head_select)
        print(current_cobra.tsd_gain(gain))

    def change_ss_target_50(self, head_select, target="50"):
        current_cobra = self.get_cobra_head(head_select)
        print(current_cobra.ss_target(target))

    def get_rt_version(self, head_select):
        current_cobra = self.get_cobra_head(head_select)
        cobra_response = current_cobra.gui.ip()
        return cobra_response

    # Actuate based on head select
    def actuate(self, head_select):
        current_cobra = self.get_cobra_head(head_select)
        current_cobra.actuate()

    # Deactuate based on head select
    def deactuate(self, head_select):
        current_cobra = self.get_cobra_head(head_select)
        current_cobra.deactuate()

    def print_status(self, head_select, status_num):
        try:
            # Get the attribute name from the statuses map
            attr_name = statuses[status_num]  # e.g., "status1"
            current_cobra = self.get_cobra_head(head_select)

            # Get the method from current_cobra
            status_method = getattr(current_cobra, attr_name)

            # Call the method and pass its result to run_print
            self.run_print(status_method())

        except KeyError:
            raise ValueError(f"[ERROR] Unsupported status number: {status_num}")
        except AttributeError:
            raise ValueError(f"[ERROR] Cobra head {head_select} does not have {attr_name}")


    def ip_set(self, ip_input):
        self.ipaddr = ip_input

    def init_cobra(self, head_select):
        try:
            attr_name = head_to_attr[head_select]
            port_attr = head_to_port_attr[head_select]
            port_value = getattr(self, port_attr)
            setattr(self, attr_name, cobra_tcp_2025.cobra_thermal_system(self.ipaddr, port_value))
            self.print_status(head_select, 1)
        except KeyError:
            raise ValueError(f"[ERROR] Unsupported head selection: {head_select}")

    def get_cobra_head(self, select):
        try:
            attr_name = head_to_attr[select]
            return getattr(self, attr_name)
        except KeyError:
            raise ValueError(f"[ERROR] Invalid head selection: {select}")

    def get_free_memory(self, head_select):
        current_cobra = self.get_cobra_head(head_select)
        som_readback = current_cobra.som_status().split()
        free_memory = som_readback[8]
        return free_memory

    def run_print(self, input):
        print(datetime.utcnow().strftime('%F %T.%f')[:-3] + "\t" + input)

    def disconnect_cobra(self, head_select):
        current_cobra = self.get_cobra_head(head_select)
        current_cobra.main_close()

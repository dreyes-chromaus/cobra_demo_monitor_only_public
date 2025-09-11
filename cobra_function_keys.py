import random

functions = {
    "status",
    "status1",
    "status2",
    "status4",
    "power",
    "set_temp",
    "tsd_feedback",
    "tj_priority",
    "feedback",
    "heater_override",
    "actuate",
    "deactuate",
    "set_force",
    "new_datalog",
    "ss_target",
    "dut_list",
    "select_dut",
    "set_rpm",
    "serial_number",
    "help",
    "som_status",
    "gui_ip",
    "powerbox",
    "n_factor",
    "set_ramp_rate",
    "event_test",
    "warning_test",
    "fault_test",
    "cancel_log",
    "end_log",
    "start_log",
    "tsd_gain",
}

test_functions_port_1111 = {
    "port": 11,
    "actuate": [None, 15],
    "deactuate": [None, 15]
}

'''
test_functions_port_1111 = {
    "port": 11,
    "status1": None,
    "ss_target": 50,
    "tsd_gain": 1,
    "set_temp": round(random.uniform(25.1, 25.2), 3),
    "actuate": None,
    "deactuate": None,
}
'''

test_functions_port_1000 = {
    "port": 1,
    "set_temp": round(random.uniform(25.1, 25.2), 3)
}

test_functions_port_1100 = {
    "port": 10,
    "set_temp": round(random.uniform(25.1, 25.2), 3)
}

test_functions_port_1112 = {
    "port": 22,
    "set_temp": round(random.uniform(25.1, 25.2), 3)
}

test_functions_port_2000 = {
    "port": 2,
    "set_temp": round(random.uniform(25.1, 25.2), 3)
}

test_functions_port_2100 = {
    "port": 20,
    "set_temp": round(random.uniform(25.1, 25.2), 3)
}

import queue
import telnetlib
import time
import sys

global error_msg
#global error_check # why not just put it in the class as an attribute??? Question Mark

class cobra_thermal_system:
    def __init__(self, ipaddr, port=1300):
        self.ipaddr = ipaddr  # gpib address
        self.id_expect = 'STATUS'
        self.main_port = port   # Port 1000 - 60sec timeout
                                # Port 1300 - 5sec timeout         
                                # Port 1100 - No timeout
                                # Port 2000 - 5sec timeout [For head 2 on dual Cobra]
                                # Port 2100 - No timeout [For head 2 on dual Cobra]
                                # Port 3001 - Only for sending diode temp readings through TCP/IP for TSD feedback (Experimental)
        self.lcd_port = '1001'      # LCD port for head 1 - 60sec timeout
        self.lcd_secport = '2001'   # LCD port for head 2 - 60sec timeout
        self.error_check = 0
        self.main = None  # Telnet Object for Cobra Unit
        self.lcd = None  # Telnet Object for LCD Unit
        self.assign_id()

    def assign_id(self):
        global error_msg # TODO: why do this if it is already initialized outside of the class???
        #global error_check # TODO: why do this as well, for the same reason?
        error_check = 0 # TODO: this doesnt do anything because the variable is not actually part of the class
        try:
            self.main = telnetlib.Telnet(self.ipaddr, self.main_port, 5)
            id_query = self.ask('STATUS1()')
            if self.id_expect not in id_query:
                # print('****************************************************************************') print(
                # 'Problem connecting to ip address {}. \n Response to STATUS1(): {}'.format(self.ipaddr, id_query))
                # print('One method to bring back comm link is to power cycle cobra unit')
                error_check = 1
                error_msg = 'Problem connecting to ip address {}. \n Response to STATUS2(): {}\n' \
                            'One method to bring back comm link is to power cycle Cobra unit'.format(self.ipaddr,
                                                                                                     id_query)
        except:
            # print('Problem connecting {} {} using IP Address {}'.format(self.name, self.type, self.ipaddr))
            # print('****************************************************************************')
            error_check = 2
            error_msg = 'Problem connecting system using IP Address {}\n' \
                        'Please check IP address is correct'.format(self.ipaddr)

    def write(self, command):
        self.main.write('{}\r\n'.format(command).encode('ascii'))

    def ask(self, command):
        self.main.write('{}\r\n'.format(command).encode('ascii'))
        query = self.main.read_until(b'\r\n', 5)
        return query.decode()

    # Outdated status command, less information provided in response compared to STATUS2
    def status(self):
        self.main.read_very_eager()  # clear buffer
        response = self.ask('STATUS()')
        return response

    def status1(self):
        self.main.read_very_eager()  # clear buffer
        response = self.ask('STATUS1()')
        return response

    def sw_version(self):
        '''
        Returns SW Version of Cobra
        '''
        query = self.ask('SOM STATUS()')
        version = query.split('SW Version:')[1].split(' C')[0]
        return version

    def sd_storage(self):
        '''
        Returns SD card free space available (MB)
        '''
        query = self.ask('SOM STATUS()')
        storage = query.split('SD Free Space: ')[1].split(' ')[0]
        return storage

    def power(self, state):
        time.sleep(0.5)
        query = self.status1()
        while 'STATUS' not in query:
            query = self.status1()
        power_state = (query.split('HEAD_STATE: ')[1].split('\n')[0])
    
        
        if power_state == 'DISABLED' and state == 1:
            # print('Turning compressor ON')
            self.write('POWER({})'.format(state))
            response = self.main.read_until(b'ON', 0.5)
            return response.decode().strip()

        elif power_state == 'RUN' and state == 0:
            # print('Turning compressor OFF')
            self.write('POWER({})'.format(state))
            response = self.main.read_until(b'OFF', 0.5)
            return response.decode().strip()

    def read_head_position(self):
        response = self.status1()
        while 'STATUS' not in response:
            response = self.status1()
        position = response.split('POWERDRIVE: ')[1].split('\n')[0]
        return position

    def set_temp(self, temp):
        temp = float(temp)
        self.main.read_very_eager()  # clear buffer
        #if temp > 150:
            #self.lcd_color('red')
            #self.lcd_msg('User Error!')
            #msg = 'Set temperature too high. ({}) Assuming error and exiting. Please check config and restart.'.format(
            #    temp)
            #print(msg)
            #sys.exit(msg)
        self.write('SET TEMP({})'.format(temp))
        """if temp > 60.0:
        
            self.lcd_color('amber')
            self.lcd_msg('Hot Temp')
        elif temp > 15.0:
            self.lcd_color('green')
            self.lcd_msg('Nominal Temp')
        else:
            self.lcd_color('cyan')
            self.lcd_msg('Cold Temp')
        """

    def tsd_feedback(self, state):
        '''
        Turn ON (1) or OFF (0) TSD Feedback mode
        '''
        self.write('TSD FEEDBACK({})'.format(state))
        if state == 1:
            response = self.main.read_until(b'ON', 5)
            print(response)
            return response.decode().strip()
        elif state == 0:
            response = self.main.read_until(b'OFF', 5)
            print(response)
            return response.decode().strip()
        else:
            response = 'Invalid value: must be either 1: ON or 0: OFF'
            return response

    def read_temps(self):
        """
        Returns Temperatures as [TCASE, TEVAP, TSD] (e.g. Tcase = read_temp()[0])
        """
        self.main.read_very_eager()  # clear buffer
        query = self.status1()
        while 'STATUS' not in query:
            query = self.status1()
        try:
            tcase = (query.split('T_CASE: ')[1].split('\n')[0])
        except IndexError:
            tcase = 'NaN'
        try:
            tevap = (query.split('T_EVAP: ')[1].split('\n')[0])
        except IndexError:
            tevap = 'NaN'
        try:
            tsd = (query.split('T_DIODE: ')[1].split('\n')[0])
        except IndexError:
            tsd = 'NaN'
        return float(tcase), float(tevap), float(tsd)

    def tcase1_calibrate(self, gain, offset):
        '''
        Updates Head 1 T-CASE Gain and Offset for temperature calibration
        Response format: "Update Config NEW M1 T-CASE GAIN value = X.000000", "Update Config NEW M1 T-CASE OFFSET value = Y.000000"
        '''
        self.write('T-CASE GAIN({})'.format(gain))
        response = self.main.read_until(b'000000', 5)
        response_gain = response.decode().strip()

        self.write('T-CASE OFFSET({})'.format(offset))
        response = self.main.read_until(b'000000', 5)
        response_offset = response.decode().strip()

        return (response_gain, response_offset)

    def tcase2_calibrate(self, gain, offset):
        '''
        Updates Head 2 T-CASE Gain and Offset for temperature calibration
        Response format: "Update Config NEW M2 T-CASE GAIN value = X.000000", "Update Config NEW M2 T-CASE OFFSET value = Y.000000"
        '''
        self.write('M2 T-CASE GAIN({})'.format(gain))
        response = self.main.read_until(b'000000', 5)
        response_gain = response.decode().strip()

        self.write('M2 T-CASE OFFSET({})'.format(offset))
        response = self.main.read_until(b'000000', 5)
        response_offset = response.decode().strip()

        return (response_gain, response_offset)

    def heater_override(self, value):
        '''
        Manually set heater percentage and override PID controls.
        Value must be nonnegative or else PID will resume control and manual override disabled.
        '''
        if value < 0:
            response = 'M1 HEATER OVERRIDE DISABLED'
        else:
            self.write('M1 HEATER OVERRIDE({})'.format(value))
            response = self.main.read_until(b'000000', 5).decode().strip()

        return response

    def actuate(self):
        self.main.read_very_eager()  # clear buffer
        self.write('ACTUATE()')
        response = self.main.read_until(b'OK)', 5)
        return response.decode().strip()

    def deactuate(self):
        self.main.read_very_eager()  # clear buffer
        self.write('UNACTUATE()')
        response = self.main.read_until(b'OK)', 5)
        return response.decode().strip()

    def set_force(self, force):
        '''
        Sets the force of DUT 0 to #LBS
        '''
        self.write('SET FORCE({})'.format(force))
        response = self.main.read_until(b'.0', 0.5)
        return response.decode().strip()

    def ss_target(self, target):
        '''
        Sets the heater% to new target value
        Response format: "Update Config NEW Steady State Target value = X.000000"
        '''
        self.main.write('SS TARGET({})\r\n'.format(target).encode('ascii'))
        query = self.main.read_until(b'000000', 0.5)
        return query.decode().strip()

    def dut_list(self):
        self.main.read_very_eager()  # clear buffer
        list = self.ask('DUT NAMES()')
        return list

    def select_dut(self, dut):
        self.main.read_very_eager()  # clear buffer
        checklist = self.dut_list()
        if dut in checklist:
            self.write('SELECT DUT({})'.format(dut))
        else:
            error_msg = 'Error: DUT not found'
            return error_msg

    def set_rpm(self, rpm):
        '''
        For Sea Cobra(E) only. Manually set RPM of compressor
        '''
        self.main.read_very_eager()  # clear buffer
        response = self.ask('RPM({})'.format(rpm))
        if "NEW" in response:
            return response
        elif 'Override' in response:
            error_msg = 'Invalid RPM value; must be 1500-5500'
            return error_msg
        else:
            error_msg = 'Command sent but no response received'
            return error_msg

    def serial_number(self):
        if self.main_port != 2000 or self.main_port != 2100:
            self.main.read_very_eager() # clear buffer
            sn = self.ask('SERIAL()')
            sn = sn.split('Serial_Number: ')[1].split('\n')[0].strip()
            return sn
        else:
            print('Invalid command on Port 2000/2100')
            return None

    def clear_errors(self):
        '''
        Clears the error list
        '''
        self.write('CLEAR ERRORS()')
        response = self.main.read_until(b'Cleared', 0.5)
        return response.decode().strip()

    def powerbox(self, state):
        if self.main_port != 2000 or self.main_port != 2100:
            self.main.read_very_eager() # clear buffer
            query = self.status1()
            while 'STATUS' not in query:
                query = self.status1()
            powerbox_state = int(query.split('POWERBOX: ')[1].split('\n')[0])
            if powerbox_state == 0 and state == 1:
                self.write('M1 POWERBOX({})'.format(state)) # Turning powerbox ON
            elif powerbox_state == 1 and state == 0:
                self.write('M1 POWERBOX({})'.format(state)) # Turning powerbox OFF
        else:
            print('Invalid command on Port 2000/2100')


    def lcd_msg(self, message):
        if self.main_port == 2000:
            self.lcd = telnetlib.Telnet(self.ipaddr, self.lcd_secport, 5)
        elif self.main_port == 1300:
            self.lcd = telnetlib.Telnet(self.ipaddr, self.lcd_port, 5)
        self.lcd.write("STRING({})\r\n".format(message).encode('ascii'))
        self.lcd.close()

    '''
    def lcd_color(self, color):
        """
            0 =  Black (no backlight)
            1 =  White (All colors)
            2 =  Red - Blinking
            3 =  Green
            4 =  Blue
            5 =  Cyan
            6 =  Amber
        """
        color_code = {'black': 0, 'white': 1, 'red': 2, 'green': 3, 'blue': 4, 'cyan': 5, 'amber': 6, 'yellow': 6}
        if type(color) == int:
            if self.main_port == 2000:
                self.lcd = telnetlib.Telnet(self.ipaddr, self.lcd_secport, 5)
            elif self.main_port == 1300:
                self.lcd = telnetlib.Telnet(self.ipaddr, self.lcd_port, 5)
            self.lcd.write("COLOR({})\r\n".format(color).encode('ascii'))
            self.lcd.close()
        else:
            if self.main_port == 2000:
                self.lcd = telnetlib.Telnet(self.ipaddr, self.lcd_secport, 5)
            elif self.main_port == 1300:
                self.lcd = telnetlib.Telnet(self.ipaddr, self.lcd_port, 5)
            self.lcd.write("COLOR({})\r\n".format(color_code[color.lower()]).encode('ascii'))
            self.lcd.close()
    '''

    def lcd_close(self):
        self.lcd_color('white')
        self.lcd_msg('')
        self.lcd.close()

    def main_close(self):
        self.main.close()
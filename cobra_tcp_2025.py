import queue
import socket
import time
import sys
import select
#import telnetlib

global error_msg
global error_check


class cobra_thermal_system:
    def __init__(self, ipaddr, port=1300):
        self.connected = None  # determines if there is established connection with cobra
        self.ipaddr = ipaddr  # gpib address
        self.id_expect = 'STATUS'
        self.main_port = port  # Port 1000 - 60sec timeout
        # Port 1300 - 5sec timeout
        # Port 1100 - No timeout
        # Port 2000 - 5sec timeout [For head 2 on dual Cobra]
        # Port 2100 - No timeout [For head 2 on dual Cobra]
        # Port 3001 - Only for sending diode temp readings through TCP/IP for TSD feedback (Experimental)
        self.lcd_port = '1001'  # LCD port for head 1 - 60sec timeout
        self.lcd_secport = '2001'  # LCD port for head 2 - 60sec timeout
        self.main = None  # Telnet Object for Cobra Unit
        self.lcd = None  # Telnet Object for LCD Unit
        self.sock = None
        self.sock_to = None
        self.define_timeout()
        self.cobra_connect()
        # self.assign_id()

    def define_timeout(self):
        match self.main_port:
            case '1000':
                self.sock_to = 60
            case '1100':
                self.sock_to = 0
            case '2000':
                self.sock_to = 1000
            case '2100':
                self.sock_to = 0
            case '1111':
                self.sock_to = 5
            case '1112':
                self.sock_to = 5
            case '1300':
                self.sock.to = 120

    def cobra_connect(self): # 5/13 DREYES | NEW METHOD FOR CONNECTING TO THE COBRA.
        global error_check # Why global?????
        global error_msg #  Why global? This seems inefficient
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.sock_to)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.sock.connect((self.ipaddr, int(self.main_port)))
            if self.main_port == '1000' or self.main_port == '1100' or self.main_port == '1111':
                self.sock.sendall('STATUS2()\r\n'.encode())
                print(self.sock.recv(1024).decode())
                self.connected = True
            else:
                self.sock.sendall('STATUS()\r\n'.encode())
                print(self.sock.recv(1024).decode())
                self.connected = True
        except socket.timeout:
            print("Timed out waiting for response")
            self.connected = False
        except socket.error as e:
            error_msg = 'Problem connecting system using IP Address {}\n' \
                        'Please check IP address is correct'.format(self.ipaddr)
            error_check = 2
            self.connected = False
            return error_msg
    '''
    def assign_id(self): # USED OLD TELNET LIB DEPRECATED AFTER 3.12
        global error_msg
        global error_check
        error_check = 0
        try:
            self.main = telnetlib.Telnet(self.ipaddr, self.main_port, 5)
            id_query = self.ask('STATUS2()')
            if self.id_expect not in id_query:
                # print('****************************************************************************') print(
                # 'Problem connecting to ip address {}. \n Response to STATUS1(): {}'.format(self.ipaddr, id_query))
                # print('One method to bring back comm link is to power cycle cobra unit')
                error_check = 1
                error_msg = 'Problem connecting to ip address {}. \n Response to STATUS2(): {}\n' \
                            'One method to bring back comm link is to power cycle Cobra unit'.format(self.ipaddr,
                                                                                                     id_query)
            self.connected = True
        except:
            # print('Problem connecting {} {} using IP Address {}'.format(self.name, self.type, self.ipaddr))
            # print('****************************************************************************')
            error_check = 2
            error_msg = 'Problem connecting system using IP Address {}\n' \
                        'Please check IP address is correct'.format(self.ipaddr)
    '''
    def is_connected(self):
        try:
            readable, _, _ = select.select([self.sock], [], [], 0)
            if readable:
                data = self.sock.recv(1, socket.MSG_PEEK)
                if not data:
                    return False  # Connection is closed
            return True  # Still connected
        except (socket.error, OSError):
            return False  # Likely disconnected

    def reconnect(self):
        x = 0# reconnect to the cobra system
        for x in range(0, 20):
            print("Attempting to reconnect to the cobra...")
            try:
                self.main_close()
                self.main = telnetlib.Telnet(self.ipaddr, self.main_port, 5)
                time.sleep(50)
                print("Reconnected to the cobra")
                break
            except TimeoutError:
                time.sleep(5)
                continue
        if x > 20:
            print("Failed to connect to the cobra: Connection Reset Error")

    def write(self, command):
        self.main.write('{}\r\n'.format(command).encode('ascii'))

    def clr_bfr(self):
        self.sock.setblocking(False)
        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    break
        except BlockingIOError:
            # No more data to read (buffer is empty)
            pass
        finally:
            self.sock.setblocking(True)  # Restore blocking mode

    def ask(self, command):
        #OLD OLD METHOD
        #self.main.write('{}\r\n'.format(command).encode('ascii'))
        #query = self.main.read_until(b'\r\n', 5)
        #return query.decode()
        ############################################################
        #OLD
        #self.main.read_until(b'\r\n', timeout=0.5)
        #self.main.write(bytes(command + '\r\n', 'utf-8'))
        #query = self.main.read_until(b'\r\n', timeout=0.5)
        #return query.decode('ascii').strip()
        ############################################################
        # TODO: 5/13 New method needs testing
        command_wr = command + '\r\n'
        try:
            self.sock.sendall(command_wr.encode('ascii'))
            time.sleep(0.5)
            response = b''
            while not response.endswith(b'\r\n'):  # or whatever your delimiter is
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            #resp = self.sock.recv(1026).decode()
            return response.decode().strip('\r\n')
        except socket.timeout:
            print("Timed out waiting for response")
            self.sock.close()
            self.cobra_connect()
        except socket.error as e:
            self.sock.close()
            print("Lost Connection to Cobra")
            raise


    def recv(self):
        query = self.main.read_until(b'\r\n', timeout=0.5)
        return query.decode('ascii').strip()

    # Outdated status command, less information provided in response compared to STATUS2
    def status(self):
        #self.main.read_very_eager()  # clear buffer
        response = self.ask('STATUS()')
        return response

    def status1(self):
        #self.main.read_very_eager()  # clear buffer
        response = self.ask('STATUS1()')
        return response

    def status2(self):
        #self.main.read_very_eager() # clear buffer
        response = self.ask('STATUS2()')
        return response

    def status4(self): #4/8 DReyes: new for port 1111
        #self.main.read_very_eager()
        response = self.ask('STATUS4()')
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
        '''
        time.sleep(0.5)
        query = self.status1()
        while 'STATUS' not in query:
            query = self.status1()
        power_state = (query.split('HEAD_STATE: ')[1].split('\n')[0])

        if power_state == 'DISABLED' and state == 1:
            print('Turning compressor ON')
            response = self.ask('POWER({})'.format(state))
            return response

        elif power_state == 'RUN' and state == 0:
            print('Turning compressor OFF')
            response = self.ask('POWER({})'.format(state))
            return response
        '''
        if state == 1:  # 4/17 New Compact Method, does not need run state to get a response. The user should know how to handle the error
            print('Turning compressor ON')
            response = self.ask('POWER({})'.format(state))
            return response

        elif state == 0:
            print('Turning compressor OFF')
            response = self.ask('POWER({})'.format(state))
            return response


    def read_head_position(self):
        response = self.status1()
        while 'STATUS' not in response:
            response = self.status1()
        position = response.split('POWERDRIVE: ')[1].split('\n')[0]
        return position

    def set_temp(self, temp):
        # temp = float(temp)
        #self.main.read_very_eager()  # clear buffer
        if temp > 150:
            # self.lcd_color('red')
            # self.lcd_msg('User Error!')
            msg = 'Set temperature too high. ({}) Assuming error and exiting. Please check config and restart.'.format(
                temp)
            print(msg)
            sys.exit(msg)
        return self.ask('SET TEMP({})'.format(temp))
        # if temp > 60.0:
        # self.lcd_color('amber')
        # self.lcd_msg('Hot Temp')
        # elif temp > 15.0:
        # self.lcd_color('green')
        # self.lcd_msg('Nominal Temp')
        # else:
        # self.lcd_color('cyan')
        # self.lcd_msg('Cold Temp')

    def tsd_feedback(self, state):
        '''
        Turn ON (1) or OFF (0) TSD Feedback mode
        '''
        '''self.ask('TSD FEEDBACK({})'.format(state))
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
        '''

        response = self.ask('TSD FEEDBACK({})'.format(state))
        print(response)
        return response

    def tj_priority(self, diode):
        '''
        change which diode on multichannel TSD to use as feedback
        '''
        response = self.ask('TJ_PRIORITY({})'.format(diode))
        print(response)
        return response


    def feedback(self, type): # 4/8 DReyes: New function to change temperature feedback type
        '''
        change feedback type
        '''
        response = self.ask('FEEDBACK({})'.format(type))
        print(response)
        return response

    def read_temps(self):
        """
        Returns Temperatures as [TCASE, TEVAP, TSD] (e.g. Tcase = read_temp()[0])
        """
        #self.main.read_very_eager()  # clear buffer
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

    def tcase1_calibrate(self, gain, offset): # TODO: 4/26 Dreyes, Verify command set. Deprecated?
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

        return response_gain, response_offset

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

        return response_gain, response_offset

    def heater_override(self, value):
        '''
        Manually set heater percentage and override PID controls.
        Value must be nonnegative or else PID will resume control and manual override disabled.
        '''
        if value < 0:
            response = 'HEATER OVERRIDE DISABLED'
        else:
            response = self.ask('HEATER OVERRIDE({})'.format(value))

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

    def set_force(self, force, index=0):
        '''
        Sets the force of DUT <index> to <force> LBS
        '''
        response = self.ask(f'SET DUT_{index} FORCE({force})')
        #response = self.main.read_until(b'.0', 0.5)
        return response

    def new_datalog(self):
        #self.main.read_very_eager()  # clear buffer
        response = self.ask('NEW DATALOG()')
        return response

    def ss_target(self, target): #4/8/2025 DReyes: read untils for different edge cases
        '''
        Sets the heater% to new target value
        Response format: "Update Config NEW Steady State Target value = X.000000"
        '''
        response = self.ask('SS TARGET({})\r\n'.format(str(target)))
        return response

    def dut_list(self):
        #self.main.read_very_eager()  # clear buffer
        list = self.ask('DUT NAMES()')
        return list

    def select_dut(self, dut):
        #self.main.read_very_eager()  # clear buffer
        '''
        checklist = self.dut_list()
        if str(dut) in checklist:
            self.write('SELECT DUT({})'.format(dut))
        else:
            error_msg = 'Error: DUT not found'
            return error_msg
        '''
        response = self.ask('SELECT DUT({})'.format(str(dut)))
        print(response)
        return response

    def set_rpm(self, rpm):
        '''
        For Sea Cobra(E) only. Manually set RPM of compressor
        '''
        #self.main.read_very_eager()  # clear buffer
        response = self.ask('RPM({})'.format(rpm))
        """if "NEW" in response:
            return response
        elif 'Override' in response:
            error_msg = 'Invalid RPM value; must be 1500-5500'
            return error_msg
        else:
            error_msg = 'Command sent but no response received'
            return error_msg"""
        return response

    def serial_number(self):
        if self.main_port != 2000 or self.main_port != 2100:
            #self.main.read_very_eager()  # clear buffer
            sn = self.ask('SERIAL()')
            return sn
        else:
            print('Invalid command on Port 2000/2100')
            return None

    def clear_errors(self):
        '''
        Clears the error list
        '''
        response = self.ask('CLEAR ERRORS()')
        print(response)
        return response

    def help(self):
        '''
        obtains list of commands
        '''
        response = self.ask('HELP()')
        print(response)
        return response

    def som_status(self):
        '''
        obtains information about SOM
        '''
        response = self.ask('SOM STATUS()')
        print(response)
        return response

    def gui_ip(self):
        '''
        obtains Host name and Host IP
        '''
        response = self.ask('GUI IP()')
        print(response)
        return response

    def powerbox(self, state):
        #if self.main_port != 2000 or self.main_port != 2100:
            #self.main.read_very_eager()  # clear buffer
        query = self.status1()
        while 'STATUS' not in query:
            query = self.status1()
        powerbox_state = str(query.split('POWERBOX: ')[1].split('\n')[0])
        #logic branch needs to be redone
        #if powerbox_state == "OFF" and state == 1:
        if state == 1:
            return self.ask('POWERBOX({})'.format(state))  # Turning powerbox ON
        #elif powerbox_state == "ON" and state == 0:
        if state == 0:
            return self.ask('POWERBOX({})'.format(state))  # Turning powerbox OFF
        #else:
        #    print('Invalid command on Port 2000/2100')

    def n_factor(self, value):
        #self.main.read_very_eager()
        response = self.ask('N-FACTOR({})'.format(value))
        return response

    def set_ramp_rate(self, ramp_rate):
        '''
        Sets the M1 ramp rate in degrees per minute
        '''
        #self.main.read_very_eager()  # clear buffer
        response = self.ask('RAMP RATE({})'.format(ramp_rate))
        if "NEW" in response:  # Checks if the Cobra's response is valid: command was accepted fine
            return response
        elif 'INVALID' in response:  # Checks if the user input is within the expected range for this command
            error_msg = 'Invalid ramp rate value; must be 1500-5500'
            return error_msg
        else:  # Last check that will display an error message if the above two conditions aren't met
            error_msg = 'Command sent but no response received'
            return error_msg

    def event_test(self):
        #self.main.read_very_eager()
        response = self.ask('EVENT TEST()')
        return response

    def warning_test(self):
        #self.main.read_very_eager()
        response = self.ask('WARNING TEST()')
        return response

    def fault_test(self):
        #self.main.read_very_eager()
        response = self.ask('FAULT TEST()')
        return response

    """
    def lcd_msg(self, message):
        if self.main_port == 2000:
            self.lcd = telnetlib.Telnet(self.ipaddr, self.lcd_secport, 5)
        elif self.main_port == 1300:
            self.lcd = telnetlib.Telnet(self.ipaddr, self.lcd_port, 5)
        self.lcd.write("STRING({})\r\n".format(message).encode('ascii'))
        self.lcd.close()

    def lcd_color(self, color):

            #0 =  Black (no backlight)
            #1 =  White (All colors)
            #2 =  Red - Blinking
            #3 =  Green
            #4 =  Blue
            #5 =  Cyan
            #6 =  Amber

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


    def lcd_close(self):
        self.lcd_color('white')
        self.lcd_msg('')
        self.lcd.close()
    """

    def cancel_log(self): # 4/28 DReyes
        '''
        Cancels Hyperlog
        '''
        response = self.ask('CANCEL LOG()')
        return response

    def end_log(self): # 4/28 DReyes
        '''
        Ends Hyperlog
        '''
        response = self.ask('END LOG()')
        return response

    def start_log(self): # 4/28 DReyes
        '''
        Starts Hyperlog
        '''
        response = self.ask('START LOG()')
        return response

    def tsd_gain(self, gain=None):
        if gain is not None:
            response = self.ask('TSD GAIN({})'.format(gain))
        else:
            response = self.ask('TSD GAIN()')
        return response

    def close_connection(self):
        self.sock.shutdown(socket.SHUT_RDWR)  # Disable both send and receive
        self.sock.close()

    #def main_close(self):
    #    self.main.close()

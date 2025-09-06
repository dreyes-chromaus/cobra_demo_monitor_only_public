import paramiko

class som_com:
    def __init__(self, cobra_ip):
        self.hostname = cobra_ip
        self.username = 'admin'
        self.password = 'admin'
        self.som_client = None
        self.init_com()

    def init_com(self):
        # Connect
        self.som_client = paramiko.SSHClient()
        self.som_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.som_client.connect(self.hostname, username=self.username, password=self.password)

    def os_reboot(self):
        if self.som_client.get_transport() is None or not self.som_client.get_transport().is_active():
            self.init_com()
        try:
            stdin, stdout, stderr = self.som_client.exec_command("sudo reboot")

            output = stdout.read().decode()
            error = stderr.read().decode()

            stdin.close()
            stdout.close()
            stderr.close()

        except paramiko.SSHException as e:
            print(f"SSH error during os_reboot: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error during os_reboot: {e}")
            return []


    def dir_read(self):
        # Check if the SSH client is connected, reconnect if needed
        if self.som_client.get_transport() is None or not self.som_client.get_transport().is_active():
            self.init_com()

        try:
            # Commands must be all in one STRING or else each call of exec_command creates a new instance
            # of SSH. In the case of changing directories and then using ls -l, causes a readback of the
            # contents from the wrong directory
            stdin, stdout, stderr = self.som_client.exec_command("cd /U && echo $PWD && ls -l")

            output = stdout.read().decode()
            error = stderr.read().decode()

            stdin.close()
            stdout.close()
            stderr.close()

            if error:
                print(f"Error reading directory: {error.strip()}")
                return []

            # Parse and clean up output lines, skip 'total' line
            lines = [line for line in output.strip().split('\n') if line and not line.startswith('total')]
            file_info_list = []

            for line in lines:
                parts = line.split(None, 8)  # Split into max 9 parts to preserve filenames with spaces
                if len(parts) < 9:
                    print(f"Skipping malformed line: {line}")
                    continue

                try:
                    file_info = {
                        "permissions": parts[0],
                        "links": int(parts[1]),
                        "owner": parts[2],
                        "group": parts[3],
                        "size": int(parts[4]),
                        "month": parts[5],
                        "day": parts[6],
                        "time_or_year": parts[7],
                        "name": parts[8],
                    }
                    file_info_list.append(file_info)
                except ValueError as ve:
                    print(f"Failed to parse line: {line} — {ve}")
                    continue

            return file_info_list

        except paramiko.SSHException as e:
            print(f"SSH error during dir_read: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error during dir_read: {e}")
            return []

    def mem_read(self):
        # Run the command
        if self.som_client.get_transport() is None:
            self.init_com()
        stdin, stdout, stderr = self.som_client.exec_command('free -m')
        mem_read_str = stdout.read().decode()
        stdin.close()
        stdout.close()
        stderr.close()
        #self.som_client.close()
        return mem_read_str

    def mem_free(self):
        output = self.mem_read()
        output = output.split()
        free = [output[2], output[9]]
        return free

    def mem_read_split(self):
        output = self.mem_read()
        output = output.split()
        #split output
        total = [output[0], output[7]]
        used = [output[1], output[8]]
        free = [output[2], output[9]]

        print(total[0] + '\t\t' + used[0] + '\t\t' + free[0])
        print(total[1] + 'MB\t\t' + used[1] + 'MB\t\t' + free[1] + 'MB')
        return total[1], used[1], free[1]



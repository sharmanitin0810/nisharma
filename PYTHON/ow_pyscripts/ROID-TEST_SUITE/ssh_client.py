##################################################################################################################################
#  Copyright Copyright (c) 2020 Hughes Network System, LLC.
#
#  FILE NAME: ssh_client.py
#
#  DESCRIPTION: Abstract class over Paramiko's SSH Client. 
#
#  DATE           NAME          REFERENCE       REASON
#  06/08/2020     A.Deb         SPR83952     Initial Create.
#
##################################################################################################################################

import paramiko

class SSHClient:
    def __init__(self, hostname, username, password, init_sftp_flag = False):
        self.hostname = hostname
        self.username = username
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client_exception = False
        self.init_sftp_flag = init_sftp_flag
        try:
            self.ssh_client.connect(hostname = self.hostname, username = self.username, password = password)
        except Exception as e:
            print("Could not initialize SSH Client. Reason : " + str(e))
            self.ssh_client_exception = True
        if self.init_sftp_flag and not self.ssh_client_exception:
            self.ftp_client = self.ssh_client.open_sftp()

    def cleanUpLists(self, input_list):
        input_list = [data for data in input_list if self.username not in data]
        return input_list

    def executeCommand(self, command, input = None):
        if not self.ssh_client_exception:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, get_pty=True)
            channel = stdout.channel
            if input:
                stdin.write(str(input) + "\n")
                return_code = channel.recv_exit_status()
                stdout = self.cleanUpLists(stdout.readlines())
                stderr = self.cleanUpLists(stderr.readlines())
                return (return_code, stdout, stderr)
            
            return_code = channel.recv_exit_status() 
            return(return_code, stdout.readlines(), stderr.readlines()) 
        else:
            return(1, [], [])

    def get(self, remote_file_path, local_file_path):
        if self.init_sftp_flag and not self.ssh_client_exception:
            try:
                self.ftp_client.get(remote_file_path, local_file_path)
            except Exception as e:
                print("Error getting file. Reason : " + str(e))
        else:
            print("Exception occured in initialzing client or SFTP is not supported by the remote server.")

    def put(self, local_file_path, remote_file_path):
        if self.init_sftp_flag and not self.ssh_client_exception:
            try:
                self.ftp_client.put(local_file_path, remote_file_path)
            except Exception as e:
                print("Error putting file. Reason : " + str(e))
        else:
            print("Exception occured in initialzing client or SFTP is not supported by the remote server.")

    def __del__(self):
        if self.init_sftp_flag and not self.ssh_client_exception:
            self.ftp_client.close()

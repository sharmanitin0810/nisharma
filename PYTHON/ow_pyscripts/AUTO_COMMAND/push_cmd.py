#-----------------------------------------------------------------------------------------
# PURPOSE: To run multile commands parrellely on multiple reachable nodes.
#
# SOURCE CODE FILE: push-cmd.py
#
# REVISION HISTORY:
#          DATE:           AUTHOR:         CHANGE:
#          12-02-20        Nitin Sharma    Initial version
#          30-03-21        Nitin Sharma    Final version
#
# Copyright 2019 Hughes Network Systems Inc
#-----------------------------------------------------------------------------------------
#!/usr/bin/python
# Version 2

###############################################################################
#
#       Prerequisites to run this script:
#       ---------------------------------------
#               - Python 2.7 must be installed
#       Command Line Parameters to this script:
#		-N/A	
#       ---------------------------------------
#		
#       Return values of the script:
#       ----------------------------
#               On successful execution, the exit status is 0
#
###############################################################################


import os
import signal
import sys
import time
import logging
import paramiko
from datetime import datetime
from subprocess import call
import subprocess
import errno


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

def create_log_dir():
     dir_log = 'auto_logs'
     try:
        os.mkdir(dir_log)
        print("Logger Directory is Created")

     except OSError as e:
           if e.errno == errno.EEXIST:
              print("Log Directory already Exist - Not Creating Again")

def chk_node_status(node_ip):
	try:	
		print('Going to check the IP connectivity of node :' + str(node_ip))
		#node_rsp = os.system("ping -i 1 -c 3" + node_ip)
		node_rsp = subprocess.check_output(["ping", "-c", "3", node_ip])
		return True

	except subprocess.CalledProcessError:
		return False

def push_cmds():
	current_dir = os.getcwd()
        target_nodes=open("ip-list.txt")
        user_cmd=open("cmd-list.txt")
        cmd=user_cmd.read()
        #print(cmd)
        USERNAME='msat'
        PASSWORD='oneweb123'
        for line in target_nodes:
                   print('Accessing Host :' + str(line))
	           node_stat = chk_node_status(line)
		   #print("NOde stats :",node_stat)
	           if node_stat == True:
			print("[SUCCESS] GN component :" +str(line)+ " " + "is reachable")
			print("Executing commands on GN component ..Please wait..")
                   	logger.info("Entering for loop")
	                ssh = paramiko.SSHClient()
        	        ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
                	ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
	                try:
        	           ssh.connect(line, username=USERNAME, password=PASSWORD, timeout = 10)
			   stdin, stdout, stderr = ssh.exec_command(cmd)
			   print(" ********* Command Output ************ \n ")
			   for line in stdout.read().splitlines():
			      print(line)

		     	   print(' *********** Command(s) Executed *************** : \n'+ str(cmd))
	                   logger.info("SSH and Commands executed successfully")
        	           ssh.close()

                	except Exception as e:
	                      logger.critical('Not reachable',e)
		   else:
			print("[FAILED] GN component:" +str(line)+ " "+ "is not reachable")

	target_nodes.close()
	user_cmd.close()

if __name__=="__main__":

        signal.signal(signal.SIGINT,signal_handler)
        signal.signal(signal.SIGTSTP,signal_handler)

        os.system("clear")

        time.sleep(1)
        create_log_dir()

        #Basic Configuration for Generating Logs

        logFname = datetime.now().strftime('auto_run_%d_%m_%Y:%H_%M.log')
        logging.basicConfig(filename='auto_logs/%s' %(logFname),level=logging.DEBUG,format='%(asctime)s : %(message)s ')
        logger = logging.getLogger()
        logger.info("Log directory is successfully created")
        os.system("clear")

        push_cmds()

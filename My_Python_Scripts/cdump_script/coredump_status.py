#PURPOSE:To verify presence of core files on GN Components
#
# SOURCE CODE FILE: coredump_status.py
#
# REVISION HISTORY:
#          DATE:           AUTHOR:         CHANGE:
#          27-08-2020      Nitin           Final version
#
# Copyright 2019 Hughes Network Systems Inc
#-----------------------------------------------------------------------------------------
#!/usr/bin/python
# Version 2

###############################################################################
#
#          Prerequisites to run this script:
#       ---------------------------------------
#               - Python 2.7 must be installed
#               - gn-iplist.txt file should be configured with ip/hostname \
#		  of GN Components.
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
import errno
from datetime import datetime
from subprocess import call


# Created vars to store ip and hostname
ipAd=''
IpList = []

# Basic loging configuration 
logger = paramiko.util.logging.getLogger()
logging.getLogger("paramiko").setLevel(logging.WARNING)

#####################################
# --- Function to Handle Signal --- #
#####################################

def signal_handler(signal,frame):
        logging.info("Entering Signal Handler to Handle Recieved Signal")
        print(" Successfully exited on User Request !! ")
        sys.exit(0)

################################################
# --- Function to Create Directory for Log --- #
################################################

def create_log_dir():
        dir_log = 'logs'
        try:
           os.mkdir(dir_log)
           print("Logger Directory is Created Successfully")

        except OSError as e:
            if e.errno == errno.EEXIST:
                print("Log Directory already Exist - Not Creating Again")

#########################################################
# --- Function to check core files on GN components --- #
#########################################################

def check_core_files(host,ipAd):
    path = '/home/msat/cores'
    rcmd = 'ls %s | wc -l' %(path)
    listrcmd = 'ls -ltr %s'  %(path)
    USERNAME='msat'
    PASSWORD='oneweb123'
    
    #signal.signal(signal.SIGINT,signal_handler)
    #signal.signal(signal.SIGTSTP,signal_handler)
    host = ipAd.replace("'","")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
    #ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    try:

        ssh.connect(host, username=USERNAME, password=PASSWORD, timeout = 10)
        stdin, stdout, stderr = ssh.exec_command(rcmd)
        logging.info("*******************Checking core files on GN Component*****************")
        output = stdout.read().decode('ascii').strip("\n")

        if int(output) == 0:
            logging.info("No any core file generated on host [ %s ]" %(host))
        else:
            logging.error(" CRITICAL: [%s] Core files are generated on host " %(output))
            crcmd  = 'ls -lrt %s' %(path)
            ssh.connect(host, username=USERNAME, password=PASSWORD, timeout = 10)
            stdin, stdout, stderr = ssh.exec_command(crcmd)
            for lines in stdout:
                #print("%s" %(lines))
                logging.info("%s" %(lines))
            time.sleep(2)
        ssh.close()

    except Exception as e:
        	ssh.close()

################################################################
# --- Function to derive ip & hotsname form gn-iplist file --- #
################################################################

def derive_ip_host():

       logFname = datetime.now().strftime('core_verify_%H_%M_%d_%m_%Y.log')
       logging.basicConfig(filename='logs/%s' %(logFname),level=logging.DEBUG,format='%(asctime)s : %(message)s')

       global IpList
       i = 0

       signal.signal(signal.SIGINT,signal_handler)
       signal.signal(signal.SIGTSTP,signal_handler)

       hosts = open('gn-iplist.txt','r')
       hostList = [line.strip() for line in hosts if line.strip()]

       for line in hostList:
            try:
                if "#" in line or "local" in line:
                        continue
                #print "HostName: %s Ip Addr: %s" %(line.split()[1:],line.split()[:1])
                IpList.append(line.split()[1:])
                IpList.append(line.split()[:1])

                #print ('IP list : ',IpList)
                host = str(IpList[i])
                host = host.replace("[", "")
                host = host.replace("]", "")
                #print ('Host List : ', host)

                i += 1
                ip = str(IpList[i])
                ip = ip.replace("[", "")
                ip = ip.replace("]", "")

                ## Verifcation starts for core files
                logging.info("********************************************************")
                logging.info("*** Verification started for Host: %s Ip: %s ***" %(host,ip))

                check_core_files(host,ip)

                logging.info("********* Verification End ***********")
		logging.info("\n")

                i += 1
                #print "Host:%s Ip:%s" %(host,ip)
            except (KeyboardInterrupt, SystemExit):
                logging.info ("Script Aborted by User ")


######################################################
# --- Execution starts from Here - MAIN_FUNCTION --- #
######################################################

if __name__ == '__main__':

	#signal.signal(signal.SIGINT,signal_handler)
        #signal.signal(signal.SIGTSTP,signal_handler)

	time.sleep(1)
	create_log_dir()
	os.system('clear')

        derive_ip_host()
	


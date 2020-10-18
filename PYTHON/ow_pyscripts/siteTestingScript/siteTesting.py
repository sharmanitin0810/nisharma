#!/usr/bin/python
#-----------------------------------------------------------------------------------------
# PURPOSE: To check health status of all the nodes of Ground Network
#
# SOURCE CODE FILE: siteTesting.py
#
# REVISION HISTORY:
#          DATE:           AUTHOR:         CHANGE:
#          07-05-19        HSC		    Initial version
#          29-05-19        HSC 		    Final version
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
#               -N/A
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
ipAd=''
IpList = []

logger = paramiko.util.logging.getLogger()
logging.getLogger("paramiko").setLevel(logging.WARNING)

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

def pingTest(host):
    hostname = str(ipAd)
    cmd = "ping -c 1 "  + hostname
    print cmd
    response = os.system(cmd)
    # and then check the response...
    print response
    if response == 0:
        logging.info("Host: %s with IP: %s is reachable" %(host))
    else:
        logging.warning("Host: %s with IP: %s is not reachable" %(host))

def checkSystem(host,ipAd):
    path = '/var/cores/'
    rcmd = 'ls %s | wc -l' %(path)
    listrcmd = 'ls -ltr %s'  %(path)
    USERNAME='msat'
    PASSWORD='oneweb123'
    #print rcmd
    #op = call(rcmd)
    #op = os.system(rcmd)
    #print op
    #sys.exit(0)
    host = ipAd.replace("'","")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    try:
       
        #ssh.connect(ipAd, username="msat", password="oneweb123")
        ssh.connect(host, username=USERNAME, password=PASSWORD, timeout = 10)
        stdin, stdout, stderr = ssh.exec_command(rcmd)
        #stdin, stdout, stderr = ssh.exec_command(listrcmd)
	logging.info("*******************Checking core files...*****************")
        output = stdout.read().decode('ascii').strip("\n")
        #output = ssh_stdout.readlines()
        #print output
        #logging.info("Core file test output: %s" %(output))
        #ssh_stdin.flush()
        if int(output) == 0:
	    logging.info("Core file not generated...")
        else:
	    logging.error(" %s Core file generated..." %(output))
            crcmd  = 'ls -lrt %s' %(path)
            ssh.connect(host, username=USERNAME, password=PASSWORD, timeout = 10)
            stdin, stdout, stderr = ssh.exec_command(crcmd)
            for lines in stdout:
	        logging.info("%s" %(lines))
            time.sleep(2)
        ssh.close()

	logging.info("*******************Checking disk usage...*****************")
        dcmd  = 'df -h'
        ssh.connect(host, username=USERNAME, password=PASSWORD, timeout = 10)
        stdin, stdout, stderr = ssh.exec_command(dcmd)
        #output = stdout.read().decode('ascii').strip("\n")
        for lines in stdout:
	    logging.info("%s" %(lines))
            #print "  %s" %(lines)
        time.sleep(2)
        ssh.close()
        
	logging.info("*******************Checking Time sync...*****************")
	ccmd  = 'chronyc tracking'
        ssh.connect(host, username=USERNAME, password=PASSWORD, timeout = 10)
        stdin, stdout, stderr = ssh.exec_command(ccmd)
        #output = stdout.read().decode('ascii').strip("\n")
        for lines in stdout:
	    logging.info("%s" %(lines))
            #print "  %s" %(lines)
        time.sleep(2)
        ssh.close()
        
	logging.info("*******************Checking process status...*****************")
	pcmd  = 'ps -ef | grep -E "procmon|netman|LTP|lcp|ATP|acp|BTP|bcp|AMS|PLS|rms|ems|xeon|dsmapp"'
        ssh.connect(host, username=USERNAME, password=PASSWORD, timeout = 10)
        stdin, stdout, stderr = ssh.exec_command(pcmd)
        #output = stdout.read().decode('ascii').strip("\n")
        for lines in stdout:
	    logging.info("%s" %(lines))
            #print "  %s" %(lines)
        time.sleep(2)
        ssh.close()
        '''
        logging.info("*******************Checking mtu size...*****************")
        ifcmd  = 'ifconfig -a'
        ssh.connect(host, username=USERNAME, password=PASSWORD, timeout = 10)
        stdin, stdout, stderr = ssh.exec_command(ifcmd)
        #output = stdout.read().decode('ascii').strip("\n")
        #logging.info("%s" %(stdout))
        for lines in stdout:
            logging.info("%s" %(lines))
        #print "  %s" %(lines)
        time.sleep(2)


        ssh.close()
	'''
    except Exception as e:
        ssh.close()
    ''' 
    except paramiko.AuthenticationException:
        logging.error("Authentication failed, please verify your credentials: %s")
    except paramiko.SSHException as sshException:
        logging.error("Unable to establish SSH connection: %s" % sshException)
    except paramiko.BadHostKeyException as badHostKeyException:
        logging.error("Unable to verify server's host key: %s" % badHostKeyException)
    except paramiko.ChannelException:
        logging.error("SSH channel failed")
    except paramiko.BadAuthenticationType:
        logging.error("SSH bad authentication")
    except paramiko.ssh_exception.NoValidConnectionsError:
        logging.error("SSH Not a valid connection")
    ssh.close()
    '''
#def checkDiskUsage():
        
def main():
        logFname = datetime.now().strftime('remoteTest_%H_%M_%d_%m_%Y.log')
        logging.basicConfig(filename='log/%s' %(logFname),level=logging.DEBUG)
	global IpList
        i = 0
	signal.signal(signal.SIGINT, signal_handler)
	hosts = open('site-ip.txt','r')
        hostList = [line.strip() for line in hosts if line.strip()]
        
	for line in hostList:
            try:
                if "#" in line or "local" in line:
			continue
		#print "HostName: %s Ip Addr: %s" %(line.split()[1:],line.split()[:1])
                IpList.append(line.split()[1:])
                IpList.append(line.split()[:1])
                
                
                print ('IP list : ',IpList)
                host = str(IpList[i])
                host = host.replace("[", "")
                host = host.replace("]", "")
                print ('Host List : ', host)
                    
                i += 1
                ip = str(IpList[i])
                ip = ip.replace("[", "")
                ip = ip.replace("]", "")
                ## Execute tests ##
                logging.info("********************************************************")
                logging.info("*** Test started for Host: %s Ip: %s ***" %(host,ip))
                pingTest(host)
                checkSystem(host,ip)
                


                logging.info("********* Test End ***********")  
                i += 1
       		#print "Host:%s Ip:%s" %(host,ip)
            except (KeyboardInterrupt, SystemExit):
		print "Stopping Script on User request"
        #print IpList

if __name__ == '__main__':
	main()

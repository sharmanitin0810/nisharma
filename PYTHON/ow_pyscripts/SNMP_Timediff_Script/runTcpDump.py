#-----------------------------------------------------------------------------------------
# PURPOSE: Calculate the SNMP response delay from RCM to BUCAMP
#
# SOURCE CODE FILE: runTcpDump.py
#
# REVISION HISTORY:
#          DATE:           AUTHOR:         CHANGE:
#          03-20-20        Surya Prakash   Initial version
#
# Copyright 2017 Hughes Network Systems Inc
#-----------------------------------------------------------------------------------------

#!/usr/bin/python
import os
import signal
import sys
import time
import logging
import paramiko
from datetime import datetime, date
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
'''
def checkSnmpDelay(host):
        f=open("snmpOpt.txt")
        spt = 0
        sgt = 0
        dCntr = 0
        tCntr = 0
        for line in f:
            if "F=apr" in line:
                gTime = line.split()
                reqTime = gTime[0].split(".")
                spt = int(reqTime[1])
            elif "F=ap" in line:
                pTime = line.split()
                resTime = pTime[0].split(".")
                sgt = int(resTime[1])
            if spt and spt !=0 and sgt and sgt !=0:
               timDiff = (sgt - spt)/1000
               #print "Delay in SNMP response:%s milliseconds" %(timDiff)
               tCntr +=1
               spt = 0
               sgt = 0
               if timDiff > 10:
                   dCntr +=1
                   print "Delay in SNMP response is greater than 10 milliseconds on host %s delay %s" %(host,timDiff)
                   logger.info("Delay in SNMP response is greater than 10 milliseconds on host %s" %host)
        print("Total snmp requests timeouts: %s out of %s requests" %(dCntr,tCntr))
'''

def timeDiffFunc(host):
        print host
        f=open("snmpOpt.txt")
        spt = 0
        sgt = 0
        resTime = 0
        reqTime = 0
        timD = 0
        fName = host.rstrip()+"_timeDiff.txt"
        if os.path.exists(fName):
            os.remove(fName)
        file1 = open(fName,"a")#append mode

        for line in f:
            if "F=apr " in line:
                gTime = line.split()
                #reqTime = gTime[0].split(".")
                #spt = int(reqTime[1])
                o_data = {'RA': gTime[0]}
                #reqTime = datetime.strptime(obs_data[', '%H:%M:%S.%f').time()
                reqTime = datetime.strptime(o_data['RA'], '%H:%M:%S.%f').time()
                #print reqTime
            elif "F=ap " in line:
                if reqTime == 0:
                    continue
                pTime = line.split()
                #resTime = pTime[0].split(".")
                #sgt = int(resTime[1])
                n_data = {'RA': pTime[0]}
                resTime = datetime.strptime(n_data['RA'], '%H:%M:%S.%f').time()
                #print resTime
            if resTime and reqTime:
               diff = datetime.combine(date.today(), resTime) - datetime.combine(date.today(), reqTime)
               timD = diff.total_seconds() * (10 ** 3)
               #print reqTime, resTime,diff.total_seconds() * (10 ** 3)
               resTime = 0
               reqTime = 0
               #delta = resTime - reqTime
               #print "delta = %s" %diff
            if timD != 0:
                file1.write(str(timD))
                file1.write("\n")
                timD = 0

def runTcpdump():
        f=open("ip-list.txt")
        USERNAME='admin'
        PASSWORD='oneweb123'
        for line in f:
                   print('\n\nAccessing Host :' + str(line))
                   logger.info("Entering for loop")
                   output =""
                   ssh = paramiko.SSHClient()
                   ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
                   ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
                   cmd = "echo oneweb123 | sudo -S /usr/sbin/tcpdump -c 500000 | grep snmp > snmpPckt.txt"        # command will never exit
                   try:
                      ssh.connect(line, username=USERNAME, password=PASSWORD, timeout = 10)
		      (stdin,stdout,stderr) = ssh.exec_command(cmd)  # will return instantly due to new thread being spawned.
                      #stdin.write("oneweb123" + "\n")
                      #stdin.flush()
		      time.sleep(180)
                      ssh.exec_command("echo oneweb123 | sudo -S pkill /usr/sbin/tcpdump")
                      ftp_client=ssh.open_sftp()
		      ftp_client.get("/home/admin/snmpPckt.txt","snmpOpt.txt")
		      time.sleep(10)
                      ftp_client.close()
                      ssh.exec_command("rm -f snmpPckt.txt")
                      logger.info("SSH and Command run successfully")
                      ssh.close()
                      print ("Session closed")
                      '''   
                      for line in stdout:
    		          output=output+line
                      if output!="":
                          print (output)
                      '''
                   except Exception as e:
                      print ("Exception occured ! %s" %e)
                      logger.critical('Exception %s ' %(e))
                      continue
                   timeDiffFunc(line)

if __name__=="__main__":

        signal.signal(signal.SIGINT,signal_handler)
        signal.signal(signal.SIGTSTP,signal_handler)

        #os.system("clear")

        time.sleep(1)
        create_log_dir()

        #Basic Configuration for Generating Logs

        logFname = datetime.now().strftime('auto_run_%d_%m_%Y:%H_%M.log')
        logging.basicConfig(filename='auto_logs/%s' %(logFname),level=logging.DEBUG,format='%(asctime)s : %(message)s ')
        logger = logging.getLogger()
        logger.info("Log directory is successfully created")
        os.system("clear")

        runTcpdump()

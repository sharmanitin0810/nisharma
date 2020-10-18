#!/usr/bin/python
import os
import signal
import sys
import time
import logging
import paramiko
from datetime import datetime, time, date
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


def timeDiffFunc():
        f=open("snmpGnOp.txt")
        spt = 0
        sgt = 0
        resTime = 0
        reqTime = 0
        timD = 0
        if os.path.exists("timeDiff.txt"):
            os.remove("timeDiff.txt")
        file1 = open("timeDiff.txt","a")#append mode 
    
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
               print reqTime, resTime,diff.total_seconds() * (10 ** 3)
               resTime = 0
               reqTime = 0
               #delta = resTime - reqTime
               #print "delta = %s" %diff
            if timD != 0: 
                file1.write(str(timD)) 
                file1.write("\n")
                timD = 0 
if __name__=="__main__":

        signal.signal(signal.SIGINT,signal_handler)
        signal.signal(signal.SIGTSTP,signal_handler)

        os.system("clear")

        #time.sleep(1)
        #create_log_dir()

        #Basic Configuration for Generating Logs

        logFname = datetime.now().strftime('auto_run_%d_%m_%Y:%H_%M.log')
        #logging.basicConfig(filename='auto_logs/%s' %(logFname),level=logging.DEBUG,format='%(asctime)s : %(message)s ')
        logger = logging.getLogger()
        logger.info("Log directory is successfully created")
        os.system("clear")

        timeDiffFunc()

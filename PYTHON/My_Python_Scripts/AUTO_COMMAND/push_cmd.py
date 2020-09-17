#!/usr/bin/python
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


def working():
        f=open("/home/msat/LOGS/prd_gn/ip-list.txt")
        g=open("/home/msat/LOGS/prd_gn/cmd-list.txt")
        cmd=g.read()
        #print(cmd)
        USERNAME='msat'
        PASSWORD='oneweb123'
        #rcmd='touch /tmp/a; touch /tmp/b; ls -lrt>/tmp/abb.log'
        for line in f:
                   print('Accessing Host :' + str(line))
                   logger.info("Entering for loop")
                   ssh = paramiko.SSHClient()
                   ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
                   ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
                   try:
                      ssh.connect(line, username=USERNAME, password=PASSWORD, timeout = 10)
		      stdin, stdout, stderr = ssh.exec_command(cmd)
		      print('Command Executed : '+ str(cmd))
                      logger.info("SSH and Command run successfully")
                      ssh.close()
                   except Exception, e :
                      logger.critical('Not reachable',e)

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

        working()

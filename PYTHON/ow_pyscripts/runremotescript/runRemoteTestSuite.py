##################################################################################################################################################
#  Copyright Copyright (c) 2020 Hughes Network System, LLC.
#
#  FILE NAME: runRemoteTestSuite.py
#
#  DESCRIPTION: This script is used for automated testing of user terminal to Ground Network communication over OneWeb satellite constellation.
#
#  DATE           NAME          REFERENCE       REASON
#  08/25/2020     S.Krishna         SPR84256    Initial Draft
#
##################################################################################################################################################

import os
import json
from collections import namedtuple
import sys
import subprocess
from subprocess import check_output
import datetime
from datetime import timezone
import tarfile
import zipfile
import fnmatch
import csv
import re
import shutil
import paramiko
from paramiko import client
import requests
import select
import time
import warnings
import threading
import UT
import config_info
        
if __name__ == "__main__":
    currentTime = datetime.datetime.utcnow()
    startDir = os.getcwd()
    LogDir = startDir +"\\Test"
    if (os.path.isdir(LogDir) == False):
        os.mkdir(LogDir)
    os.chdir(LogDir)
    LogDir+= "\\"+currentTime.strftime("%Y-%m-%d-%H%M%S")
    if (os.path.isdir(LogDir) == True):
        shutil.rmtree(Logdir)
    os.mkdir(LogDir)
    os.chdir(LogDir)
    
    config = config_info.config_info()
    config.loadConfig(startDir+'\\common_config.txt')
    
    UTlist = []
        
    debugFile2 = open('ServerLog_'+currentTime.strftime("%Y-%m-%d-%H%M%S")+'.txt',"w+")
    debugFile3 = open('CNXClientLog_'+currentTime.strftime("%Y-%m-%d-%H%M%S")+'.txt',"w+")
    
    testServerClient = UT.getProxySSHClient(config.proxy_server_ip_gw, config.proxy_server_login_gw, config.proxy_server_pass_gw, config.server_ip, config.server_login, config.server_pass, debugFile2)
    cnxClient = UT.getProxySSHClient(config.proxy_server_ip_ut, config.proxy_server_login_ut, config.proxy_server_pass_ut,config.ut_cnx_ip,config.ut_cnx_login,config.ut_cnx_pass,debugFile3)   

      
      
    with open(startDir+"\\UTlist.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            debugFile = open('UT'+row['UT Id']+'_Log_'+currentTime.strftime("%Y-%m-%d-%H%M%S")+'.txt',"w+")
            UT_obj = UT.UT(row['UT Id'], config, testServerClient, cnxClient, debugFile)
            UT_obj.setTestData(startDir+"\\UTlist.csv")
            UTlist.append(UT_obj)     
    try:
        for UT_obj in UTlist:
            UT_obj.thread = threading.Thread(target=UT.launchUT, args = (UT_obj,startDir+"\\test_suites.json"))
            UT_obj.thread.start()
        while (True in [UT_obj.thread.is_alive() for UT_obj in UTlist]):
           [UT_obj.thread.join(1) for UT_obj in UTlist if UT_obj.thread is not None and UT_obj.thread.is_alive()]		
    except KeyboardInterrupt as e:
        print("keyboard interrupt_main\n")
        for UT_obj in UTlist:
            UT_obj.endProg()
        [UT_obj.thread.join() for UT_obj in UTlist if UT_obj.thread is not None and UT_obj.thread.is_alive()]
			
    #UT.remoteExecCommand(testServerClient,"sudo killall -9 iperf",debugFile2)
    #UT.remoteExecCommand(testServerClient,"sudo killall -9 ping",debugFile2)

    debugFile2.close()
    testServerClient.close()
    for UT_obj in UTlist:
        #UT.remoteExecCommand(UT_obj.cnxClient,"killall -9 iperf", UT_obj.debugFile1)
        #UT.remoteExecCommand(UT_obj.cnxClient,"killall -9 ping", UT_obj.debugFile1)
        UT_obj.debugFile1.close()
        UT_obj.ssmClient.close()
    cnxClient.close()
    debugFile3.close()
    print("exiting\n")    




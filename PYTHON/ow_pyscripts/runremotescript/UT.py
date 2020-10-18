##################################################################################################################################################
#  Copyright Copyright (c) 2020 Hughes Network System, LLC.
#
#  FILE NAME: UT.py
#
#  DESCRIPTION: The UT class and a set of functions are invoked by runRemoteTestSuite.py to execute the suite of tests as soon as the UT is attached to the network
#
#
#  DATE           NAME          REFERENCE       REASON
#  08/25/2020     S.Krishna         SPR84256    Initial Draft
#
##################################################################################################################################################

import csv
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
import re
import shutil
import paramiko
from paramiko import client
import requests
import select
import time
import warnings
import threading

class UT:
    def __init__(self, num, config_file, testServerClient, cnxClient, debugFile1):
        self.threads = []
        self.num = num
        self.ssmClient = None
        self.testServerClient = testServerClient
        self.IP = ""
        self.username = ""
        self.password = "" 
        self.iperf_port = ""
        self.test_name = ""
        self.debugFile1 = debugFile1
        self.config = config_file
        self.debugFiles = []
        self.wan_ip_addr = ""
        self.mgt_ip_addr = ""
        self.endTest=False
        self.cnxClient = cnxClient
        self.test_server_wan = ""
        self.test_server_mgt = ""
        self.system = ""
        self.natPorts = []
    
    def addThread(self, client, cmd, debugFile):
        t = threading.Thread(target=remoteExecCommand, args = (client, cmd, debugFile))
        self.threads.append(t)
        t.start()
        return t
        
    def addTest(self, Test):
        currentTime = datetime.datetime.utcnow()
        if(Test['testCaseType'] == "PING_TO_SERVER_WAN"):
            debugFile = open('UT' + self.num + '_' + Test['testCaseType']+ '_' + currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+ "_UT.txt","w+")
            self.debugFiles.append(debugFile)
            if(self.system == "CNX"):
                UTPingTimeStamp=" |cmd /q /v /c \"(pause&pause)>nul &for /l %a in () do (for /f \"delims=*\" %a in (\'powershell get-date -format \"{ddd dd-MMM-yyyy HH:mm:ss}\"\') do (set datax=%a) && set /p \"data=\" && echo([!datax!] - !data!)&ping -n 2 localhost>nul\""
                return self.addThread(self.cnxClient, "ping " + Test['testCaseParameters_CNX'] + " " + self.test_server_wan + UTPingTimeStamp, debugFile)
            else:
                return self.addThread(self.ssmClient, "ping " + Test['testCaseParameters'] + " " + self.test_server_wan + " -O | while read pong; do echo \"$(date): $pong\"; done", debugFile)
        elif(Test['testCaseType'] == "PING_TO_INTERNET"):
            debugFile = open('UT' + self.num + '_' + Test['testCaseType']+ '_' + currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+ "_UT.txt","w+")
            self.debugFiles.append(debugFile)
            if(self.system == "CNX"):
                UTPingTimeStamp=" |cmd /q /v /c \"(pause&pause)>nul &for /l %a in () do (for /f \"delims=*\" %a in (\'powershell get-date -format \"{ddd dd-MMM-yyyy HH:mm:ss}\"\') do (set datax=%a) && set /p \"data=\" && echo([!datax!] - !data!)&ping -n 2 localhost>nul\""
                return self.addThread(self.cnxClient, "ping " + Test['testCaseParameters_CNX'] + " " + UTPingTimeStamp, debugFile)
            else:
                return self.addThread(self.ssmClient, "ping " + Test['testCaseParameters'] + " " + " -O | while read pong; do echo \"$(date): $pong\"; done", debugFile)
        elif(Test['testCaseType'] == "PING_TO_SERVER_MGMT"):
            debugFile = open('UT' + self.num + '_' + Test['testCaseType']+ '_' +currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+'_UT.txt',"w+")
            self.debugFiles.append(debugFile)
            return self.addThread(self.ssmClient, "ping " + Test['testCaseParameters'] + " " + self.test_server_mgt + " -I rmnet_data1 -O | while read pong; do echo \"$(date): $pong\"; done", debugFile)
        elif(Test['testCaseType'] == "PING_FROM_SERVER_WAN"):
            debugFile = open('UT' + self.num + '_' + Test['testCaseType']+ '_' +currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+'_TestServer.txt',"w+")
            self.debugFiles.append(debugFile)
            return self.addThread(self.testServerClient, "ping " + Test['testCaseParameters'] + " " + self.wan_ip_addr + " -O | while read pong; do echo \"$(date): $pong\"; done", debugFile)
        elif(Test['testCaseType'] == "PING_FROM_SERVER_MGMT"):
            debugFile = open('UT' + self.num + '_' + Test['testCaseType']+ '_' +currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+'_TestServer.txt',"w+")
            self.debugFiles.append(debugFile)
            return self.addThread(self.testServerClient, "ping " + Test['testCaseParameters'] + " " + self.mgt_ip_addr + " -O | while read pong; do echo \"$(date): $pong\"; done", debugFile)
        elif(Test['testCaseType'] == "DOWNLINK_IPERF_WAN"):
            debugFile = open('UT' + self.num + '_' + Test['testCaseType']+ '_' +currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+'_TestServer.txt',"w+")
            self.debugFiles.append(debugFile)
            debugFile_ut = open('UT' + self.num + '_' + Test['testCaseType']+ '_' +currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+'_UT.txt',"w+")
            self.debugFiles.append(debugFile_ut)
            testPort = str(int(self.iperf_port) + Test['offsetFromBasePort'])
            if (Test['testCaseParameters'].find('-u ') == -1):
                udpOption = ''
            else:
                udpOption = ' -u'
            if(self.system == "CNX"):
                if (udpOption != ''):
                    remoteExecCommand(self.ssmClient, "iptables -t nat -A PREROUTING -i rmnet_data0 -p udp --dport " + testPort + " -j DNAT --to-destination 10.101.1.5:" + testPort, debugFile_ut)
                else:
                    remoteExecCommand(self.ssmClient, "iptables -t nat -A PREROUTING -i rmnet_data0 -p tcp --dport " + testPort + " -j DNAT --to-destination 10.101.1.5:" + testPort, debugFile_ut)
                self.natPorts.append(testPort)
                self.addThread(self.cnxClient, self.config.cnx_iperf_cmd + " -s -p " + testPort + " -i 2 ", debugFile_ut)
                return self.addThread(self.testServerClient, self.config.test_server_iperf_cmd_for_cnx + " -c " + self.wan_ip_addr + " -p " + testPort  + " " + Test['testCaseParameters_CNX']  + " -B " + self.test_server_wan, debugFile)
            else:
                self.addThread(self.ssmClient, self.config.ssm_iperf_cmd + udpOption + " -s -p " + testPort + " -i 2 ", debugFile_ut)			
                time.sleep(2)
                return self.addThread(self.testServerClient, self.config.test_server_iperf_cmd_for_ssm + " -c " + self.wan_ip_addr + " -p " + testPort  + " " + Test['testCaseParameters']  + " -B " + self.test_server_wan, debugFile)
        elif(Test['testCaseType'] == "UPLINK_IPERF_WAN"):
            debugFile = open('UT' + self.num + '_' + Test['testCaseType']+ '_' +currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+'_TestServer.txt',"w+")
            self.debugFiles.append(debugFile)
            debugFile_ut = open('UT' + self.num + '_' + Test['testCaseType']+ '_' +currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+'_UT.txt',"w+")
            self.debugFiles.append(debugFile_ut)
            testPort = str(int(self.iperf_port) + Test['offsetFromBasePort'])
            if (Test['testCaseParameters'].find('-u ') == -1):
                udpOption = ''
            else:
                udpOption = ' -u'
            if (self.system == "CNX"):
                if (udpOption != ''):
                    remoteExecCommand(self.ssmClient, "iptables -t nat -A PREROUTING -i rmnet_data0 -p udp --dport " + testPort + " -j DNAT --to-destination 10.101.1.5:" + testPort, debugFile_ut)
                else:
                    remoteExecCommand(self.ssmClient, "iptables -t nat -A PREROUTING -i rmnet_data0 -p tcp --dport " + testPort + " -j DNAT --to-destination 10.101.1.5:" + testPort, debugFile_ut)
                self.natPorts.append(testPort)
                self.addThread(self.testServerClient, self.config.test_server_iperf_cmd_for_cnx + " -s -p " + testPort + " -i 2 ", debugFile)
                time.sleep(2)
                return self.addThread(self.cnxClient, self.config.cnx_iperf_cmd + " -c " + self.test_server_wan + " -p " + testPort  + " " + Test['testCaseParameters_CNX']  + " -B " + self.config.ut_cnx_ip, debugFile_ut)
            else:
                self.addThread(self.testServerClient, self.config.test_server_iperf_cmd_for_ssm + udpOption + " -s -p " + testPort + " -i 2 ", debugFile)
                return self.addThread(self.ssmClient, self.config.ssm_iperf_cmd + " -c " + self.test_server_wan + " -p " + testPort  + " " + Test['testCaseParameters']  + " -B " + self.wan_ip_addr, debugFile_ut)			
        elif(Test['testCaseType'] == "DOWNLINK_IPERF_MGMT"):
            debugFile = open('UT' + self.num + '_' + Test['testCaseType']+ '_' +currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+'_TestServer.txt',"w+")
            self.debugFiles.append(debugFile)
            debugFile_ut = open('UT' + self.num + '_' + Test['testCaseType']+ '_' +currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+'_UT.txt',"w+")
            self.debugFiles.append(debugFile_ut)
            testPort = str(int(self.iperf_port) + Test['offsetFromBasePort'])
            if (Test['testCaseParameters'].find('-u ') == -1):
                udpOption = ''
            else:
                udpOption = ' -u'
            self.addThread(self.ssmClient, self.config.ssm_iperf_cmd + udpOption + " -s -p " + testPort + " -i 2 ", debugFile_ut)
            time.sleep(2)
            return self.addThread(self.testServerClient, self.config.test_server_iperf_cmd_for_ssm + " -c " + self.mgt_ip_addr + " -p " + testPort  + " " + Test['testCaseParameters']  + " -B " + self.test_server_mgt, debugFile)
        elif(Test['testCaseType'] == "UPLINK_IPERF_MGMT"):
            debugFile = open('UT' + self.num + '_' + Test['testCaseType']+ '_' +currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+'_TestServer.txt',"w+")
            self.debugFiles.append(debugFile)
            debugFile_ut = open('UT' + self.num + '_' + Test['testCaseType']+ '_' +currentTime.strftime("%Y-%m-%d-%H%M%S.%f")+'_UT.txt',"w+")
            self.debugFiles.append(debugFile_ut)
            testPort = str(int(self.iperf_port) + Test['offsetFromBasePort'])
            if (Test['testCaseParameters'].find('-u ') == -1):
                udpOption = ''
            else:
                udpOption = ' -u '
            self.addThread(self.testServerClient, self.config.test_server_iperf_cmd_for_ssm + udpOption + " -s -p " + testPort + " -i 2 ", debugFile)
            time.sleep(2)
            return self.addThread(self.ssmClient, self.config.ssm_iperf_cmd + " -c " + self.test_server_mgt + " -p " + testPort  + " " + Test['testCaseParameters']  + " -B " + self.mgt_ip_addr, debugFile_ut)
        else:
            pass
        
    def endProg(self):
        self.endTest = True
        logText(self.debugFile1,f"{datetime.datetime.utcnow()}: KeyBoard Interrupt on UT:{self.num}\n")
        for t in self.threads:
            t.endThread = True    
        
    def runTests(self, TestFile):
        #loop through json file and figure out what threads to run 
        with open(TestFile, "r") as readTest_file:
            Tests = json.load(readTest_file)
            for Test_suite in Tests:
                if(Test_suite['testSuiteName'] == self.test_name):
                    for Test in Test_suite['testCases']:
                        if (self.endTest == False):
                            if(Test['testStartOption'] == "StartAfterPrevious"):
                                while(prev.is_alive()):
                                    prev.join(0.5)
                            if (self.endTest == False):
                                prev = self.addTest(Test)
        [t.join() for t in self.threads if t is not None and t.is_alive()]
        for testPort in self.natPorts:
            remoteExecCommand(self.ssmClient, "iptables -t nat -D PREROUTING -i rmnet_data0 -p tcp --dport " + testPort + " -j DNAT --to-destination 10.101.1.5:" + testPort, self.debugFile1)
            remoteExecCommand(self.ssmClient, "iptables -t nat -D PREROUTING -i rmnet_data0 -p udp --dport " + testPort + " -j DNAT --to-destination 10.101.1.5:" + testPort, self.debugFile1)		    
        for d in self.debugFiles:
            d.close()
        
    def setTestData(self, file_path):
        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if(row['UT Id'] == self.num):
                    print(f"row:{row}\n")
                    self.IP = row['UT IP Address']
                    self.username = row['Username']
                    self.password = row['Password']
                    self.test_server_wan = row['Test Server WAN IP Address']
                    self.test_server_mgt = row['Test Server Management IP Address']
                    self.iperf_port = row['IPerf Base Port']
                    self.test_name = row['Test SuiteName']
                    self.system = row['System']
                    print(self.test_name)
            print(f"self.config.proxy_server_ip_ut: {self.config.proxy_server_ip_ut}, self.config.proxy_server_login_ut: {self.config.proxy_server_login_ut}, self.config.proxy_server_pass_ut:{self.config.proxy_server_pass_ut},self.IP:{self.IP},self.username:{self.username},self.password:{self.password}\n")        
            self.ssmClient = getProxySSHClient(self.config.proxy_server_ip_ut, self.config.proxy_server_login_ut, self.config.proxy_server_pass_ut,self.IP,self.username,self.password,self.debugFile1)   
    
    def waitForUTAttach(self):
        #proxies = {
        #    "http": "socks5h://localhost:58082",
        #    "https": "socks5h://localhost:58082"
        #   }

        #GET_MODEM_STATUS_API = "https://10.101.1.10/api/modem/modemstatus"
        #GET_NETWORK_STATUS_API= "https://10.101.1.10/api/system/ifstats"
        attached = False
        wan_connection_status = ""
        mgt_connection_status = ""
        while not attached and not self.endTest:
            try:
                #with warnings.catch_warnings():
                #    warnings.simplefilter("ignore")
                #    api_response = requests.get(url=GET_MODEM_STATUS_API,proxies=proxies, verify=False)
                #decoded_json_data = api_response.json()
                #wan_connection_status = decoded_json_data['wan_connection_status']
                #mgt_connection_status = decoded_json_data['mgt_connection_status']
                #if (wan_connection_status == 'connected') and (mgt_connection_status == 'connected'):
                #    attached = True
                #    logText(self.debugFile1, "UT Attached\n")
                #    network_response = requests.get(url=GET_NETWORK_STATUS_API,proxies=proxies, verify=False)
                #    decoded_network_data = network_response.json()
                #    self.wan_ip_addr = decoded_network_data['IF_WAN']['ifAddr']
                #    self.mgt_ip_addr = decoded_network_data['IF_MGT']['ifAddr']
                #    logText(self.debugFile1, f"wan_ip_addr: {self.wan_ip_addr}, mgt_ip_Addr: {self.mgt_ip_addr}\n")
                #else:
                    self.wan_ip_addr, self.mgt_ip_addr = self.checkIPAddressAssignment()
                    if (self.wan_ip_addr != "") and (self.mgt_ip_addr != ""):
                        logText(self.debugFile1,f"{datetime.datetime.utcnow()}: UT {self.num} Attached, wan_ip_addr: {self.wan_ip_addr}, mgt_ip_Addr: {self.mgt_ip_addr}\n" )
                        attached = True
                    else :
                        logText(self.debugFile1,f"{datetime.datetime.utcnow()}: UT {self.num} not yet attached, WAN Status:{wan_connection_status}, Mgmt Status:{mgt_connection_status}\n")
                        time.sleep(2)
            except Exception as e:
                logText(self.debugFile1, "GET Modem Status API request Unsuccessful : " + str(e)+"\n")    
                
    def checkIPAddressAssignment(self):
        wan_ip_addr =""
        mgt_ip_addr =""
        #if (self.num =='1'):
        #    wan_ip_addr ="192.168.52.1"
        #    mgt_ip_addr ="192.168.12.1"
        #elif (self.num =='3'):
        #    wan_ip_addr ="192.168.52.3"
        #    mgt_ip_addr ="192.168.12.3"
        #else:
        #    wan_ip_addr ="192.168.52.4"
        #    mgt_ip_addr ="192.168.12.4"		
        #return wan_ip_addr, mgt_ip_addr
        mystdin,mystdout,mystderr = self.ssmClient.exec_command("ip addr |grep \"scope global rmnet_data\"")
        if (mystdout.channel.recv_exit_status() == 0):
            cmdOutput = ""
            for line in mystdout.readlines():
                ipString = line.split("inet ")[1]
                ipString = ipString.split("/")[0]
                net = line.strip().split(" ")[4]
                if (net == "rmnet_data0"):
                    wan_ip_addr = ipString
                else:
                    mgt_ip_addr = ipString
        mystdout.channel.close()								
        return wan_ip_addr, mgt_ip_addr
        
    
def getSSHClient(proxy_ip, proxy_login, proxy_pw):
    """
    Instantiate, setup and return a straight forward proxy SSH client
    :param proxy_ip:
    :param proxy_login:
    :param proxy_pw:
    :return:
    """
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(proxy_ip, 22, username=proxy_login, password=proxy_pw)
    return client

def getProxySSHClient(proxy_ip, proxy_login, proxy_pw, destination_ip, destination_login, destination_pw,debugFile):
    """
    Establish a SSH client through the proxy.
    :param proxy_ip:
    :param proxy_login:
    :param proxy_pw:
    :param destination_ip:
    :param destination_login:
    :param destination_pw:
    :return:
    """
    proxy = getSSHClient(proxy_ip, proxy_login, proxy_pw)
    transport = proxy.get_transport()
    dest_addr = (destination_ip, 22)
#    local_addr = ('127.0.0.1', 10022)
    local_addr = ('127.0.0.1', 58081)
    proxy_transport = transport.open_channel('direct-tcpip', dest_addr, local_addr)

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(destination_ip, 22, username=destination_login, password=destination_pw, sock=proxy_transport)
    logText(debugFile,f"{datetime.datetime.utcnow()} : Connected to {dest_addr} over SSH tunnel via {proxy_ip}\n") 
    return client
    
def logText(debugFile,output):
    debugFile.write(f"{output}")
    print(f"{output}",end="")
            
def logCmdOutput(stdStream,debugFile):
    while stdStream.channel.recv_ready():
        rl, wl, xl = select.select([stdStream.channel], [], [], 0.0)
        if len(rl) > 0:
            output = stdStream.channel.recv(len(rl)).decode('ascii')
            logText(debugFile,output)
            if '\n' in output:
                debugFile.flush()
                os.fsync(debugFile)

def logCmdError(stdStream,debugFile):
    while stdStream.channel.recv_stderr_ready():
        rl, wl, xl = select.select([stdStream.channel], [], [], 0.0)
        if len(rl) > 0:
            output = stdStream.channel.recv_stderr(len(rl)).decode('ascii')
            logText(debugFile,output)
            if '\n' in output:
                debugFile.flush()
                os.fsync(debugFile)
                    
def remoteExecCommand(myclient,command, debugFile):    
    t=threading.current_thread()
    logText(debugFile,f"{datetime.datetime.utcnow()}: Thread:{t.getName()} Started remote execution of {command}\n")
    t.endThread = False    
    mystdin,mystdout,mystderr = myclient.exec_command(command,get_pty=True)
    # Wait for the command to terminate
    while not mystdout.channel.exit_status_ready() and not t.endThread:
        # Only print data if there is data to read in the channel
        logCmdOutput(mystdout,debugFile)
        logCmdError(mystderr,debugFile)
    logCmdOutput(mystdout,debugFile)
    logCmdError(mystderr,debugFile)
    logText(debugFile,f"{datetime.datetime.utcnow()}: Thread:{t.getName()}, Exiting Remote command: {command}\n")
    if (mystdout.channel.exit_status_ready()):
        status = mystdout.channel.recv_exit_status()
        if status != 0:
            output = mystderr.read().decode('ascii')
            logText(debugFile,output)
            logText(debugFile,f"Remote command: {command} status: {status}\n")
    mystdout.channel.close()
	
def launchUT(UT_obj, filename):
    logText(UT_obj.debugFile1, f"{datetime.datetime.utcnow()}: Starting UT: {UT_obj.num}, Thread:{threading.current_thread().getName()}\n")
    UT_obj.waitForUTAttach()
    UT_obj.runTests(filename)
    logText(UT_obj.debugFile1,f"{datetime.datetime.utcnow()}: Exiting UT: {UT_obj.num}, Thread:{threading.current_thread().getName()}\n")
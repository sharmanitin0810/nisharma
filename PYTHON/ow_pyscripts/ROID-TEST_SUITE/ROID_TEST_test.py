#!/usr/bin/env python
##########################################################################################
# PURPOSE: This file is a collection of classes and methods which 
#          are a part of OW UT test automation framework  
#
# SOURCE CODE FILE: ROID_TEST.py
#
# REVISION HISTORY:
# DATE:           AUTHOR:         CHANGE:
# 12-03-19        Gautham Bharadwaj        Initial Version
#                                 
# Copyright 2019 Hughes Network Systems Inc
##########################################################################################
# Import the modules needed to run the script.
import sys, os
import requests
import datetime                        # need for getting current time in readable format
import time                            # need for getting current time in second format
import json
import logging
import configparser as ConfigParser
import re
import win32com.client as win32
from win32com.client import gencache
import winerror
import pythoncom
from win32com.client import constants
from win32com.client.dynamic import Dispatch
import subprocess as sp
import paramiko
import glob
from scp import SCPClient
import psutil
import check_nd_push_eph
import ssh_client


EPH_HOST_MACHINE = '10.31.128.22'
USERNAME = 'msat'
PASSWORD = 'oneweb123'
REMOTE_DIR = '/home/msat/GNOC_FILES/DYNAMIC/OUT/UT_EPH/'
LOCAL_DIR='C:\\Users\oneweb\\Documents\\UtEphemeris\\'
KEYFILEPATH = None
KEYFILETYPE = None

UT_REMOTE_DIR = '/home/root/'
UT_HOST_MACHINE = '192.168.100.1'
UT_PORT = 22
UT_USERNAME = 'root'
UT_PASSWORD = 'use4Tst!'

 
gencache.EnsureModule('{10101010-1962-4443-B554-28AB4645A17B}', 0, 1, 0)
gencache.EnsureModule('{21454A49-2D4B-4F4E-A401-0C2614B1266B}', 0, 1, 0)
gencache.EnsureModule('{73E70491-EED3-11D3-A096-00805F9B0C38}', 0, 1, 0)
gencache.EnsureModule('{F6F37A12-F62A-4603-8757-6266058CF48E}', 0, 1, 0)
gencache.EnsureModule('{73E704FA-EED3-11D3-A096-00805F9B0C38}', 0, 1, 0)
gencache.EnsureModule('{73E704AF-EED3-11D3-A096-00805F9B0C38}', 0, 1, 0)
gencache.EnsureModule('{9A67840B-D27F-45F9-823F-0E0CB5171ED3}', 0, 1, 0)

class OneWeb_UT_AutomationSuiteConfig:
    def __init__(self):

        #### Variables from configuration file
        self.number_of_ut = 0           # SSM Address

        self.qxdm_log_mask_filepath = ""    # Filepath for QXDM LOG mask
        self.fwk_test_logs_base_dir = "C:\\UT_LOGS\\"
        self.fwk_iperf_udp_base_port = 15600
        self.fwk_gn_log_server_ip = "10.1.0.13"
        self.fwk_test_mode = "STATIC"
        self.fwk_test_ephemeris_file_dir = "C:\\Python27\\TOD_LOCATION\\UtEphemeris\\"
        self.latest_ephemeris_filepath = ''
       

class UT_Config:
    def __init__(self):

        #### Variables from configuration file
        self.ut_ssm_ip_addr = ""                                         # SSM Address
        self.ut_wan_ftp_server_ip = ""                                   # FTP server to conduct ping / FTP sessions
        
        self.ClearUtApiIfStats()
        
        self.ClearUtApiModemStatus()

        self.ClearUtApiSystemModemReset()
        
        self.ClearUtApiSystemAIMReset()
		
        self.ClearUtApiModemConnectDiagnosticsBridge()
        
        self.ClearUtApiModemDisconnectDiagnosticsBridge()
        
        self.ClearUtApiModemSetOperatingModeOnline()
        
        self.ClearUtApiAntennaGetAntennaInfo()
        
        self.ClearUtApiSystemRebootSSM()
        
        self.ut_qpst_assigned_com_port = 0              # COM port assigned from QPST Automation server
        self.ut_framework_assigned_qxdm_application = 0
        self.ut_framework_assigned_qxdm_session = 0     # QXDM session Assigned by Framework
        self.ut_qxdm_logfile_path = "C:\\UT_LOGS\\"
        
        self.ut_uplink_traffic_test_iperf_port = 0 
        self.ut_downlink_traffic_test_iperf_port = 0 
        
        self.ut_aim_emulator_executable_filepath = ""
        self.ut_current_test_aim_emulator_proc_id = 0
        
        self.ut_current_test_tod_proc_status = 0
        
        self.ut_current_test_tod_proc_id = 0
        
        self.ut_tod_executable_filepath = ""
        
        self.ut_mgmt_downlink_iperf_udp_port = 15601
        self.ut_mgmt_uplink_iperf_udp_port = 15602
        
        self.ut_mgmt_downlink_iperf_udp_port = 15603
        self.ut_mgmt_uplink_iperf_udp_port = 15604
        
        
        
        self.ut_tag = ""                            # ut tag for logging purposes
        self.ut_current_test_case_name = ""         # Name of the test case being executed with this UT
        self.ut_logs_dir_name = ""         # Name of the test case being executed with this UT
        self.ut_current_test_start_timestamp = ""
        self.configuration_valid = False                         # Configuration Valid
        self.is_call_running = False                         # is call running
        self.current_call_logs_dir = ""
        
    def ClearUtApiSystemRebootSSM(self):
        self.ut_api_system_reboot_response_successful = True
        self.ut_api_system_reboot_status = "field_not_present"
        self.ut_api_system_reboot_status_message = "field_not_present"
        
        return 
        
    def ClearUtApiSystemModemReset(self):
        self.ut_api_system_mdm_reset_response_successful = False
        self.ut_api_system_mdm_reset_command = "mdm_reset"
        self.ut_api_system_mdm_reset_result = "field_not_present"
        self.ut_api_system_mdm_reset_error = "field_not_present"   
        return 
        
    def ClearUtApiSystemAIMReset(self):
        self.ut_api_system_aim_reset_response_successful = False
        self.ut_api_system_aim_reset_command = "aim_reset"
        self.ut_api_system_aim_reset_result = "field_not_present"
        self.ut_api_system_aim_reset_error = "field_not_present"
        return

    def ClearUtApiModemConnectDiagnosticsBridge(self):
        self.ut_api_modem_connect_diagnostics_bridge_response_successful = False
        self.ut_api_modem_connect_diagnostics_bridge_command = "qdart_bridge"
        self.ut_api_modem_connect_diagnostics_bridge_result = "field_not_present"
        self.ut_api_modem_connect_diagnostics_bridge_error = "field_not_present"
        return
    
    def ClearUtApiModemDisconnectDiagnosticsBridge(self):
        self.ut_api_modem_disconnect_diagnostics_bridge_response_successful = False
        self.ut_api_modem_disconnect_diagnostics_bridge_command = "qdart_bridge"
        self.ut_api_modem_disconnect_diagnostics_bridge_result = "field_not_present"
        self.ut_api_modem_disconnect_diagnostics_bridge_error = "field_not_present"
        return 
        
    def ClearUtApiModemSetOperatingModeOnline(self):
        self.ut_api_modem_set_operating_mode_online_response_successful = False
        self.ut_api_modem_set_operating_mode_online_command_result = "field_not_present"
        return 
        
    def ClearUtApiAntennaGetAntennaInfo(self):
        self.ut_api_antenna_get_antenna_info_response_successful = False
        self.ut_api_antenna_get_antenna_info_status = "field_not_present"
        
    def ClearUtApiModemStatus(self):
        self.ut_api_modemstatus_response_successful = False
        self.ut_api_modemstatus_diagnostic_bridge_up = False     # Status of SSM - MDM Diagnostic Bridge connection
        self.ut_api_modemstatus_qmi_client_connected = False     # Status of SSM - MDM QMI client Interface
        self.ut_api_modemstatus_operating_mode = "Offline"       # Modem Call Status
        self.ut_api_modemstatus_loc_injections = 0 
        self.ut_api_modemstatus_wan_connection_status = "disconnected"            # WAN connection status
        self.ut_api_modemstatus_mgt_connection_status = "disconnected"            # MGT connection status
        self.ut_api_modemstatus_operating_mode = "shutting_down"
        self.ut_api_modemstatus_service_available = False
        return 
        
        
    def ClearUtApiIfStats(self):
        self.ut_api_ifstats_response_successful = False
        self.ut_api_ifstats_wan_ipv4_addr = ""                        # WAN IPv4 assigned by the Core Network
        self.ut_api_ifstats_mgt_ipv4_addr = ""       # WAN IPv4 assigned by the Core Network
        self.ut_api_ifstats_wan_ipv4_addr_mask = ""
        self.ut_api_ifstats_mgt_ipv4_addr_mask = ""
        self.ut_api_ifstats_wan_if_status = ""
        self.ut_api_ifstats_mgt_if_status = ""
        self.ut_api_ifstats_wan_ipv6_addr = ""       # WAN IPv6 assigned by the Core Network
        self.ut_api_ifstats_mgt_ipv6_addr = ""       # WAN IPv6 assigned by the Core Network
        return
        
class OW_UT_Automation_Framework:

    def get_ssh_client(self, host, uname, password):
        port = 22
        ssh_client = paramiko.SSHClient()
        ssh_client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, port, uname, password)
        return ssh_client

    def __init__(self):


        # =======================
        #    MENUS DEFINITIONS
        # =======================
 
        # Menu definition
        self.menu_actions = {
            'main_menu': self.main_menu,
			'0': self.exit,
            '1': self.start_call,
            '2': self.stop_call,
            '3': self.start_wan_downlink_iperf_session,
            '4': self.start_wan_uplink_iperf_session,
            '5': self.start_wan_uplink_downlink_iperf_session,
            '6': self.load_latest_ephemeris_files,
            '7': self.collect_ut_logs,
            '8': self.get_interface_status,
            '9': self.start_qpst_server,
            '10': self.stop_qpst_server,
        }
        
        #Empty list of UT IP address which will be used as Key to 
        #UT config Objects dictionary
        self.connectedUtList = []
        # Tracks List of QXDM automation Windows opened by Framework to close at the exit
        self.associated_qxdm_sessions_list = []     
        self.qpst_automation_server_app_handle = 0 
        self.utConfigObjectsDict = dict()
        self.is_qpst_server_running = False
        self.ut_with_active_call_dict = dict()
        self.procname = 'AIM_Emulator.py'
        self.final_proc = ''
        return

    def ParseForAutomationSuiteConfig(self,UtAutomationSuiteConfig):
        parser = ConfigParser.RawConfigParser()
        parser.read("ROID_TEST_SUITE.cfg")
        #parse automation_suite_config
        UtAutomationSuiteConfig.number_of_ut = parser.getint('automation_suite_config',"NUM_UT_CONNECTED")
        UtAutomationSuiteConfig.qxdm_log_mask_filepath = parser.get('automation_suite_config',"QXDM_LOG_MASK_FILEPATH")
        UtAutomationSuiteConfig.fwk_test_logs_base_dir = parser.get('automation_suite_config',"TEST_LOGS_BASE_DIR")
        UtAutomationSuiteConfig.fwk_iperf_udp_base_port = parser.getint('automation_suite_config',"IPERF_UDP_BASE_PORT")
        UtAutomationSuiteConfig.fwk_test_mode = parser.get('automation_suite_config',"TEST_MODE")
        UtAutomationSuiteConfig.fwk_test_ephemeris_file_dir = parser.get('automation_suite_config',"TEST_EPHEMERIS_FILE_DIR")
        UtAutomationSuiteConfig.fwk_wan_ftp_server_ssh_ip = parser.get('automation_suite_config',"WAN_FTP_SERVER_SSH_IP")
        UtAutomationSuiteConfig.fwk_mgt_ftp_server_ssh_ip = parser.get('automation_suite_config',"MGT_FTP_SERVER_SSH_IP")
        return
           
    def ProcessAutomationSuiteConfig(self,UtAutomationSuiteConfig):
        #Validate whether Configured IPs are reachable
        #validate whether files and folders are present
        
    
    
        return
        
    def ParseForUtConfig(self,UtConfig,ut_config_section):
        parser = ConfigParser.RawConfigParser()
        parser.read("ROID_TEST_SUITE.cfg")
        UtConfig.ut_ssm_ip_addr = parser.get(ut_config_section,"UT_SSM_IP_ADDR")
        if((parser.get(ut_config_section,"UT_TAG")) == ""):
            UtConfig.ut_tag = ut_config_section
        else:
            UtConfig.ut_tag = parser.get(ut_config_section,"UT_TAG")
        
        UtConfig.ut_current_test_case_name = parser.get(ut_config_section,"UT_CURRENT_TEST_CASE_NAME")
        UtConfig.ut_logs_dir_name = parser.get(ut_config_section,"UT_LOGS_DIR_NAME")
        UtConfig.ut_aim_emulator_executable_filepath = parser.get(ut_config_section,"UT_AIM_EMULATOR_EXECUTABLE_FILEPATH")
        UtConfig.ut_tod_executable_filepath = parser.get(ut_config_section,"UT_NMEA_GENERATOR_EXECUTABLE_FILEPATH")
        UtConfig.ut_ssm_uname = parser.get(ut_config_section,"UT_SSM_UNAME")
        UtConfig.ut_ssm_password = parser.get(ut_config_section,"UT_SSM_PASSWD")
        UtConfig.configuration_valid = True
        
        return

    # =======================
    #     MENUS FUNCTIONS
    # =======================
     
    # Main menu
    def main_menu(self):
    
        logging.info('Main Menu')
        
        user_input = ''
        action = ''
        print(self.connectedUtList)
        for i in range(0,len(self.connectedUtList)) :
            tempUtObject = self.utConfigObjectsDict.get(self.connectedUtList[i],UT_Config())
            if (tempUtObject.configuration_valid == True):
                print("Connected UT is : "+ tempUtObject.ut_ssm_ip_addr + " ID : " + str(i+1))
                   
        print ("Choose Test Action")
        print ("0. EXIT TEST SUITE")
        print ("1. START_CALL")
        print ("2. STOP_CALL")
        print ("3. START WAN DOWNLINK IPERF SESSION")
        print ("4. START WAN UPLINK IPERF SESSION")
        print ("5. START WAN UPLINK/DOWNLINK IPERF SESSION")
        print ("6. LOAD LATEST EPHEMERIS")
        print ("7. COLLECT UT LOGS")
        print ("8. GET INTERFACE STATUS")
        print ("9. START QPST SERVER")
        print ("10. STOP QPST SERVER")
        
        try:
            user_input=input("Test Action>>")
        except SyntaxError:
            print("\nNo valid user input received\n")
        
        if(user_input != ''):
            parsed_input = user_input.split()
            if(len(parsed_input) != 0):
                action = parsed_input[0].strip()

        self.exec_menu(action)
     
        return
     
    # Execute menu
    def exec_menu(self,choice):
   
        ch = choice.lower()
        if ch == '':
            print ("\nNo Option Selected.\n")
            #self.menu_actions['main_menu']()
        else:
            try:
                self.menu_actions[ch]()
            except KeyError:
                print ("\nInvalid selection, please try again.\n")
                #self.menu_actions['main_menu']()
        return
        
    def check_aim_emulator(self):
    
        try :
            print("Going to check for AIM_Emulator script is Running or not ..")
            os.system('tasklist >tasks.txt')
            with open ('tasks.txt','r') as procfile:
                for line in procfile:
                    if line.startswith('python.exe'):
                        if line.split()[1] != str(os.getpid()):
                            print("AIM_Emulator is already running, Process Clean up required ..")
                            os.system(f'TASKKILL /F /PID {line.split()[1]}')
                        break
            os.remove('tasks.txt')
            print("AIM_Emulator is not running now , going to start it ..!!" )    
            os.chdir('C:\Python27\\3.2_Scripts\OW_AIME_3.0.4_modified\AIMEmulator_ROID_1\PSC')
            self.final_proc = sp.Popen(['C:\Python27\python.exe', 'C:\Python27\\3.2_Scripts\OW_AIME_3.0.4_modified\AIMEmulator_ROID_1\PSC\AIM_Emulator.py'])
            #final_proc = sp.Popen(['C:\Windows\System32\cmd.exe''C:\Python27\python.exe', 'C:\Python27\3.2_Scripts\OW_AIME_3.0.4_modified\AIMEmulator_ROID_1\PSC\AIM_Emulator.py'])
            print("AIM Emulator is Started successfully")
            return
        
        except Exception as e:
            print ("Exception Occured :",e)
            os.system('exit')
            
    def stop_aim_new(self):
        print("Stop AIM emulator new")
        if self.final_proc != 0:
            try:
                print("close already running AIM script :",self.final_proc)
                sp.Popen.terminate(self.final_proc)
                
            except Exception as e:
                print("Except:",str(e))
                
        
    def get_push_load_eph(self):
        print("Entering get_push_load eph func")
        self.get_latest_ephemeris_info()
        ssh_connection = self.get_ssh_client("192.168.100.1", "root" , "use4Tst!")        
        ssh_connection.exec_command('rm -f /home/root/default_ephemeris*')
        target_file_path = "/home/root/" + os.path.basename(UtAutomationSuiteConfig.latest_ephemeris_filepath)
        scp = SCPClient(ssh_connection.get_transport())
        scp.put(UtAutomationSuiteConfig.latest_ephemeris_filepath, target_file_path)
        time.sleep(2)
        print("Going to copy latest file to UT")
        
        stdin, stdout, stderr = ssh_connection.exec_command('adb shell rm /etc/sha1chksum;                   \
                                            mv /home/root/default_ephemeris_*.csv /home/root/default_ephemeris.csv; \
                                            adb push /home/root/default_ephemeris.csv /etc/;         \
                                            adb shell tail -n 1 /etc/default_ephemeris.csv; \
                                            adb shell sync')
        
        for line in stdout:
            print (line.strip('\n'))
        print("Successfully pushed the latest eph to UT")
        ssh_connection.close()
        
    def check_eph_ems(self):
        print("Going to check latest UT eph file on EMS")
        ems_login = check_nd_push_eph.ChkEphEmsUT(EPH_HOST_MACHINE,22,USERNAME,PASSWORD,REMOTE_DIR,LOCAL_DIR)
        ems_hash = ems_login.EmsFileCheck()
        print("The latest EMS file sha512sum is :",ems_hash)
        if ems_hash == '1':
            print("No new file detected on EMS , nothing to do")
            return
        
        else:
            print("BUG : Entering else loop - Need to check (WIP)")
            print("Going to check ephemeris file on UT")
            ssh_obj = ssh_client.SSHClient("192.168.100.1","root","use4Tst!")
            output = ssh_obj.executeCommand("sha512sum /home/root/default_ephemeris.csv | awk {'print $1'}")
            #print (output)
            shasum = output[1]
            shasum[-1]= shasum[-1].strip()
            #print ("Final Shasum is :",shasum)
            ut_hash = shasum[0]
            print("On UT sha512sum of eph.file is  :" , ut_hash)
            print("UT and EMS are having diffrent EPH file")
            print("Going to push the latest eph file")
            self.get_push_load_eph()
        
    def start_call(self):
        print("Going to perform eph. file ..")
        self.check_eph_ems()
        #Verifying AIM script 
        self.check_aim_emulator()
        time.sleep(3)
        self.start_qpst_server()  
        print ("Enter UT Id s to start call on : <1,4> or <all>")
        ut_list = self.get_ut_list()
        print(ut_list) 
        currentDT = datetime.datetime.now()
        call_start_timestamp = currentDT.strftime("%Y_%m_%d_%H_%M_%S")
        for UtSsmIp , UtConfigObject in self.utConfigObjectsDict.items():
            if(UtSsmIp in ut_list):
                if (UtSsmIp in self.ut_with_active_call_dict):
                    print ("Call already in progress for UT " + UtSsmIp + " Skipping !!")
                    continue
                else:
                    UtConfigObject.ut_current_test_start_timestamp = call_start_timestamp
                    self.start_test(UtConfigObject) 
                    self.ut_with_active_call_dict[UtSsmIp] = UtConfigObject.ut_framework_assigned_qxdm_session
                
        return
        
    def start_wan_uplink_iperf_session(self):
        print("\nNot Implemented\n")
    
        return
        
    def start_wan_downlink_iperf_session(self):
        print("\nNot Implemented\n")
    
        return

    def start_wan_uplink_downlink_iperf_session(self):
        print("\nNot Implemented\n")
    
        return

    '''
    Loop through list of UT s and obtain interface details 
    via HTTP API    
    '''
    def get_interface_status(self):
        print ("Enter UT Id s to retrieve interface status from : <1,4> or <all>")
        ut_list = self.get_ut_list()
        print(ut_list)   
        for UtSsmIp , UtConfigObject in self.utConfigObjectsDict.items():
            if(UtSsmIp in ut_list):
                self.get_if_status(UtConfigObject)
                self.print_if_status(UtConfigObject)
      
        return
        
    def start_qpst_server(self):
        if(self.is_qpst_server_running == False):
            self.start_qpst_automation_server()
            self.remove_all_existing_ut_connections()
        else :
            print("QPST Server is already running.")
        return
        
    def stop_qpst_server(self):
        if(self.is_qpst_server_running):
            self.remove_all_existing_ut_connections()
            try:
                self.qpst_automation_server_app_handle.Quit()
            except Exception as e:
                print("QPST server Instance is not present " + str(e))
            self.is_qpst_server_running = False
            self.qpst_automation_server_app_handle = 0
        else:
            print("QPST Server is not running")
        return
        
    def load_latest_ephemeris_files(self):
        print ("Enter UT Id s to Load Ephemeris to <1,4> or <all>")
        ut_list = self.get_ut_list()
        print(ut_list)
        self.get_latest_ephemeris_info()

        for UtSsmIp , UtConfigObject in self.utConfigObjectsDict.items():
            if(UtSsmIp in ut_list):
                ssh_connection = self.get_ssh_client(UtConfigObject.ut_ssm_ip_addr, UtConfigObject.ut_ssm_uname , UtConfigObject.ut_ssm_password)
                self.push_ephemeris_file(ssh_connection, UtConfigObject)
                self.load_ephemeris_file(ssh_connection, UtConfigObject)  
                ssh_connection.close()
        

        return
        
    def collect_ut_logs(self):
        print ("Enter UT Id s to collect SSM/AIM/MDM Logs from <1,4> or <all>")
        ut_list = self.get_ut_list()
        print(ut_list)
                
        currentDT = datetime.datetime.now()
        
        for UtSsmIp , UtConfigObject in self.utConfigObjectsDict.items():
            if(UtSsmIp in ut_list):
                ssh_connection = self.get_ssh_client(UtConfigObject.ut_ssm_ip_addr, UtConfigObject.ut_ssm_uname , UtConfigObject.ut_ssm_password)
                target_dir_for_logs = UtAutomationSuiteConfig.fwk_test_logs_base_dir + '\\' + UtConfigObject.ut_logs_dir_name
                if(UtConfigObject.current_call_logs_dir != ''):
                    target_dir_for_logs = UtAutomationSuiteConfig.fwk_test_logs_base_dir + '\\' + UtConfigObject.ut_logs_dir_name + '\\' + UtConfigObject.current_call_logs_dir
                
                self.collect_ssm_logs(ssh_connection, currentDT, target_dir_for_logs,UtConfigObject.ut_tag)
                self.collect_aim_logs(ssh_connection, currentDT, target_dir_for_logs,UtConfigObject.ut_tag)
                self.collect_mdm_logs(ssh_connection, currentDT, target_dir_for_logs,UtConfigObject.ut_tag)
                ssh_connection.close()
        
        return        
        
    def stop_call(self):
        self.stop_aim_new()
        print ("Enter UT Id s to stop call on <1,4> or <all>")
        ut_list = self.get_ut_list()
        print(ut_list)
        i=0
        last_active_qxdm_session = False
        for UtSsmIp , UtConfigObject in self.utConfigObjectsDict.items():
            if(UtSsmIp in ut_list):
                if(len(self.ut_with_active_call_dict) == 1):
                    last_active_qxdm_session = True
                    print("last active QXDM Session")
                if(UtSsmIp in self.ut_with_active_call_dict.keys()):
                    self.disconnect_ut_from_qxdm(UtConfigObject, last_active_qxdm_session)
                    self.reset_aim(UtConfigObject)
                    self.reset_mdm(UtConfigObject)
                    del self.ut_with_active_call_dict[UtSsmIp]
                else :
                    print ("Call not in progress for UT " + UtSsmIp + " Skipping !! " )
                    continue
                #self.stop_tod_script(UtConfigObject)
                #self.stop_aim_emulator(UtConfigObject)
                

        return
        
        

    def get_latest_ephemeris_info(self):
        path_to_filetype = UtAutomationSuiteConfig.fwk_test_ephemeris_file_dir + "\\*.csv"
        list_of_files = glob.glob(path_to_filetype) 
        UtAutomationSuiteConfig.latest_ephemeris_filepath  = max(list_of_files, key=os.path.getctime)
        print("Fetch latest ephemeris file @ " + UtAutomationSuiteConfig.latest_ephemeris_filepath)
    
    
        return

    def collect_aim_logs(self, ut_ssh_conn, log_collection_time,target_dir_for_aim_logs, ut_tag):
        
        self.exec_remote_command(ut_ssh_conn,'rm -rf /home/root/aim_logs')
        self.exec_remote_command(ut_ssh_conn,'mkdir /home/root/aim_logs')
        self.exec_remote_command(ut_ssh_conn,'scp -o "ConnectTimeout 3" -o "StrictHostKeyChecking no" -o "UserKnownHostsFile /dev/null" 192.168.100.254:/var/log/rcmb_log /home/root/aim_logs/rcmb_log')
        self.exec_remote_command(ut_ssh_conn,'scp -o "ConnectTimeout 3" -o "StrictHostKeyChecking no" -o "UserKnownHostsFile /dev/null" 192.168.100.254:/var/log/rcmb_log.1 /home/root/aim_logs/rcmb_log.1')
        self.exec_remote_command(ut_ssh_conn,'scp -o "ConnectTimeout 3" -o "StrictHostKeyChecking no" -o "UserKnownHostsFile /dev/null" 192.168.100.254:/var/log/aim_manager_log /home/root/aim_logs/aim_manager_log')
        self.exec_remote_command(ut_ssh_conn,'scp -o "ConnectTimeout 3" -o "StrictHostKeyChecking no" -o "UserKnownHostsFile /dev/null" 192.168.100.254:/var/log/aim_manager_log.1 /home/root/aim_logs/aim_manager_log.1')
  
        ut_current_log_collection_timestamp = log_collection_time.strftime("%Y_%m_%d_%H_%M_%S")
        aim_logs_zip_filename = ut_tag + '_' + str(ut_current_log_collection_timestamp) + '_AIM_LOGS.tar.gz'
        
        aim_logs_zip_command = 'tar -cvzf ' + aim_logs_zip_filename + ' aim_logs'
        self.exec_remote_command(ut_ssh_conn,aim_logs_zip_command)
        
        current_path = os.getcwd()
        os.chdir(target_dir_for_aim_logs)

        scp = SCPClient(ut_ssh_conn.get_transport())
        scp.get(aim_logs_zip_filename)
        
        os.chdir(current_path)
        aim_logs_zip_file_delete_command = 'rm -rf /home/root/' + aim_logs_zip_filename
        self.exec_remote_command(ut_ssh_conn,'rm -rf /home/root/aim_logs')
        self.exec_remote_command(ut_ssh_conn,aim_logs_zip_file_delete_command)
        
        return
        
    def collect_mdm_logs(self, ut_ssh_conn, log_collection_time,target_dir_for_mdm_logs, ut_tag):
        
        self.exec_remote_command(ut_ssh_conn,'rm -rf /home/root/mdm_a7_logs')
        self.exec_remote_command(ut_ssh_conn,'mkdir /home/root/mdm_a7_logs')
        self.exec_remote_command(ut_ssh_conn,'adb pull /data/oneweb/oneweb_service.log.bk /home/root/mdm_a7_logs/oneweb_service.log.bk')
        self.exec_remote_command(ut_ssh_conn,'adb pull /data/oneweb/oneweb_service.log /home/root/mdm_a7_logs/oneweb_service.log')
        self.exec_remote_command(ut_ssh_conn,'adb pull /data/oneweb/ow_start_stop.log /home/root/mdm_a7_logs/ow_start_stop.log')
        self.exec_remote_command(ut_ssh_conn,'adb pull /data/oneweb/ow_start_stop.log.bk /home/root/mdm_a7_logs/ow_start_stop.log.bk')     
  
        ut_current_log_collection_timestamp = log_collection_time.strftime("%Y_%m_%d_%H_%M_%S")
        mdm_logs_zip_filename = ut_tag + '_' + str(ut_current_log_collection_timestamp) + '_MDM_A7_LOGS.tar.gz'
        
        mdm_logs_zip_command = 'tar -cvzf ' + mdm_logs_zip_filename + ' mdm_a7_logs'
        self.exec_remote_command(ut_ssh_conn,mdm_logs_zip_command)
        
        current_path = os.getcwd()
        os.chdir(target_dir_for_mdm_logs)

        scp = SCPClient(ut_ssh_conn.get_transport())
        scp.get(mdm_logs_zip_filename)
        
        os.chdir(current_path)
        mdm_logs_zip_file_delete_command = 'rm -rf /home/root/' + mdm_logs_zip_filename
        self.exec_remote_command(ut_ssh_conn,'rm -rf /home/root/mdm_a7_logs')
        self.exec_remote_command(ut_ssh_conn,mdm_logs_zip_file_delete_command)
        
        return        
        
    def collect_ssm_logs(self, ut_ssh_conn, log_collection_time,target_dir_for_ssm_logs, ut_tag):
        
        self.exec_remote_command(ut_ssh_conn,'rm -rf /home/root/ssm_logs')
        self.exec_remote_command(ut_ssh_conn,'mkdir /home/root/ssm_logs')
        
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/fm.log /home/root/ssm_logs/fm.log')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/mm_starter.log /home/root/ssm_logs/mm_starter.log')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/mm_owext.log /home/root/ssm_logs/mm_owext.log')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/mm_timeinj.log /home/root/ssm_logs/mm_timeinj.log')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/mm_callmgr.log /home/root/ssm_logs/mm_callmgr.log')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/mm_timemon.log /home/root/ssm_logs/mm_timemon.log')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/gnss.log /home/root/ssm_logs/gnss.log')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/amc.log /home/root/ssm_logs/amc.log')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/amc.log /home/root/ssm_logs/sysmon.log')

        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/fm.log.1 /home/root/ssm_logs/fm.log.1')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/mm_starter.log.1 /home/root/ssm_logs/mm_starter.log.1')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/mm_owext.log.1 /home/root/ssm_logs/mm_owext.log.1')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/mm_timeinj.log.1 /home/root/ssm_logs/mm_timeinj.log.1')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/mm_callmgr.log.1 /home/root/ssm_logs/mm_callmgr.log.1')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/mm_timemon.log.1 /home/root/ssm_logs/mm_timemon.log.1')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/gnss.log.1 /home/root/ssm_logs/gnss.log.1')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/amc.log.1 /home/root/ssm_logs/amc.log.1')
        self.exec_remote_command(ut_ssh_conn,'cp -f /var/log/amc.log /home/root/ssm_logs/sysmon.log.1')
        
        self.exec_remote_command(ut_ssh_conn,'cp -f /misc/stats.sqlite3 /home/root/ssm_logs/stats.sqlite3')
  
        ut_current_log_collection_timestamp = log_collection_time.strftime("%Y_%m_%d_%H_%M_%S")
        ssm_logs_zip_filename = ut_tag + '_' + str(ut_current_log_collection_timestamp) + '_SSM_LOGS.tar.gz'
        
        ssm_logs_zip_command = 'tar -cvzf ' + ssm_logs_zip_filename + ' ssm_logs'
        self.exec_remote_command(ut_ssh_conn,ssm_logs_zip_command)
        
        current_path = os.getcwd()
        os.chdir(target_dir_for_ssm_logs)

        scp = SCPClient(ut_ssh_conn.get_transport())
        scp.get(ssm_logs_zip_filename)
        
        os.chdir(current_path)
        ssm_logs_zip_file_delete_command = 'rm -rf /home/root/' + ssm_logs_zip_filename
        self.exec_remote_command(ut_ssh_conn,'rm -rf /home/root/ssm_logs')
        self.exec_remote_command(ut_ssh_conn,ssm_logs_zip_file_delete_command)
        
        return        
        
    def exec_remote_command(self, ut_ssh_conn, remote_command):
        try:
            stdin, stdout, stderr = ut_ssh_conn.exec_command(remote_command)
            for line in stdout:
                print (line.strip('\n'))
        except Exception as e:
            print("Exception ! Unable to execute remote command : " + str(e))
            
        return
        
    def push_ephemeris_file(self, ssh_conn, UtConfigObject):
        
        self.exec_remote_command(ssh_conn,'rm -f /home/root/default_ephemeris*')
        
        target_file_path = "/home/root/" + os.path.basename(UtAutomationSuiteConfig.latest_ephemeris_filepath)

        scp = SCPClient(ssh_conn.get_transport())
        scp.put(UtAutomationSuiteConfig.latest_ephemeris_filepath, target_file_path)

        return
        
    def load_ephemeris_file(self,ssh_conn,UtConfigObject):
        
        stdin, stdout, stderr = ssh_conn.exec_command('adb shell rm /etc/sha1chksum;                   \
                                            mv /home/root/default_ephemeris_*.csv /home/root/default_ephemeris.csv; \
                                            adb push /home/root/default_ephemeris.csv /etc/;         \
                                            adb shell tail -n 1 /etc/default_ephemeris.csv; \
                                            adb shell sync')
        
        for line in stdout:
            print (line.strip('\n'))
        
        return 
    
    # Start_Test      
    def start_test(self,UtConfigObject):
        
        UtConfigObject.current_call_logs_dir = UtConfigObject.ut_tag + '_' + UtConfigObject.ut_current_test_start_timestamp + '_' + UtConfigObject.ut_current_test_case_name
        current_logs_dir_path = UtAutomationSuiteConfig.fwk_test_logs_base_dir + '\\' +  UtConfigObject.ut_logs_dir_name + '\\' +  UtConfigObject.current_call_logs_dir + '\\'
        if(os.path.exists(current_logs_dir_path) == False):
            os.mkdir(current_logs_dir_path)
            print("Created directory for test logs" + current_logs_dir_path)
        UtConfigObject.ut_qxdm_logfile_path = current_logs_dir_path
        self.get_modem_status(UtConfigObject)
        if (UtConfigObject.ut_api_modemstatus_qmi_client_connected == True) :
            print("modem qmi client connected")
        
        if (UtConfigObject.ut_api_modemstatus_diagnostic_bridge_up == False) :
            print("modem diagnostic bridge not up .. Enabling")
            self.connect_diagnostics_bridge(UtConfigObject)
            if(UtConfigObject.ut_api_modem_connect_diagnostics_bridge_result == 'n/a'):
                print('Diagnostics bridge connection successful')
            
        self.get_modem_status(UtConfigObject)
        if (UtConfigObject.ut_api_modemstatus_diagnostic_bridge_up == True) :
            print("Diagnostics Bridge Connected , Connecting to QPST....")
            self.connect_ut_to_qpst(UtConfigObject)
            
        if (UtConfigObject.ut_qpst_assigned_com_port != 0):
            print("COM Port Successfully Assigned , Connecting QXDM")
            self.connect_ut_to_qxdm(UtConfigObject)
        
        self.start_qxdm_log_collection(UtConfigObject)
        #time.sleep(1)
        #self.start_tod_script(UtConfigObject)
        
        time.sleep(5)
        #print("Going to start the aim")
        #self.start_aim_emulator(UtConfigObject)
        time.sleep(5)
        
        self.set_modem_operating_mode_online(UtConfigObject)

        return
    
    def start_emulators(self):
        
        for UtSsmIp , UtConfigObject in self.utConfigObjectsDict.items():
            self.start_aim_emulator(UtConfigObject)
            

        return 
     
    def stop_emulators(self):
        
        for UtSsmIp , UtConfigObject in self.utConfigObjectsDict.items():
            self.stop_aim_emulator(UtConfigObject)
            
        
        return 
 
    def stop_aim_emulator(self,UtConfigObject) :
        logging.debug("Stopping AIM Emulator for SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        if(UtConfigObject.ut_current_test_aim_emulator_proc_id !=0):
            try:
                print("Close Already running AIM-E Process")
                sp.Popen.terminate(UtConfigObject.ut_current_test_aim_emulator_proc_id) 
            
            except Exception as e:
                print("Exception ! Unable to stop AIM-E Process: " + str(e))    
                     
        return        
 
    def start_aim_emulator(self,UtConfigObject) :
        logging.debug("Starting AIM Emulator for SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        if(UtConfigObject.ut_current_test_aim_emulator_proc_id !=0):
            try:
                print("Close Already running AIM-E Process")
                sp.Popen.terminate(UtConfigObject.ut_current_test_aim_emulator_proc_id) 
            
            except Exception as e:
                print("Exception ! Unable to stop AIM-E Process: " + str(e))    
                     
        cwd = os.getcwd()
        
        try:
            dirpath = os.path.dirname(UtConfigObject.ut_aim_emulator_executable_filepath)
            os.chdir(dirpath)
            UtConfigObject.ut_current_test_aim_emulator_proc_id = sp.Popen(['python',UtConfigObject.ut_aim_emulator_executable_filepath])
            os.chdir(cwd)
        
        except Exception as e:
            print("Exception ! Unable to start AIM_Emulator process : " + str(e))
        
        UtConfigObject.ut_current_test_aim_emulator_proc_status  = sp.Popen.poll(UtConfigObject.ut_current_test_aim_emulator_proc_id)
         
        print ("AIM Emulator started with proc_id : " + str(UtConfigObject.ut_current_test_aim_emulator_proc_id) + " Status : " )
        
        #+ str(UtConfigObject.ut_current_test_aim_emulator_proc_status)
    
        return
        
    def start_tod_script(self,UtConfigObject) :
        logging.debug("Starting TOD script for SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        if(UtConfigObject.ut_current_test_tod_proc_id !=0):
            try:
                print("Close already running TOD Process")
                sp.Popen.terminate(UtConfigObject.ut_current_test_tod_proc_id) 
            
            except Exception as e:
                print("Exception ! TOD process not running: " + str(e))    
                     
        cwd = os.getcwd()
        
        try:
            dirpath = os.path.dirname(UtConfigObject.ut_tod_executable_filepath)
            os.chdir(dirpath)
            UtConfigObject.ut_current_test_tod_proc_id = sp.Popen(['python',UtConfigObject.ut_tod_executable_filepath])
        
        except Exception as e:
            print("Exception ! Unable to start TOD process : " + str(e))
        
        os.chdir(cwd)
        
        UtConfigObject.ut_current_test_tod_proc_status  = sp.Popen.poll(UtConfigObject.ut_current_test_tod_proc_id)
         
        print ("TOD Script started with proc_id : " + str(UtConfigObject.ut_current_test_tod_proc_id) + " Status : " )
        
        #+ str(UtConfigObject.ut_current_test_aim_emulator_proc_status)
    
        return

    def stop_tod_script(self,UtConfigObject) :
        logging.debug("Stopping TOD Script for SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        if(UtConfigObject.ut_current_test_tod_proc_id !=0):
            try:
                print("Close Already running TOD Process")
                sp.Popen.terminate(UtConfigObject.ut_current_test_tod_proc_id) 
            
            except Exception as e:
                print("Exception ! Unable to stop TOD Process: " + str(e))    
                     
        return 
        
    def reset_ssm(self,UtConfigObject ):  
        logging.debug("Rebooting SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        
        UtConfigObject.ClearUtApiSystemRebootSSM()
        try:

            SSM_REBOOT_API = "http://" + UtConfigObject.ut_ssm_ip_addr + "/api/system/reboot"
            api_response = requests.get(url=SSM_REBOOT_API)
            UtConfigObject.ut_api_system_reboot_response_successful = True
        
            decoded_json_data = api_response.json()
            logging.debug(decoded_json_data)
            UtConfigObject.ut_api_system_reboot_status = decoded_json_data.get('status','field_not_present')
            UtConfigObject.ut_api_system_reboot_status_message = decoded_json_data.get('status_message','field_not_present')
        
            logging.debug("status : %s , status_massage : %s" ,status ,message)        
        
        except Exception as e:
            print("API request Unsuccessful : " + str(e))
            
        return
     
    # reset_mdm
    def reset_mdm(self,UtConfigObject):
        logging.debug("Performing Modem reset on SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        UtConfigObject.ClearUtApiSystemModemReset()
        
        try:
            MODEM_RESET_API = "http://" + UtConfigObject.ut_ssm_ip_addr + "/api/system/mdm_reset/mrd"
            api_response = requests.get(url=MODEM_RESET_API)   
            UtConfigObject.ut_api_system_mdm_reset_response_successful = True
            
            decoded_json_data = api_response.json()
            logging.debug(decoded_json_data)
            UtConfigObject.ut_api_system_mdm_reset_command = decoded_json_data.get('command' , 'field_not_present')
            UtConfigObject.ut_api_system_mdm_reset_result = decoded_json_data.get('result','field_not_present')
            UtConfigObject.ut_api_system_mdm_reset_error = decoded_json_data.get('error','field_not_present')

        except Exception as e:
            print("API request Unsuccessful : " + str(e))
            
        return
		
    def reset_aim(self,UtConfigObject):
        logging.debug("Performing aim reset on SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        UtConfigObject.ClearUtApiSystemAIMReset()
        try: 
            AIM_RESET_API = "http://" + UtConfigObject.ut_ssm_ip_addr + "/api/system/aim_reset"
            api_response = requests.get(url=AIM_RESET_API) 
            UtConfigObject.ut_api_system_aim_reset_response_successful = True
            
            #Successful reset output {"command":"aim_reset","result":"n/a"}		
            decoded_json_data = api_response.json()
            logging.debug(decoded_json_data)
            UtConfigObject.ut_api_system_aim_reset_command = decoded_json_data.get('command' , 'field_not_present')
            UtConfigObject.ut_api_system_aim_reset_result = decoded_json_data.get('result','field_not_present')
            UtConfigObject.ut_api_system_aim_reset_error = decoded_json_data.get('error','field_not_present')

        except Exception as e:
            print("API request Unsuccessful : " + str(e))
            
        return		

    # connect_diagnostics_bridge
    def connect_diagnostics_bridge(self,UtConfigObject):
        logging.debug("Enabling Diagnostics Bridge on SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        
        UtConfigObject.ClearUtApiModemConnectDiagnosticsBridge()
        try:
            CONNECT_DIAGNOSTICS_BRIDGE_API = "http://" + UtConfigObject.ut_ssm_ip_addr + "/api/modem/qdart_bridge/1"
            api_response = requests.get(url=CONNECT_DIAGNOSTICS_BRIDGE_API)
            UtConfigObject.ut_api_modem_connect_diagnostics_bridge_response_successful = True
            
            decoded_json_data = api_response.json()
            logging.debug(decoded_json_data)
            UtConfigObject.ut_api_modem_connect_diagnostics_bridge_command = decoded_json_data.get('command','field_not_present')
            UtConfigObject.ut_api_modem_connect_diagnostics_bridge_result = decoded_json_data.get('result','field_not_present')
            UtConfigObject.ut_api_modem_connect_diagnostics_bridge_error = decoded_json_data.get('error','field_not_present')
            time.sleep(1)
            
        except Exception as e:
            print("API request Unsuccessful : " + str(e))
            
        return
        
    # disconnect_diagnostics_bridge
    def disconnect_diagnostics_bridge(self,UtConfigObject):
        logging.debug("Disconnecting Diagnostics Bridge on SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        
        UtConfigObject.ClearUtApiModemDisconnectDiagnosticsBridge()
        try:
   
            DISCONNECT_DIAGNOSTICS_BRIDGE_API = "http://" + UtConfigObject.ut_ssm_ip_addr + "/api/modem/qdart_bridge/0"
            api_response = requests.get(url=DISCONNECT_DIAGNOSTICS_BRIDGE_API)
            UtConfigObject.ut_api_modem_connect_diagnostics_bridge_response_successful = True
            
            decoded_json_data = api_response.json()
            logging.debug(decoded_json_data)
            UtConfigObject.ut_api_modem_disconnect_diagnostics_bridge_command = decoded_json_data.get('command','field_not_present')
            UtConfigObject.ut_api_modem_disconnect_diagnostics_bridge_result = decoded_json_data.get('result','field_not_present')
            UtConfigObject.ut_api_modem_disconnect_diagnostics_bridge_error = decoded_json_data.get('error','field_not_present')
        
            time.sleep(1)
        
        except Exception as e:
            print("API request Unsuccessful : " + str(e))
            
        return  

    # connect_qpst
    def start_qpst_automation_server(self):
        logging.debug("Start QPST Automation Server")
        # AppId for the Automation server.
        try :
            self.qpst_automation_server_app_handle = Dispatch('QPSTAtmnServer.Application')
            
            time.sleep(2)
            self.qpst_automation_server_app_handle._FlagAsMethod("StartOutgoingDiagConnection")
            self.qpst_automation_server_app_handle._FlagAsMethod("AddPort")
            self.qpst_automation_server_app_handle._FlagAsMethod("ConfigureIpConnections")
            self.qpst_automation_server_app_handle._FlagAsMethod("EnablePort")
            self.qpst_automation_server_app_handle._FlagAsMethod("GetCOMPortList")
            self.qpst_automation_server_app_handle._FlagAsMethod("GetPort")
            self.qpst_automation_server_app_handle._FlagAsMethod("GetPortList")
            self.qpst_automation_server_app_handle._FlagAsMethod("RemovePort")
          
            self.qpst_automation_server_app_handle.ShowWindow()
            self.is_qpst_server_running = True
            
        except Exception as e:
            print("Exception ! Unable to start QPST Automation Server : " + str(e))
            sys.exit(11)
        
        
        return 
        
    def remove_all_existing_ut_connections(self) : 
        qpst_automation_server_app_handle_is_valid = False
        if(self.qpst_automation_server_app_handle != 0):
            try:
                comPortList = self.qpst_automation_server_app_handle.GetCOMPortList()
                qpst_automation_server_app_handle_is_valid = True
            except Exception as e:
                print("Stored QPST App server handle is invalid Resetting. Start QPST server again!! \n" + str(e))
                    
        if(qpst_automation_server_app_handle_is_valid):    
            comPortListCount = comPortList.PortCount
            for i in range (0,comPortListCount) :
                time.sleep(2)
                pName = comPortList.PortName(i)
                pType = comPortList.PortType(i)
                pAssigned = comPortList.AssignedToQPST(i)
                pDescription = comPortList.DeviceDescription(i)
            
                pNumber = int((re.search("\d+",pName)).group())
                for UtSsmIp , UtConfigObject in self.utConfigObjectsDict.items():
                    if(UtConfigObject.ut_qpst_assigned_com_port == pNumber ):
                        logging.debug("Found COM port %d assigned to SSM %s in QPST server ... Removing" ,pNumber,UtConfigObject.ut_ssm_ip_addr )
                        break
                    
                if (pAssigned == 1 and pType == "Network") :
                    print("Found Connected Network Port : " + pName + " Removing...")
                    self.qpst_automation_server_app_handle.RemovePort(pName)		
                 
        else:
            print("QPST Server is not running. No UTs to Disconnect") 
            
        return
        
    def connect_ut_to_qpst(self,UtConfigObject) :
        logging.debug("Connecting Modem Diagnostics bridge to QPST on SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        assignedComPort = 0
        comPortList = self.qpst_automation_server_app_handle.GetCOMPortList()
        comPortListCount = comPortList.PortCount
        pDescriptionSubstring = (UtConfigObject.ut_ssm_ip_addr + "/2500")
        for i in range (0,comPortListCount) :
            pName = comPortList.PortName(i)
            pType = comPortList.PortType(i)
            pAssigned = comPortList.AssignedToQPST(i)
            pDescription = comPortList.DeviceDescription(i)
            # Remove UT if already Connected
            
            if (pAssigned == 1 and pType == "Network" and  pDescriptionSubstring in pDescription) :
                print("Found Pre-existing Configured Network Port : " + pName + "For UT : " + UtConfigObject.ut_ssm_ip_addr + " Removing...")
                logging.debug("Found Pre-existing Configured Network Port %s For UT : %s ... Removing" ,pName, UtConfigObject.ut_ssm_ip_addr)
                self.qpst_automation_server_app_handle.RemovePort(pName)
                UtConfigObject.ut_qpst_assigned_com_port = 0
                
        self.qpst_automation_server_app_handle.StartOutgoingDiagConnection(UtConfigObject.ut_ssm_ip_addr, 2500)
        
        # Find the COM port assigned to the UT
        comPortList = self.qpst_automation_server_app_handle.GetCOMPortList()
        comPortListCount = comPortList.PortCount
        for i in range (0,comPortListCount) :
            pName = comPortList.PortName(i)
            pType = comPortList.PortType(i)
            pAssigned = comPortList.AssignedToQPST(i)
            pDescription = comPortList.DeviceDescription(i)
            
            if (pAssigned == 1 and pType == "Network" and  pDescriptionSubstring in pDescription) :
                print("Assigned port : " + pName + " to UT : " + UtConfigObject.ut_ssm_ip_addr)
                assignedComPort = int((re.search("\d+",pName)).group())
                break 
            
        time.sleep(2)
        if (assignedComPort != 0) :
            UtConfigObject.ut_qpst_assigned_com_port = assignedComPort
            logging.debug("Assigned COM Port %d on QPST server to SSM with tag %s and IP  %s" ,UtConfigObject.ut_qpst_assigned_com_port, UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        else :
            UtConfigObject.ut_qpst_assigned_com_port = assignedComPort
            logging.debug("Failed to Assign COM port on QPST server to SSM with tag %s and IP  %s", UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        return 

    # set_modem_operating_mode_online
    def set_modem_operating_mode_online(self,UtConfigObject):
        logging.debug("Set modem operating mode online on SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        
        UtConfigObject.ClearUtApiModemSetOperatingModeOnline()
        try:
     
            BRING_MODEM_ONLINE_API = "http://" + UtConfigObject.ut_ssm_ip_addr + "/api/modem/set_operating_mode/online?bypass_fm=true"
            api_response = requests.get(url=BRING_MODEM_ONLINE_API)
            UtConfigObject.ut_api_modem_set_operating_mode_online_response_successful = True
        
            decoded_json_data = api_response.json()
            logging.debug(decoded_json_data)
            UtConfigObject.ut_api_modem_set_operating_mode_online_command_result = decoded_json_data.get('status','field_not_present')
            
            if (UtConfigObject.ut_api_modem_set_operating_mode_online_command_result == "ok"):
                logging.debug("Modem Online command successful")

            time.sleep(1)
            self.get_modem_status(UtConfigObject)
        
            if(UtConfigObject.ut_api_modemstatus_operating_mode == "online") :
                logging.debug("Modem Operating mode set to Online")
        
        except Exception as e:
            print("API request Unsuccessful : " + str(e))
            
        return    

    def get_modem_status(self,UtConfigObject):
        logging.debug("Get Modem status on SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        
        UtConfigObject.ClearUtApiModemStatus()
        try:

            GET_MODEM_STATUS_API = "http://" + UtConfigObject.ut_ssm_ip_addr + "/api/modem/modemstatus"
        
            api_response = requests.get(url=GET_MODEM_STATUS_API)
            
            UtConfigObject.ut_api_modemstatus_response_successful = True
            decoded_json_data = api_response.json()
            logging.debug(decoded_json_data)        
            UtConfigObject.ut_api_modemstatus_diagnostic_bridge_up = decoded_json_data['diagnostic_bridge_up']
        
            UtConfigObject.ut_api_modemstatus_qmi_client_connected = decoded_json_data['qmi_client_connected']
        
            UtConfigObject.ut_api_modemstatus_operating_mode = decoded_json_data['operating_mode']
        
            UtConfigObject.ut_api_modemstatus_mgt_connection_status = decoded_json_data['mgt_connection_status']

            UtConfigObject.ut_api_modemstatus_wan_connection_status = decoded_json_data['wan_connection_status']
        
        except Exception as e:
            print("API request for get modem status unsuccessful : " + str(e))
     
        return
        
    # Get_IF_Status
    def get_if_status(self,UtConfigObject):
        logging.debug("Get IF status on SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        
        UtConfigObject.ClearUtApiIfStats()
        try:
            GET_IF_STATUS_API = "http://" + UtConfigObject.ut_ssm_ip_addr + "/api/system/ifstats"
            api_response = requests.get(url=GET_IF_STATUS_API)
            UtConfigObject.ut_api_ifstats_response_successful = True

            decoded_json_data = api_response.json()
            logging.debug(decoded_json_data)
        
            ant_if_status_decoded = decoded_json_data['IF_ANT']
            cnx_if_status_decoded = decoded_json_data['IF_CNX']
            mgt_if_status_decoded = decoded_json_data['IF_MGT']
            wan_if_status_decoded = decoded_json_data['IF_WAN']
           
            ant_if_ipv4_address = ant_if_status_decoded['ifAddr']
            ant_if_ipv4_mask = ant_if_status_decoded['ifAddrMask']
            ant_if_name =   ant_if_status_decoded['ifName']
            ant_if_status = ant_if_status_decoded['ifStatus']
        
            UtConfigObject.ut_api_ifstats_wan_ipv4_addr = wan_if_status_decoded.get('ifAddr','field_not_present')
        
            UtConfigObject.ut_api_ifstats_mgt_ipv4_addr = mgt_if_status_decoded.get('ifAddr','field_not_present')       
        
            UtConfigObject.ut_api_ifstats_wan_ipv6_addr = wan_if_status_decoded.get('if6AddrGlobal','field_not_present')  
            UtConfigObject.ut_api_ifstats_mgt_ipv6_addr = mgt_if_status_decoded.get('if6AddrGlobal','field_not_present')  

            UtConfigObject.ut_api_ifstats_wan_ipv4_addr_mask = wan_if_status_decoded.get('ifAddrMask','field_not_present')
            UtConfigObject.ut_api_ifstats_mgt_ipv4_addr_mask = mgt_if_status_decoded.get('ifAddrMask','field_not_present')
        
            UtConfigObject.ut_api_ifstats_wan_if_status = wan_if_status_decoded.get('ifStatus','Down')
            UtConfigObject.ut_api_ifstats_mgt_if_status = mgt_if_status_decoded.get('ifStatus','Down')       
        
        except Exception as e:
            print("API request Unsuccessful : " + str(e))      
        
        return

    # Get_IF_Status
    def print_if_status(self,UtConfigObject):
        logging.debug("Print IF status on SSM with tag %s and IP  %s" , UtConfigObject.ut_tag , UtConfigObject.ut_ssm_ip_addr )
        
        print ("WAN Address : " + str(UtConfigObject.ut_api_ifstats_wan_ipv4_addr))
        
        print ("MGT Address : " + str(UtConfigObject.ut_api_ifstats_mgt_ipv4_addr))        
        
        print ("WAN v6 Address : " + str(UtConfigObject.ut_api_ifstats_wan_ipv6_addr))  
        print ("MGT v6 Address : " + str(UtConfigObject.ut_api_ifstats_mgt_ipv6_addr))  

        print ("WAN Address mask: " + str(UtConfigObject.ut_api_ifstats_wan_ipv4_addr_mask))
        print ("MGT Address mask: " + str(UtConfigObject.ut_api_ifstats_mgt_ipv4_addr_mask))
        
        print ("WAN IF status : " + str(UtConfigObject.ut_api_ifstats_wan_if_status)) 
        print ("MGT IF Status : " + str(UtConfigObject.ut_api_ifstats_mgt_if_status))
      
        return
    # connect_qxdm
    def connect_ut_to_qxdm(self,UtConfigObject):
        logging.debug("Connect UT to QXDM")
        qxdm_instance_started = False
        # AppId for the QXDM Automation Application.
        try:
            qxdm_application_id = win32.gencache.EnsureDispatch('QXDM.QXDMAutoApplication')
            time.sleep(1)
            qxdm_instance_id = qxdm_application_id.GetAutomationWindow2()
            qxdm_instance_id.SetVisible(True)
            time.sleep(2)
            qxdm_instance_started = True
            self.associated_qxdm_sessions_list.append(qxdm_instance_id)
            
        except Exception as e:
            print("Exception ! Unable to start QXDM Automation Window : " + str(e))
            
        if (qxdm_instance_started == True) : 
            # Successfully started the QXDM instance assign the Com Port to UT and store it in UT context
            try:
                qxdm_instance_id.SetComPort(str(UtConfigObject.ut_qpst_assigned_com_port))
                ### Disable Autosave option Initially Enable it during start log collection
                ### SetItemStoreAdvanceOptions(bool enable AdvanceMode,uint MaxISFSizeInMB,uint maxISFDuration,bool autosave,uint maxArchives)
                qxdm_instance_id.SetItemStoreAdvanceOptions(True, 250 , 10 , False, 50)
                UtConfigObject.ut_framework_assigned_qxdm_session = qxdm_instance_id
                UtConfigObject.ut_framework_assigned_qxdm_application = qxdm_application_id
            except Exception as e:
                print("Exception ! Unable to Associate UT Com port with QXDM instance : " + str(e))
                
        return

    def start_qxdm_log_collection(self,UtConfigObject) :
        logging.debug("Start Log Collection on QXDM")
        print("start qxdm Log collection")
        UtConfigObject.ut_framework_assigned_qxdm_session.LoadConfig(UtAutomationSuiteConfig.qxdm_log_mask_filepath)
        UtConfigObject.ut_framework_assigned_qxdm_session.SetItemStoreAdvanceOptions(True, 250 , 10 , True, 50)
        print("logmask file path :" + UtAutomationSuiteConfig.qxdm_log_mask_filepath)
        
        if(UtConfigObject.ut_current_test_case_name == "") :
            # Test Case Name Not Set
            baseIsfFileName = UtConfigObject.ut_tag + "_" + UtConfigObject.ut_current_test_start_timestamp + "_"
        elif(UtConfigObject.ut_current_test_case_name != "") :
            # Test case name set
            baseIsfFileName = UtConfigObject.ut_tag + "_" + UtConfigObject.ut_current_test_start_timestamp + "_" + UtConfigObject.ut_current_test_case_name + "_"
            
        print("base ISF fielname : " + baseIsfFileName)
        UtConfigObject.ut_framework_assigned_qxdm_session.SetBaseISFFileName(baseIsfFileName)
        print("base ISF Dirpath  : " + UtConfigObject.ut_qxdm_logfile_path)
        UtConfigObject.ut_framework_assigned_qxdm_session.SetISFDirPath(UtConfigObject.ut_qxdm_logfile_path)
        #UtConfigObject.ut_framework_assigned_qxdm_session.ClearViewItems()
        #print("save file name  : " + (UtConfigObject.ut_qxdm_logfile_path + baseIsfFileName + "_final.isf"))
        #UtConfigObject.ut_framework_assigned_qxdm_session.SaveItemStore((UtConfigObject.ut_qxdm_logfile_path + baseIsfFileName + "_final.isf"))
        
        if (UtConfigObject.ut_framework_assigned_qxdm_session.GetAutoSaveISF() == True) :
            print("Autosave Option enabled")
        
        if (UtConfigObject.ut_framework_assigned_qxdm_session.IsISFAdvancedModeEnabled() == True):
            print("Advanced mode enabled")
        print ("ISF File size set to : " + str(UtConfigObject.ut_framework_assigned_qxdm_session.GetISFFileSize()))
        
        print ("ISF Max Duration : " + str(UtConfigObject.ut_framework_assigned_qxdm_session.GetISFMaxDuration()))
        
        print ("ISF Max Archives : " + str(UtConfigObject.ut_framework_assigned_qxdm_session.GetMaxISFArchives()))
        
        return
        
    def disconnect_ut_from_qxdm(self,UtConfigObject, isLastQxdmSession) :
        assignedComPort = UtConfigObject.ut_framework_assigned_qxdm_session.GetComPort()
        print("comport assigned to UT was " + str(assignedComPort))
        baseIsfFileName = UtConfigObject.ut_framework_assigned_qxdm_session.GetBaseISFFileName()
        saveFileName = baseIsfFileName + "final.isf" 
        UtConfigObject.ut_framework_assigned_qxdm_session.SaveItemStore(UtConfigObject.ut_qxdm_logfile_path + saveFileName)
        UtConfigObject.ut_framework_assigned_qxdm_session.DisconnectFromComport(str(UtConfigObject.ut_qpst_assigned_com_port))
        time.sleep(2)
        #GetComPort
        #GetIsPhoneConnected
        if(isLastQxdmSession):
            UtConfigObject.ut_framework_assigned_qxdm_session.Quit()
        else:
            UtConfigObject.ut_framework_assigned_qxdm_session.Close()
        time.sleep(2)
        

        return
     
        
    # Exit program
    def exit(self):
        self.remove_all_existing_ut_connections()
        if(self.qpst_automation_server_app_handle != 0 ):
            print("Found QPST automation server instance. Closing")
            self.qpst_automation_server_app_handle.Quit()
        sys.exit()
 
    def get_ut_list(self):
    
        ut_list = []
        user_input = input(">>")
        parsed_input = user_input.split(",")
        
        if(parsed_input[0].strip() == 'all') :
            ut_list = self.connectedUtList
            return ut_list
            
        for i in range(0,len(parsed_input)) :
            entry = parsed_input[i].strip()
            if (entry.isnumeric()) :
                if int(entry) in range(1 , len(self.connectedUtList) + 1) :
                    ut_list.append(self.connectedUtList[int(entry) - 1])
                else :
                    ut_list.clear()
                    break
            else :
                ut_list.clear()
                break                                       

        return ut_list
        
# =======================
#      MAIN PROGRAM
# =======================
 
# Main Program
if __name__ == "__main__":
    
    try:
    
        logsDir = "../logs/"
        # Create /logs/ directory if it does not exist
        if not os.path.exists(logsDir):
            os.makedirs(logsDir)

        currentDT = datetime.datetime.now()
        logFileName = "OneWeb_UT_TEST_" + currentDT.strftime("%Y%m%d%H%M%S") + ".log"
    
        logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M',
            filename=logFileName,
            filemode='w')
        
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        
        logging.info("Started Program ")
        logging.info("OneWeb UT AUTOMATED TEST EXECUTION")

        OwUtAutomationFramework = OW_UT_Automation_Framework()
        UtAutomationSuiteConfig = OneWeb_UT_AutomationSuiteConfig()
        OwUtAutomationFramework.ParseForAutomationSuiteConfig(UtAutomationSuiteConfig)
        OwUtAutomationFramework.ProcessAutomationSuiteConfig(UtAutomationSuiteConfig)
        for i in range (0,UtAutomationSuiteConfig.number_of_ut):
            UtConfig = UT_Config()
            ut_config_section = "ut_" + str(i + 1)
            OwUtAutomationFramework.ParseForUtConfig(UtConfig,ut_config_section)
            # Check if UT is reachable and all associated IP addresses are reachable
            UtConfig.ut_current_test_start_timestamp = currentDT.strftime("%Y%m%d%H%M%S")
            OwUtAutomationFramework.utConfigObjectsDict[UtConfig.ut_ssm_ip_addr] = UtConfig
            OwUtAutomationFramework.connectedUtList.append(UtConfig.ut_ssm_ip_addr)

        #OwUtAutomationFramework.start_qpst_automation_server()
        #OwUtAutomationFramework.remove_all_existing_ut_connections()
        while (1):
            OwUtAutomationFramework.main_menu()
    
    except KeyboardInterrupt:
        print("Error Option . . . . ")
        sys.exit(10)

    except Exception as e:
        print("Exceptionnnnn : " + str(e))
        sys.exit(11)

#PURPOSE:To retrieve current and desired component status 
#
# SOURCE CODE FILE: Component_status.py
#
# REVISION HISTORY:
#          DATE:           AUTHOR:         CHANGE:
#          10-09-2019      Manish Saroha   Intial version
#          11-09-2019      Nitin/Amit Soni Final version
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
#       Command Line Parameters to this script:
#
#       ---------------------------------------
#               $1 = EMS Ip address of GN.
#
#       Return values of the script:
#       ----------------------------
#               On successful execution, the exit status is 0
#
###############################################################################


##########################################
# --- Imported Basic Needful Modules --- #
##########################################

import os
import subprocess
import time
import json
import csv
import logging
from datetime import datetime
import signal
import errno
import readline

#defd = collections.defaultdict(lambda : 'Key Not found')

#####################################
# --- Function to Handle Signal --- #
#####################################

def signal_handler(signal,frame):
	logger.debug("Entering Signal Handler to Handle Recieved Signal")
        print('\n');print (" Successfully exited on User Request !! ")
        exit(0)

################################################
# --- Function to Create Directory for Log --- #
################################################

def create_log_dir():
        dir_log = 'comp_logs'
        try:
           os.mkdir(dir_log)
           print("Logger Directory is Created")

        except OSError as e:
            if e.errno == errno.EEXIST:
                print("Log Directory already Exist - Not Creating Again")

##############################################################
# --- Function to Create Directory for Output Json Files --- #
##############################################################

def create_dir():

    global logger
    dir_json = 'json_files'
    dir_sap = 'json_files/sap'
    dir_sac = 'json_files/sac'
    dir_pop = 'json_files/pop'

    try:
       os.mkdir(dir_json)
       os.mkdir(dir_sap)
       os.mkdir(dir_sac)
       os.mkdir(dir_pop)

       logger.debug("Json Files Directory is Successfully Created ")

    except OSError as e:
        if e.errno == errno.EEXIST:
                logger.debug("Json Files Directories already Exist - Not Creating Again")
                logger.debug("Error Number : ",e.errno)

######################################
# --- Function for START_UP MENU --- #
######################################

def start_menu():

     try:
       os.system("clear")

       print("###*** Select the GN Component Type ***###")
       print ("Press 1 --->To Get SAP Components Status")
       print ("Press 2 --->To Get SAC Components Status")
       print ("Press 3 --->To Get POP Components Status")
       print ("Press 4 --->To Exit");print('\n')

       choice = raw_input("Your Choice is : ")

       if choice=='1':
       		print("Getting SAP Components Status ... please Wait !")
		time.sleep(1)
		get_sap()	

       elif choice=='2':
		print("Getting SAC Components Status ... please Wait !")
		time.sleep(1)
		get_sac()	

       elif choice=='3':
		print("Getting POP Components Status ... please Wait !")
		time.sleep(1)
		get_pop()	

       elif choice=='4':
       	        print("Succesfully Exited ...!!")
       	        os.system("exit")

       else:
       	        print("Invalid Choice -- Please Select a valid choice !!")
		time.sleep(1)
		start_menu()

     except Exception as e:
               print("Exception Raised is : ",e)

######################################################
# --- Function for Getting SAP COMPONENTS STATUS --- #
######################################################

def get_sap():
	global jsonftime, ems_ip
	cmd = "curl --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://"+str(ems_ip)+"/gnems/EMSAPI/v1/components/status/segment/sap > json_files/sap/json_sap_"+str(jsonftime)+".json"
        os.system(cmd)
   	with open ("json_files/sap/json_sap_"+str(jsonftime)+".json") as data:
   	   		sap_data = json.load(data);print('\n')
	   		print("COMPONENT NAME || COMPONENT-TYPE || OPERATIONAL-STATE || DESIRED-STATE || swVersion ||")
   			for i in sap_data["componentList"] :
	         		fdata = str(i.get('componentName'))+" || "+str(i.get('componentType'))+" || "+str(i.get('operationalState'))+" || "+str(i.get('desiredState'))+" || "+str(i.get('swVersion'))
       				print(fdata);print('\n')

######################################################
# --- Function for Getting SAC COMPONENTS STATUS --- #
######################################################

def get_sac():
	global jsonftime,ems_ip
        cmd = "curl --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://"+str(ems_ip)+"/gnems/EMSAPI/v1/components/status/segment/sac > json_files/sac/json_sac_"+str(jsonftime)+".json"
        os.system(cmd)
        with open ("json_files/sac/json_sac_"+str(jsonftime)+".json") as data:
              	        sac_data=  json.load(data);print('\n')
	   		print("COMPONENT NAME || COMPONENT-TYPE || OPERATIONAL-STATE || DESIRED-STATE || swVersion  ")
               	        for i in sac_data["componentList"] :
                              fdata = str(i.get('componentName'))+" || "+str(i.get('componentType'))+" || "+str(i.get('operationalState'))+" || "+str(i.get('desiredState'))+" || "+str(i.get('swVersion'))
			      print(fdata); print('\n')

######################################################
# --- Function for Getting POP COMPONENTS STATUS --- #
######################################################

def get_pop():
	global jsonftime, ems_ip
        cmd = "curl --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://"+str(ems_ip)+"/gnems/EMSAPI/v1/components/status/segment/pop > json_files/pop/json_pop_"+str(jsonftime)+".json"
        os.system(cmd)
        with open ("json_files/pop/json_pop_"+str(jsonftime)+".json") as data:
               	         pop_data=  json.load(data);print('\n')
	   		 print("COMPONENT NAME || COMPONENT-TYPE || OPERATIONAL-STATE || DESIRED-STATE  || swVersion ")
               		 for i in pop_data["componentList"] :
                               fdata = str(i.get('componentName'))+" || "+str(i.get('componentType'))+" || "+str(i.get('operationalState'))+" || "+str(i.get('desiredState'))+" || "+str(i.get('swVersion'))
                               print(fdata);print('\n')

######################################################
# --- Execution starts from Here - MAIN_FUNCTION --- #
######################################################

if __name__ == "__main__":

	signal.signal(signal.SIGINT,signal_handler)
	signal.signal(signal.SIGTSTP,signal_handler)
	
	jsonftime=time.strftime("%Y%d%d_%H%M%S")

	time.sleep(1)

	create_log_dir()

	#Basic Configuration for Generating Logs

        logFname = datetime.now().strftime('COMP_DETAILS_%d_%m_%Y:%H_%M.log')
        logging.basicConfig(filename='comp_logs/%s' %(logFname),level=logging.DEBUG,format='%(asctime)s : %(message)s ')
        logger = logging.getLogger()
	
	create_dir()
	os.system("clear")

	print ("#####******************************************#####")
        print ("##### GN Components Status Monitoring  Utility #####")
        print ("#####******************************************#####")
        print ('\n')

	ems_ip=raw_input("Please Enter the IP Address of EMS (x.x.x.21) : ");os.system('clear')

	start_menu()


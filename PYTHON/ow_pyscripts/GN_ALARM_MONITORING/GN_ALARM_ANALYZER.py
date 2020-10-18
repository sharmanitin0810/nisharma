#-----------------------------------------------------------------------------------------
# PURPOSE: To Retrieve Alarms for Ground network GN(GN)
#
# SOURCE CODE FILE: GN_ALARM_ANALYZER.py
#
# REVISION HISTORY:
#          DATE:           AUTHOR:         CHANGE:
#          12-08-19        Amit Soni       Initial version
#          19-08-19        Nitin Sharma    Provided Support For Different Severity of current alarms
#          23-08-19        Nitin/Manish    Final Version Incorporated review comments suggested by Amit/Surya.
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
#
#       ---------------------------------------
#               $1 = EMS Ip address of GN.
#
#       Return values of the script:
#       ----------------------------
#               On successful execution, the exit status is 0
#
###############################################################################


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




def signal_handler(signal,frame):
        logger.debug("Entering Signal Handler to Handle Recieved Signal")
	print('\n');print (" Successfully exited on User Request !! ")
	exit(0)

def create_log_dir():
	dir_log = 'gn_logs'
	try:
	   os.mkdir(dir_log)
           print("Logger Directory is Created")

        except OSError as e:
            if e.errno == errno.EEXIST:
                print("Log Directory already Exist - Not Creating Again")

def create_dir():
  
    global logger  
    dir_curr = 'current_alarms_files'
    dir_all= 'current_alarms_files/all_alarm_files'
    dir_critical = 'current_alarms_files/critical_alarm_files'
    dir_major = 'current_alarms_files/major_alarm_files'
    dir_minor = 'current_alarms_files/minor_alarm_files'
   
    try:
        os.mkdir(dir_curr)
        os.mkdir(dir_all)
        os.mkdir(dir_critical)
        os.mkdir(dir_major)
        os.mkdir(dir_minor)

        print("All Alarm File Directries are Successfully Created ")
        logger.debug("All Alarm File Directries are Successfully Created ")
         
    except OSError as e:
   	if e.errno == errno.EEXIST:
		logger.debug ("All Files Directories already Exist - Not Creating Again")
    		logger.debug ("Error Number : ",e.errno)


def All_Curr_Alarms():
      Curr_GN="curl  --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://"+ems_IP+"/gnems/EMSAPI/v1/alarms"

      c=subprocess.Popen(Curr_GN,stdout=subprocess.PIPE,shell=True) 
      (output,err)=c.communicate()
      print('\n')
      GN_Data = json.loads(output)
      #print (json.dumps(GN_Data,indent =2, sort_keys =True))
      print ("Your EMS Ip Corresponds to GN-ID :",GN_Data['gnId']);print('\n')
      time.sleep(2)
      logftime=time.strftime("%Y%d%d_%H%M%S")
      print("Alarm File Created at  : current_alarms_files/all_alarm_files/GN_"+str(GN_Data['gnId'])+"_all_current_alarms_"+str(logftime)+".csv")
      with open("current_alarms_files/all_alarm_files/GN_"+str(GN_Data['gnId'])+"_all_current_alarms_"+(time.strftime("%Y%d%d_%H%M%S")+".csv"),"w") as writer:
       logger.info("All Current  Alarms are retrived Successfully.")
       #print(data['alarmList'])
       csv.register_dialect('myDialect',
       delimiter = ' ',
       quoting=csv.QUOTE_NONE,
       skipinitialspace=True)
       writer = csv.writer(writer)
       writer.writerow(["ALARM-ID","ALARM-NAME","ALARM-SEVERITY","ALARM-TIME-STAMP","REPORTING-COMP-NAME","FAULTY-COMPONENT","ENTITY-ID"])
       for i in GN_Data['alarmList']:
        GN_Data=str(i["alarmId"])+"  "+str(i["alarmName"])+"  "+str(i["alarmDescription"])+"  "+str(i["alarmSeverity"])
        #print(GN_Data)
        GN_DATA_01=i["alarmId"], i["alarmName"], i["alarmSeverity"], i["timeStamp"], i["reportingComponentName"], i["faultyComponentName"], i["entityId"]
        writer.writerow(GN_DATA_01)


def All_Critical_Alarms():
      Curr_GN="curl  --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://"+ems_IP+"/gnems/EMSAPI/v1/alarms?alarmSeverity=critical"

      c=subprocess.Popen(Curr_GN,stdout=subprocess.PIPE,shell=True)
      (output,err)=c.communicate()
      print('\n')
      GN_Data = json.loads(output)
      #print (json.dumps(GN_Data,indent =2, sort_keys =True))
      print ("Your EMS Ip Corresponds to GN-ID :",GN_Data['gnId']);print('\n')
      time.sleep(2)
      logftime=time.strftime("%Y%d%d_%H%M%S")
      print("Alarm File is Created at : current_alarms_files/critical_alarm_files/GN_"+str(GN_Data['gnId'])+"_all_critical_current_alarms_"+str(logftime)+".csv")
      with open("current_alarms_files/critical_alarm_files/GN_"+str(GN_Data['gnId'])+"_all_critical_current_alarms_"+(time.strftime("%Y%d%d_%H%M%S")+".csv"),"w") as writer:
       logger.info("Critical  Alarms are retrived Successfully.")
     #print(data['alarmList'])
       csv.register_dialect('myDialect',
       delimiter = ' ',
       quoting=csv.QUOTE_NONE,
       skipinitialspace=True)
       writer = csv.writer(writer)
       writer.writerow(["ALARM-ID","ALARM-NAME","ALARM-SEVERITY","ALARM-TIME-STAMP","REPORTING-COMP-NAME","FAULTY-COMPONENT","ENTITY-ID"])
       for i in GN_Data['alarmList']:
        GN_Data=str(i["alarmId"])+"  "+str(i["alarmName"])+"  "+str(i["alarmDescription"])+"  "+str(i["alarmSeverity"])
        #print(GN_Data)
        GN_DATA_01=i["alarmId"], i["alarmName"], i["alarmSeverity"], i["timeStamp"], i["reportingComponentName"], i["faultyComponentName"], i["entityId"]
        writer.writerow(GN_DATA_01)

def All_Major_Alarms():
      Curr_GN="curl  --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://"+ems_IP+"/gnems/EMSAPI/v1/alarms?alarmSeverity=major"

      c=subprocess.Popen(Curr_GN,stdout=subprocess.PIPE,shell=True)
      (output,err)=c.communicate()
      print('\n')
      GN_Data = json.loads(output)
      #print (json.dumps(GN_Data,indent =2, sort_keys =True))
      print ("Your EMS Ip Corresponds to GN-ID :",GN_Data['gnId']);print('\n')
      time.sleep(2)
      logftime=time.strftime("%Y%d%d_%H%M%S")
      print("Alarm File is Created at : current_alarms_files/major_alarm_files/GN_"+str(GN_Data['gnId'])+"_all_major_current_alarms_"+str(logftime)+".csv")
      with open("current_alarms_files/major_alarm_files/GN_"+str(GN_Data['gnId'])+"_all_major_current_alarms_"+(time.strftime("%Y%d%d_%H%M%S")+".csv"),"w") as writer:
       logger.info("Major Alarms are retrived Successfully.")
     #print(data['alarmList'])
       csv.register_dialect('myDialect',
       delimiter = ' ',
       quoting=csv.QUOTE_NONE,
       skipinitialspace=True)
       writer = csv.writer(writer)
       writer.writerow(["ALARM-ID","ALARM-NAME","ALARM-SEVERITY","ALARM-TIME-STAMP","REPORTING-COMP-NAME","FAULTY-COMPONENT","ENTITY-ID"])
       for i in GN_Data['alarmList']:
        GN_Data=str(i["alarmId"])+"  "+str(i["alarmName"])+"  "+str(i["alarmDescription"])+"  "+str(i["alarmSeverity"])
        #print(GN_Data)
        GN_DATA_01=i["alarmId"], i["alarmName"], i["alarmSeverity"], i["timeStamp"], i["reportingComponentName"], i["faultyComponentName"], i["entityId"]
        writer.writerow(GN_DATA_01)

def All_Minor_Alarms():
      Curr_GN="curl  --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://"+ems_IP+"/gnems/EMSAPI/v1/alarms?alarmSeverity=minor"

      c=subprocess.Popen(Curr_GN,stdout=subprocess.PIPE,shell=True)
      (output,err)=c.communicate()
      print('\n')
      GN_Data = json.loads(output)
      #print (json.dumps(GN_Data,indent =2, sort_keys =True))
      print ("Your EMS Ip Corresponds to GN-ID :",GN_Data['gnId']);print('\n')
      time.sleep(2)
      logftime=time.strftime("%Y%d%d_%H%M%S")
      print("Alarm File is Created at : current_alarms_files/minor_alarm_files/GN_"+str(GN_Data['gnId'])+"_all_minor_current_alarms_"+str(logftime)+".csv")
      with open("current_alarms_files/minor_alarm_files/GN_"+str(GN_Data['gnId'])+"_all_minor_current_alarms_"+(time.strftime("%Y%d%d_%H%M%S")+".csv"),"w") as writer:
       logger.info("Minor Alarms are retrived Successfully.")
       csv.register_dialect('myDialect',
       delimiter = ' ',
       quoting=csv.QUOTE_NONE,
       skipinitialspace=True)
       writer = csv.writer(writer)
       writer.writerow(["ALARM-ID","ALARM-NAME","ALARM-SEVERITY","ALARM-TIME-STAMP","REPORTING-COMP-NAME","FAULTY-COMPONENT","ENTITY-ID"])
       for i in GN_Data['alarmList']:
        GN_Data=str(i["alarmId"])+"  "+str(i["alarmName"])+"  "+str(i["alarmDescription"])+"  "+str(i["alarmSeverity"])
       #print(GN_Data)
        GN_DATA_01=i["alarmId"], i["alarmName"], i["alarmSeverity"], i["timeStamp"], i["reportingComponentName"], i["faultyComponentName"], i["entityId"]
        writer.writerow(GN_DATA_01)


def Curr_Alarm_Mon():
      global ems_IP
      if choice1=='1':
  	            ems_IP=raw_input("Enter Ip Address of EMS(Eg: x.x.x.21) : ")
                    print ('\n')
                    print ("Please Wait while we are Retrieving All Current Alarms ...")
                    All_Curr_Alarms()
                    os.system("exit")

      elif choice1=='2':
                    ems_IP=raw_input("Enter Ip Address of EMS(Eg: x.x.x.21) : ")
                    print ('\n')
                    print ("Please Wait while we are Retrieving All Critical Alarms ...")
                    All_Critical_Alarms()
                    os.system("exit")

      elif choice1=='3':
                    ems_IP=raw_input("Enter Ip Address of EMS(Eg: x.x.x.21) : ")
                    print ('\n')
                    print ("Please Wait while we are Retrieving All Major  Alarms ...")
                    All_Major_Alarms()
                    os.system("exit")

      elif choice1=='4':
                    ems_IP=raw_input("Enter Ip Address of EMS(Eg: x.x.x.21) : ")
                    print ('\n')
                    print ("Please Wait while we are Retrieving All Minor  Alarms ... ")
                    All_Minor_Alarms()
                    os.system("exit")

      elif choice1=='5':
                    print("Successfuly Exited ...!!!")
                    os.system("exit")
      else:
	  print("Invalid Choice -- Exiting ")
          os.system("exit") 


if __name__ == "__main__":

	signal.signal(signal.SIGINT,signal_handler)
	signal.signal(signal.SIGTSTP,signal_handler)

	time.sleep(1)

	create_log_dir()

	logFname = datetime.now().strftime('ALARM_%d_%m_%Y:%H_%M.log')
	logging.basicConfig(filename='gn_logs/%s' %(logFname),level=logging.DEBUG,format='%(asctime)s : %(message)s ')
	logger = logging.getLogger()

	create_dir()

    	os.system("clear");print('\n')

  	print ("#####################################################################")
   	print ("########### GROUND NETWORK (GN) CURRENT ALARM ANALYSER ##############")
        print ("#####################################################################")
        print ('\n')
	print ("Press 1 ---> To get CURRENT ALARMS Status")
	print ("Press 2 ---> Exit");print('\n')

	choice=raw_input("Your Choice: ");print ('\n')
	print("You Entered : " ,choice)

if choice=='1':
            os.system("clear")
 	    print ("### GN CURRENT ALARMS MONITORING ###");print ('\n')
 	    print ("Press 1 ---> To get All Current Alarms")
            print ("Press 2 ---> To get All Critical Alarms")
            print ("Press 3 ---> To get All Major Alarms")
            print ("Press 4 ---> To get All Minor Alarms")
            print ("Press 5 ---> Exit")
            choice1=raw_input("Your Choice :")
            Curr_Alarm_Mon(); print ('\n')
              
elif choice=='2':
	    print("Successfully Exited ..!! ")
            os.system("exit")

else:
   print (" Invalid Choice -- Exiting ")
   os.system("exit")
             

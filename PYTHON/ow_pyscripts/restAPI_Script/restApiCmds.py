#!/usr/bin/python
# Version 2
#-----------------------------------------------------------------------------------------
# PURPOSE: To run REST API commands for GET and PUT operations on GN Compoenents.
#
# SOURCE CODE FILE: restApiCmds.py
#
# REVISION HISTORY:
#          DATE:           AUTHOR:         CHANGE:
#          12-08-19        Surya       Initial version
#          20-08-19        Surya       Final Version
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
#
#       Return values of the script:
#       ----------------------------
#               On successful execution, the exit status is 0
#
###############################################################################

import subprocess
from subprocess import Popen, PIPE
import logging
from datetime import datetime

logFname = datetime.now().strftime('restApi_%d_%m_%Y:%H_%M.log')
logging.basicConfig(filename='logs/%s' %(logFname),level=logging.DEBUG)


def main():
        print ('\n')
        print (30 * '-')
        print ("SELECT COMMAND OPTION")
        print (30 * '-')
        print ("1. GET")
        print ("2. PUT")
        print (30 * '-')

        ###########################
        ## Robust error handling ##
        ## only accept int       ##
        ###########################
        ## Wait for valid input in while...not ###
        is_valid=0

        while not is_valid :
                try :
                        choice = int ( raw_input('Enter your choice [1 or 2] : ') )
                        is_valid = 1 ## set it to 1 to validate input and to terminate the while..not loop
                except ValueError, e :
                        print ("'%s' is not a valid integer." % e.args[0].split(": ")[1])

        ### Take action as per selected menu-option ###
        if choice == 1:
                print ("Select GET Command ...")
                print (30 * '-')
                print ("1. Get list of GN Components")
                print ("2. Get list of SAP Components")
                print ("3. Get list of POP Components")
                print ("4. Get list of SAC Components")
                print ("5. Get list of GNOC configuration files")
                print ("6. Get list of configuration database")
                print ("7. Get list of active alarms")
                print ("8. Get list of status of all alarms")
                print (30 * '-')

                is_gvalid=0

                while not is_gvalid :
                        try :
                                gchoice = int ( raw_input('Enter your choice [1-8] : ') )
                                is_gvalid = 1 ## set it to 1 to validate input and to terminate the while..not loop
                        except ValueError, e :
                                print ("'%s' is not a valid integer." % e.args[0].split(": ")[1])
                if gchoice == 1:
                        logging.info('************ GN Component Summary ************')
                        cmd = "curl -i --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/summary"
                elif gchoice == 2:
                        logging.info('************ SAP Component Summary ************')
                        cmd = "curl -i --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/segment/sap"
                elif gchoice == 3:
                        logging.info('************ POP Component Summary ************')
                        cmd = "curl -i --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/segment/pop"
                elif gchoice == 4:
                        logging.info('************ SAC Component Summary ************')
                        cmd = "curl -i --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/segment/sac"
                elif gchoice == 5:
                        logging.info('************ GNOC SRSF file ************')
                        cmd = "curl -i --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/configuration/gnoc"
                elif gchoice == 6:
                        logging.info('************ EMS DB Status ************')
                        cmd = "curl -i --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/db/status"
                elif gchoice == 7:
                        logging.info('************ Alarms Summary ************')
                        cmd = "curl -i --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/alarms"
                elif gchoice == 8:
                        logging.info('************ GN Alarms Summary ************')
                        cmd = "curl -i --insecure -X GET -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/alarms/status"
        elif choice == 2:
                print ("Select PUT Command ...")
                print (30 * '-')
                print ("1. Change state of GN Components")
                print ("2. GN Component Control")
                print ("3. Suppress alarm")
                print ("4. Backup database")
                print ("5. Control GN components")
                print (30 * '-')

                is_pvalid=0

                while not is_pvalid:
                        try:
                                pchoice = int ( raw_input('Enter your choice [1-5] : ') )
                                is_pvalid = 1 ## set it to 1 to validate input and to terminate the while..not loop
                        except ValueError, e :
                                print ("'%s' is not a valid integer." % e.args[0].split(": ")[1])
                if pchoice == 1:
                        print ("You want to change state of ...")
                        print ("1. SAP")
                        print ("2. GN Component")
                        is_psgvalid=0
                                
                        while not is_psgvalid:
                             try:
                                   psgchoice = int ( raw_input('Enter your choice [1-2] : ') )
                                   is_psgvalid = 1 ## set it to 1 to validate input and to terminate the while..not loop
                             except ValueError, e :
                                        print ("'%s' is not a valid integer." % e.args[0].split(": ")[1])
                        print ("Select desired state...")
                        print (30 * '-')
                        print ("1. INSERVICE")
                        print ("2. OUT OF SERVICE")
                       	print ("3. MAINTENANCE")
                        is_psvalid=0

                        while not is_psvalid:
                               	try:
                                       	pschoice = int ( raw_input('Enter your choice [1-3] : ') )
                                       	is_psvalid = 1 ## set it to 1 to validate input and to terminate the while..not loop
                                except ValueError, e :
                                        print ("'%s' is not a valid integer." % e.args[0].split(": ")[1])
                	
			if psgchoice == 1:
                        	sapId = raw_input("Enter SAP ID...: ")
                        	print "Changing state of: %s" %(sapId)
                        	if pschoice == 1:
                                        logging.info('Changing state of SAP: %s',sapId)
                                        cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/state/sapId/%s -d '{\"state\":\"1\"}'" %(sapId)
                                        print cmd
                                if pschoice == 2:
                                        logging.info('Changing state of SAP: %s',sapId)
                                        cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/state/sapId/%s -d '{\"state\":\"2\"}'" %(sapId)
                                        print cmd
                                if pschoice == 3:
                                        logging.info('Changing state of SAP: %s',sapId)
                                        cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/state/sapId/%s -d '{\"state\":\"3\"}'" %(sapId)
                                        print cmd

                	if psgchoice == 2:
                        	compName = raw_input("Enter component name: ")
                        	print "Changing state of: %s" %(compName)
                        	if pschoice == 1:
                                	logging.info('Changing state of: %s',compName)
                                	cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/state/componentName/%s -d '{\"state\":\"1\"}'" %(compName)
                                	print cmd
                        	if pschoice == 2:
                                	logging.info('Changing state of: %s',compName)
                                	cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/state/componentName/%s -d '{\"state\":\"2\"}'" %(compName)
                                	print cmd
                        	if pschoice == 3:
                                	logging.info('Changing state of: %s',compName)
                                	cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/state/componentName/%s -d '{\"state\":\"3\"}'" %(compName)
                                	print cmd
                if pchoice == 2:
                        print ("You want to control of ..")
                        print ("1. Switchover")
                        print ("2. Restart")
                        print ("3. Shutdowm")
                        is_psgvalid=0
                        
                        while not is_psgvalid:
                                 try:
                                         psgchoice = int ( raw_input('Enter your choice [1-3] : ') )
                                         is_psgvalid = 1 ## set it to 1 to validate input and to terminate the while..not loop
                                 except ValueError, e :
                                         print ("'%s' is not a valid integer." % e.args[0].split(": ")[1])
                        print ("Select desired Component...")
                        print ("1. RMS")
                        print ("2. AMS ")
                        print ("3. IMAGE SERVER")
                        is_psvalid=0

                        while not is_psvalid:
                                try:
                                        pschoice = int ( raw_input('Enter your choice [1-3] : ') )
                                        is_psvalid = 1 ## set it to 1 to validate input and to terminate the while..not loop
                                except ValueError, e :
                                        print ("'%s' is not a valid integer." % e.args[0].split(": ")[1])
                                        
                        if psgchoice == 1:
                               if pschoice == 1:
                                        print ("Logical name of RMS")
                                        compName = raw_input("Enter component name: ")
                                        logging.info('Switching %s component',compName)
                                        cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/control/component/%s -d '{\"control\":\"switchover\"}'" %(compName)
                               if pschoice == 2:
                                        print ("Enter Component Rack type")
                                        popId,rack,chassis,blade = input("Enter popId rack chassis blade Value")
                                        logging.info('Switching %s %s %s %s component',popId,rack,chassis,blade)
                                        cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/control/rackType/pop/popId/%s/rack/%s/chassis/%s/blade/%s/ -d '{\"control\":\"switchover\"}'" %(popId,rack,chassis,blade)
                               if pschoice == 3:
                                        print ("Enter Component Rack type")
                                        popId,rack,chassis,blade = input("Enter popId rack chassis blade Value")
                                        logging.info('Switching %s %s %s %s component',popId,rack,chassis,blade)
                                        cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/control/rackType/pop/popId/%s/rack/%s/chassis/%s/blade/%s/ -d '{\"control\":\"switchover\"}'" %(popId,rack,chassis,blade)

                        if psgchoice == 2:
                                if pschoice == 1:
                                     print ("Logical name of Rack type")
                                     popId,rack,chassis,blade = input("Enter popId rack chassis blade Value")
                                     logging.info('Switching %s %s %s %s component',popId,rack,chassis,blade)
                                     cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/control/rackType/pop/popId/%s/rack/%s/chassis/%s/blade/%s/ -d '{\"control\":\"restart\"}'" %(popId,rack,chassis,blade)             
                                if pschoice == 2:
                                     print ("Enter Component Rack type")
                                     popId,rack,chassis,blade = input("Enter popId rack chassis blade Value")
                                     logging.info('Switching %s %s %s %s component',popId,rack,chassis,blade)
                                     cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/control/rackType/pop/popId/%s/rack/%s/chassis/%s/blade/%s/ -d '{\"control\":\"restart\"}'" %(popId,rack,chassis,blade)
                                if pschoice == 3:
                                     print ("Enter Component Rack type")
                                     popId,rack,chassis,blade = input("Enter popId rack chassis blade Value")
                                     logging.info('Switching %s %s %s %s component',popId,rack,chassis,blade)
                                     cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/control/rackType/pop/popId/%s/rack/%s/chassis/%s/blade/%s/ -d '{\"control\":\"restart\"}'" %(popId,rack,chassis,blade)
                        if psgchoice ==3:
                                     print ("Enter Component Rack type")
                                     popId,rack,chassis,blade = input("Enter popId rack chassis blade Value")
                                     logging.info('Switching %s %s %s %s component',popId,rack,chassis,blade)
                                     cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/components/control/rackType/pop/popId/%s/rack/%s/chassis/%s/blade/%s/ -d '{\"control\":\"restart\"}'" %(popId,rack,chassis,blade)

                if pchoice == 3:
                        alarmId = raw_input("Enter Alarm Id to suppress: ")
                        logging.info('Suppressing %s alarm',alarmId)
                        cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/alarms/control/alarmId/%s -d '{\"alarmControl\":\"suppress\"}'" %(alarmId)

                if pchoice == 4:
                        dbName = raw_input("Enter DB name: ")
                        logging.info('Backing up %s',dbName)
                        cmd = "curl -i --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H 'Content-Type:application/json' https://{10.10.128.21}/gnems/EMSAPI/v1/db/control/%s -d '{\"operation\":\"backup\"}'" %(dbName)

                if pchoice == 5:
                        print 
                        main()
        else:
                print ("Invalid number. Try again...")
        
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
  	returned_value = proc.stdout.read()
        print returned_value
        #returned_value = subprocess.call(cmd, shell=True)
        logging.info('Command Output:%s', (returned_value))
        main()


if __name__ == "__main__":
        try:
                main()
        except (KeyboardInterrupt, SystemExit):
                print("\nExiting on user request...!!!")


########################################################################################################
#  Copyright (c) 2020 Hughes Network System, LLC.
#
#  FILE NAME: ulpc_rest_control.py
#
#  DESCRIPTION: Script to control ULPC[enable/disable] via EMS REST API.  
#
#           DATE           NAME          REFERENCE       REASON
#       12/29/2020     Nitin Sharma                  Initial Draft
#
# Additional Information :
#	(a) Use tab size = 2 for this script 
#	(b) Use python-3 for this script.
#######################################################################################################

import os
from datetime import datetime
import subprocess

class ulpc_inputs:

		def __init__(self): 
	
				self.gnId = ''
				self.satId = ''
				self.baseTime = ''
				self.cmdList = ''
				self.startTime = ''
				self.duration = ''
				self.emsIp = ''
				self.ulpc_api = ''

		def ulpc_controller(self):
			try :	
					self.gnId = input("Enter GN Id : ")	
					self.emsIp = input("Enter [GN :" + " " +self.gnId+ "]" + " " +  "EMS IP Address : """)
					self.satId = input("Enter Satellite Id [1 - 65535]: ")	
					self.cmdList = input("Enter ULPC Command [ULPC_ENABLE (1) / ULPC_DISABLE (0) ]: ")
					self.baseTime = input("Enter Basetime of Satellite Contact [GPS format - WWWWSSSSSSmmm]: ")	
					self.startTime = input("Enter Start Time for ULPC [In millisecond (Offset from Basetime)]: ")
					self.duration = input("Enter duration for ULPC Control [In millisecond (as measured from startTime)]: ")

					if self.cmdList == '1':
						print('\n')
						print("Enabling ULPC for SAT Id : " + " " + self.satId)
	
						self.ulpc_api="curl --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H  Content-Type:application/json https://"+self.emsIp+"/gnems/EMSAPI/v1/satellites/power/ulpc  -d '[ {\"satelliteId\": "+self.satId+", \"baseTime\": "+self.baseTime+", \"cmdList\": [ {\"cmd\": \"ULPC_ENABLE\", \"startTime\": "+self.startTime+", \"duration\": "+self.duration+"} ]  } ]'"

						#print("enable_Command :",self.ulpc_api)
						ulpc_enable = subprocess.Popen(self.ulpc_api, shell=True, stdout=subprocess.PIPE)
						api_out = ulpc_enable.stdout.read()
						print("Final Rest API Response : ",api_out)
						

					elif self.cmdList == '0':
						print('\n')
						print("Disabling ULPC for SAT Id : " + " " + self.satId)

						self.ulpc_api="curl --insecure -X PUT -H 'Authorization: Bearer 5b87c735ebc11b9382fb9be3a09558486c44ad2f' -H  Content-Type:application/json https://"+self.emsIp+"/gnems/EMSAPI/v1/satellites/power/ulpc  -d '[ {\"satelliteId\": "+self.satId+", \"baseTime\": "+self.baseTime+", \"cmdList\": [ {\"cmd\": \"ULPC_DISABLE\", \"startTime\": "+self.startTime+", \"duration\": "+self.duration+"} ]  } ]'"

						#print("disable_Command :",self.ulpc_api)
						ulpc_disable = subprocess.Popen(self.ulpc_api, shell=True, stdout=subprocess.PIPE)
						api_out = ulpc_disable.stdout.read()
						print("Final Rest API Response :",api_out)
	
					else:
						print("Invalid ULPC Command Entered ..Exiting !!")
						os.system('exit')
						

			except Exception as e:
				print("ulpc_controller Exceptionnn : ".str(e))
	
if __name__ == "__main__":

		os.system("clear")
		print("*"*45)
		print("#"*10 + " ULPC REST API CONTROLLER " + "#"*9)
		print("*"*45)

		ulpc_object = ulpc_inputs()
		ulpc_object.ulpc_controller()

#-----------------------------------------------------------------------------------------
# PURPOSE: To generate Stats file of GN components and push to EMS.
#
# SOURCE CODE FILE: modStats.py
#
# REVISION HISTORY:
#          DATE:           AUTHOR:         CHANGE:
#          06-06-19        HSC           Initial version
#          20-06-19        HSC           Final version
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
#               -N/A
#       ---------------------------------------
#
#       Return values of the script:
#       ----------------------------
#               On successful execution, the exit status is 0
#
###############################################################################

import json
import os
#import paramiko
import time
import sys
import ConfigParser
import argparse
from datetime import datetime
from socket import *

"""
The "UTC time stamp" is the number of seconds since the "Epoch" (Jan 1st, 1970, 00:00:00 UTC).The GPS timestamp is the same thing but the reference is different,December 31st, 1979, 23:59:42
This script finds out UTC time from a system call and adds a fixed offset to convert UTC time to GPS time"""

GPS_UTC_OFFSET = 315964782
global EMS_IP
global EMS_USER
global EMS_PASS
global EMS_PATH

def getSleepTime():
    dueTime=0
    dt = datetime.now()
    millisec = dt.microsecond / 1000
    #print "MiliSec Val: %d" %(millisec)
    #TOD Broadcast has to go only between 100-500ms since the seconds boundary
    #If milliseconds is less than 100 since seconds boundary, sleep till you cross the 100ms since seconds boundary
    if millisec <= 100:
        dueTime = (100 - millisec)/1000.0
        #print "Adjusting time (<100ms)"
    #If milliseconds is more than 500ms since seconds boundary, sleep till you come cross the next seconds boundary 
    elif millisec >= 500:
        dueTime = (1100 - millisec)/1000.0
        #print "Adjusting time (500ms)"
    return dueTime

def sendFiletoEMS(sFile):
    ssh = paramiko.SSHClient() 
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(EMS_IP, username=EMS_USER, password=EMS_PASS)
    sftp = ssh.open_sftp()
    sftp.put(sFile, EMS_PATH)
    sftp.close()
    ssh.close()

def modifyJson(sFile,stTime):
    with open(sFile, "r") as jsonFile:
    	data = json.load(jsonFile)
    if data["startTime"]:
    	tmp = data["startTime"]
    	data["startTime"] = str(stTime)
    if data["endTime"]:
    	tmp = data["endTime"]
    	data["endTime"] = str(stTime + 300)

    with open(sFile, "w") as jsonFile:
        jsonFile.seek(0)  # rewind
        json.dump(data, jsonFile,indent=4)
    sendFiletoEMS(sFile)

"""    
def modifyCsv(sFile,stTime):
    print "Modifying csv stats file"
    if "acu" in sFile:
    elif "ems" in sFile:
    elif 
"""        

def main():
    parser = argparse.ArgumentParser(description='Stats file modifier script')
    parser.add_argument('statsFile', help='Stats file to be modified')
    args = parser.parse_args()
    if not args.statsFile:
	print "ERROR: Stats file not provided..."
        sys.exit(0)
    else:
    	stats_file = args.statsFile
     
    cfg = ConfigParser.ConfigParser()
    cfg.read("stats.cfg")
    EMS_IP=cfg.get('EMS','EMS_IP')    
    EMS_USER=cfg.get('EMS','EMS_USER')    
    EMS_PASS=cfg.get('EMS','EMS_PASSWORD')    
    EMS_PATH=cfg.get('EMS','EMS_PATH')    
    print "EMS IP:%s EMS USER:%s EMS PASSWORD:%s EMS PATH:%s" %(EMS_IP,EMS_USER,EMS_PASS,EMS_PATH)
    """

    HOST = '192.168.1.255'
    #HOST = '192.168.252.105'
    PORT = 5127
    oldTod = 0
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    print "This script send TOD to MTU Host Processor every second...!"
    """
    try:
        #while True:
    	secondsToSleep = getSleepTime()
    	#print "Time to sleep: %f" %(secondsToSleep)
    	time.sleep(secondsToSleep)
    	gpsTime=(int(time.time())- GPS_UTC_OFFSET) + 1

    	print "GPS Time %d" %(gpsTime)
    	#time.sleep(0.2)
        #data = datetime.now()
        unixTime=datetime.now().strftime('%Y%m%d%H%M%S')
        print "unix time:%s"%(unixTime)
    except KeyboardInterrupt:
        print('Interrupted on user request!')
    if "ut_" in stats_file:
    	try:
	    firstDelPos=stats_file.find("ut_") # get the position of [
            secondDelPos=stats_file.find("_pop") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+3:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "beam" in stats_file:
    	try:
	    firstDelPos=stats_file.find("beam_") # get the position of [
            secondDelPos=stats_file.find("_sap") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+5:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "enodeB" in stats_file:############TBD###################
    	try:
	    #firstDelPos=stats_file.find("ems_") # get the position of [
            secondDelPos=stats_file.find("_pop") # get the position of ]
            newFname = stats_file.replace(stats_file[secondDelPos-10:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string  after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "ulpc" in stats_file:##################TBD###########
    	try:
	    #firstDelPos=stats_file.find("ems_") # get the position of [
            secondDelPos=stats_file.find("_stats") # get the position of ]
            newFname = stats_file.replace(stats_file[secondDelPos-10:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "acu" in stats_file:
    	try:
	    firstDelPos=stats_file.find("acu_") # get the position of [
            secondDelPos=stats_file.find("_gn") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+4:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "ems" in stats_file:
    	try:
	    firstDelPos=stats_file.find("ems_") # get the position of [
            secondDelPos=stats_file.find("_gn") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+4:secondDelPos],str(unixTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "pccm" in stats_file:
    	try:
	    firstDelPos=stats_file.find("pccm_") # get the position of [
            secondDelPos=stats_file.find("_gn") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+5:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "contact" in stats_file:
    	try:
	    firstDelPos=stats_file.find("contact_") # get the position of [
            secondDelPos=stats_file.find("_gn") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+8:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "equipment" in stats_file:
    	try:
	    firstDelPos=stats_file.find("equipment_") # get the position of [
            secondDelPos=stats_file.find("_gn") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+10:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "bucamp" in stats_file:
    	try:
	    firstDelPos=stats_file.find("pol_") # get the position of [
            secondDelPos=stats_file.find("_stats") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+8:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "rcm" in stats_file:
    	try:
	    firstDelPos=stats_file.find("pol_") # get the position of [
            secondDelPos=stats_file.find("_stats") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+8:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "dsm3cp" in stats_file:
    	try:
	    firstDelPos=stats_file.find("pol_") # get the position of [
            secondDelPos=stats_file.find("_stats") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+8:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "spm3cp" in stats_file:
    	try:
	    firstDelPos=stats_file.find("pol_") # get the position of [
            secondDelPos=stats_file.find("_stats") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+8:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""
    elif "spm3soc" in stats_file:
    	try:
	    firstDelPos=stats_file.find("pol_") # get the position of [
            secondDelPos=stats_file.find("_stats") # get the position of ]
            newFname = stats_file.replace(stats_file[firstDelPos+8:secondDelPos],str(gpsTime)) # replace the string between two delimiters
            print newFname # print the string after sub string between dels is replaced
            os.rename(stats_file, newFname)
            #return stats_file[start:end]
        except ValueError:
            return ""

    else:
        print "Stats file format not supported...!!!"

if __name__ == '__main__':
    main()


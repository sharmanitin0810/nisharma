#-----------------------------------------------------------------------------------------
# PURPOSE: This script is used to run RMS dump Commands.
#
# SOURCE CODE FILE: rmsDump.py
#
# REVISION HISTORY:
#          DATE:           AUTHOR:         CHANGE:
#          06-06-19        HSC   	   Initial version
#          07-06-19        HSC		   Final version
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


import paramiko

GW_Data={}
GW_Data["Palermo RMS"] = "10.31.192.32"

for gw in GW_Data:
        print "\n#########################################\n"
        print "Working on GW-",gw
        print "\n"
        matched_count = 0
        not_matched_count = 0
        not_applicable_count = 0
        under_review_count = 0
        obsolete_count = 0
        not_found_count = 0

        nmeIP = GW_Data[gw]

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(nmeIP, username='msat', password='oneweb123')
        print "\n####################### Active Contact #############\n"
        stdin, stdout, stderr = client.exec_command('java -cp "$RMS_HOME/bin/jars/*" com.sedsystems.util.mbean.MBeanClient -p 9790 -n rms -a com.sedsystems.orms.contact.contact:type=SatelliteContactManager dumpActiveContacts 2>&1', timeout=3, get_pty=True)

        for line in stdout:
                print line.strip('\n')
        print "\n####################### Sheduled Contact ############\n"
        stdin, stdout, stderr = client.exec_command('java -cp "$RMS_HOME/bin/jars/*" com.sedsystems.util.mbean.MBeanClient -p 9790 -n rms -a com.sedsystems.orms.contact.contact:type=SatelliteContactManager dumpContactSchedule 2>&1', timeout=3, get_pty=True)

        for line in stdout:
                print line.strip('\n')

        print "\n####################### Failed Contact ############\n"
        stdin, stdout, stderr = client.exec_command('java -cp "$RMS_HOME/bin/jars/*" com.sedsystems.util.mbean.MBeanClient -p 9790 -n rms -a com.sedsystems.orms.contact.contact:type=SatelliteContactManager dumpFailedContacts 2>&1', timeout=3, get_pty=True)

        for line in stdout:
                print line.strip('\n')

        print "\n####################### Dump Alarm ##################\n"
        stdin, stdout, stderr = client.exec_command('java -cp "$RMS_HOME/bin/jars/*" com.sedsystems.util.mbean.MBeanClient -p 9790 -n rms -a com.sedsystems.orms.alarm.alarm:type=EventAndAlarmManagerImpl dumpAlarms 2>&1', timeout=3, get_pty=True)

        for line in stdout:
                print line.strip('\n')

        print "\n####################### Dump Mapping Equipment ##################\n"
        stdin, stdout, stderr = client.exec_command('java -cp "$RMS_HOME/bin/jars/*" com.sedsystems.util.mbean.MBeanClient -p 9790 -n rms -a com.sedsystems.orms.equipmonitor.snp:type=MappingEquipmentModel dumpMappingEquipment 2>&1', timeout=3, get_pty=True)

        for line in stdout:
                print line.strip('\n')

        print "\n######################## Dump SAP Equipment #####################\n"
        stdin, stdout, stderr = client.exec_command('java -cp "$RMS_HOME/bin/jars/*" com.sedsystems.util.mbean.MBeanClient -p 9790 -n rms -a com.sedsystems.orms.equipmonitor.sap:type=SapEquipmentModel dumpSapEquipment 2>&1', timeout=3, get_pty=True)

        for line in stdout:
                print line.strip('\n')

        print "\n######################## Dump ENODE to AXP #####################\n"
        stdin, stdout, stderr = client.exec_command('java -cp "$RMS_HOME/bin/jars/*" com.sedsystems.util.mbean.MBeanClient -p 9790 -n rms -a com.sedsystems.orms.equipmapping.manage:type=EquipmentMappingManager dumpEnodebsToAxps 2>&1', timeout=3, get_pty=True)

        for line in stdout:
                print line.strip('\n')

        print "\n######################## Dump File Table #####################\n"
        stdin, stdout, stderr = client.exec_command('java -cp "$RMS_HOME/bin/jars/*" com.sedsystems.util.mbean.MBeanClient -p 9790 -n rms -a com.sedsystems.orms.config.filetable:type=FileTableManagerImpl dumpFileTable 2>&1', timeout=3, get_pty=True)

        for line in stdout:
                print line.strip('\n')
        client.close()


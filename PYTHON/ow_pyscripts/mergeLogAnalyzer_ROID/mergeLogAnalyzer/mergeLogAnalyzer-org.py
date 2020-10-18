##################################################################################################################################################
#  Copyright Copyright (c) 2020 Hughes Network System, LLC.
#
#  FILE NAME: mergeLogAnalyzer.py
#
#  DESCRIPTION: This script is used to aggregate the data from multiple sources in a test run to provide comprehensive view of the test results.
#
#  DATE           NAME          REFERENCE       REASON
#  09/01/2020     S.Krishna         SPR84291    Initial Draft
#
##################################################################################################################################################

import os
import time
from datetime import datetime, timedelta
from dateutil import parser
import csv
import fnmatch
import sys
import operator
import heapq
import json
import paramiko
import re
import asn1tools
import subprocess
from subprocess import check_output
import xlsxwriter


def extractTime(LineEntry,tzd):
    datePattern1 = re.compile("\w{3} \d{2}-\w{3}-\d{4} \d{2}:\d{2}:\d{2}")
    datePattern2 = re.compile("\w{3} \w{3}\s{1,2}\d{1,2} \d{2}:\d{2}:\d{2} \w{3,4} \d{4}")
    datePattern3 = re.compile("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}")
    timeString=""
    extractedTime=datetime(1,1,1)
    #try:
    dateMatch = datePattern1.search(LineEntry)
    if (dateMatch != None):             
        timeString=dateMatch.group(0)+" UTC"
        #print(timeString)
        extractedTime = parser.parse(timeString,tzinfos=tzd)
        # The PC/CNX time appears to be lagging by 2 minutes, 27 seconds
        extractedTime = extractedTime + timedelta(minutes=1,seconds=19)
    else:
        dateMatch = datePattern2.search(LineEntry)
        if (dateMatch != None):
            timeString=dateMatch.group(0)
            #print(timeString)
            extractedTime = parser.parse(timeString,tzinfos=tzd)
            # SSM timestamp is advanced by 18 seconds (reflecting GPS) 
            if ("UTC" in timeString):
                extractedTime = extractedTime - timedelta(seconds=18)
        else:
            dateMatch = datePattern3.search(LineEntry)                      
            if (dateMatch != None):
                timeString=dateMatch.group(0)+" UTC"
                #print(timeString)
                # This is time in test machine; no adjustment necessary
                extractedTime = parser.parse(timeString,tzinfos=tzd)
    #except:
    #    print("exception occured\n")
    return timeString,extractedTime

def decodeLatLongAlt(hexString):
    SPECIFICATION = '''
    LatLong DEFINITIONS ::= BEGIN
    EllipsoidPointWithAltitude ::= SEQUENCE {
	    latitudeSign				ENUMERATED {north, south},
        degreesLatitude				INTEGER (0..8388607),			-- 23 bit field
        degreesLongitude			INTEGER (-8388608..8388607),	-- 24 bit field
        altitudeDirection			ENUMERATED {height, depth},
        altitude					INTEGER (0..32767)				-- 15 bit field
    }
    END
    '''
    asn1Spec = asn1tools.compile_string(SPECIFICATION,'uper')
    encoded=bytes.fromhex(hexString)
    #print(encoded)
    decoded=asn1Spec.decode('EllipsoidPointWithAltitude',encoded)
    #print(decoded)
    decoded['degreesLatitude'] = decoded['degreesLatitude'] * 90 /(1<<23)
    decoded['degreesLongitude'] = decoded['degreesLongitude'] * 360 / (1<<24)
    alt = decoded['altitude']
    return decoded	

def extractLatLongAlt(hexString):
    LATITUDE_MASK = 0x7fffff
    LONGITUDE_MASK = 0x0000000000ffffff
    LONGITUDE_SIGN_MASK = 0x800000
    ALTITUDE_SIGN_MASK = 0x8000
    ALTITUDE_MASK = 0x7fff
    value=int(hexString,16)
    if (value < 0):
        latitude = -((value >> 40) & LATITUDE_MASK)
    else:
        latitude = (value >> 40) & LATITUDE_MASK
    latitude = latitude * 90/(1<<23)
    longitude = (value >> 16) & LONGITUDE_MASK
    print(f"long:{longitude}")
    if (longitude & LONGITUDE_SIGN_MASK):
        longitude = longitude | ~LONGITUDE_MASK
        print(f"long:{longitude} ")
    else :
        longitude = longitude & LONGITUDE_MASK
        print(f"long:{longitude} ")		
    longitude = longitude * 360/(1<<24)
    print(f"long:{longitude}\n")	
    if (value & ALTITUDE_SIGN_MASK):    	
        altitude = -(value & ALTITUDE_MASK)
    else:
        altitude = value & ALTITUDE_MASK	
    positionString=f"lat: {latitude}, long:{longitude}, alt:{altitude} "
    print(positionString)
    return positionString

def checkAndUpdateNotVisibleBeams(UTSatBeamRecords,currentSatBeam,newSat,newBeam):
    currentSat = currentSatBeam//16
    if (currentSat != newSat):
        if (currentSatBeam != 0):
            currentBeam = currentSatBeam % 16
            if (currentBeam > 0):
                for nonVisibleBeam in reversed(range(currentBeam)):
                    satBeam = currentSat*16+nonVisibleBeam
                    if (satBeam not in UTSatBeamRecords.keys()):
                        UTSatBeamRecords[satBeam] = "NOT_VISIBLE"
                        print(f"summaryEstimation:{satBeam}:{UTSatBeamRecords[satBeam]} ")
        if (newBeam < 15):
            for nonVisibleBeam in range(15,newBeam,-1):
                satBeam = newSat*16+nonVisibleBeam
                if (satBeam not in UTSatBeamRecords.keys()):
                    UTSatBeamRecords[satBeam] = "NOT_VISIBLE"
                    print(f"summaryEstimation:{satBeam}:{UTSatBeamRecords[satBeam]} ")
                        
def estimateSummaryState(list_ind,entryString,UTSatBeamRecords,currentSatBeam,HOPredictionSatBeam):
    if (list_ind ==0):
        if ("_HO" in entryString):
            newSat = int(re.search("Sat = (\d+),", entryString).group(1))
            newBeam = int(re.search("Beam = (\d+),", entryString).group(1))      
            checkAndUpdateNotVisibleBeams(UTSatBeamRecords,HOPredictionSatBeam,newSat,newBeam)
            HOPredictionSatBeam = newSat*16+newBeam
            if ((HOPredictionSatBeam not in UTSatBeamRecords.keys()) or (UTSatBeamRecords[HOPredictionSatBeam] == "NOT_VISIBLE")):
                UTSatBeamRecords[HOPredictionSatBeam] = "NOT_ACQ"
                print(f"summaryEstimation:{HOPredictionSatBeam}:{UTSatBeamRecords[HOPredictionSatBeam]}, entryString:{entryString} ")
    elif (list_ind ==1):
        if (currentSatBeam != 0):  
            if ("from" in entryString):          
                if (UTSatBeamRecords[currentSatBeam] == "PING_FAIL") or (UTSatBeamRecords[currentSatBeam] == "PING_PASS_FAIL"):
                    UTSatBeamRecords[currentSatBeam] = "PING_PASS_FAIL"
                    print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
                elif (UTSatBeamRecords[currentSatBeam] != "RLF") and (UTSatBeamRecords[currentSatBeam] != "RLF_HO") and (UTSatBeamRecords[currentSatBeam] != "SIB_FAIL") and (UTSatBeamRecords[currentSatBeam] != "DETACHED") :
                    UTSatBeamRecords[currentSatBeam] = "PING_PASS"
                    print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
                else:
                    pass
            elif ("no" in entryString):
                if (UTSatBeamRecords[currentSatBeam] == "PING_PASS"):
                    UTSatBeamRecords[currentSatBeam] = "PING_PASS_FAIL"
                    print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
                elif (UTSatBeamRecords[currentSatBeam] == "ATTACHED") or (UTSatBeamRecords[currentSatBeam] == "HO_SUCCESS"):
                    UTSatBeamRecords[currentSatBeam] = "PING_FAIL"
                    print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
                else:
                    pass                
            else:
                pass
    elif (list_ind == 3):
        if ("SystemInformationBlockType1" in entryString):
            newSat = int(re.search("sat:(\d+),",entryString).group(1))
            newBeam = int(re.search("beam:(\d+),",entryString).group(1))
            checkAndUpdateNotVisibleBeams(UTSatBeamRecords,currentSatBeam,newSat,newBeam)
            currentSatBeam = newSat*16+newBeam
            if (currentSatBeam not in UTSatBeamRecords.keys()) or (UTSatBeamRecords[currentSatBeam] == "NOT_ACQ"):
                UTSatBeamRecords[currentSatBeam] = "ACQUIRED"
                print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
            elif(UTSatBeamRecords[currentSatBeam] == "HO_TRIGGERED"):
                UTSatBeamRecords[currentSatBeam] = "HO_SUCCESS"
                print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
            else:
                pass
        elif ("Attach accept" in entryString):
            if (currentSatBeam != 0):
                UTSatBeamRecords[currentSatBeam] = "ATTACHED"
                print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
        elif ("RRCConnectionReconfiguration," in entryString):
            beam = int(re.search("Physical Cell ID = (\d+)",entryString).group(1)) % 32
            if ("targetPhysCellId" in entryString):
                targetBeam = int(re.search("targetPhysCellId (\d+)",entryString).group(1)) % 32
                if (",satellite-identity" in entryString):
                    targetSat = re.search(",satellite-identity \'(.*?)\'", entryString).group(1)
                    targetSat = targetSat.replace(" ","")
                    targetSat = int(targetSat,2)
                else:
                    targetSat = currentSatBeam//16
                checkAndUpdateNotVisibleBeams(UTSatBeamRecords,currentSatBeam,targetSat,targetBeam)
                currentSatBeam = targetSat*16+targetBeam
                UTSatBeamRecords[currentSatBeam] = "HO_TRIGGERED"
                print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
        elif ("EVENT_OW_RRC_RADIO_LINK_FAILURE_STAT" in entryString):
            if (currentSatBeam != 0):
                if (UTSatBeamRecords[currentSatBeam] != "SIB_FAIL") and (UTSatBeamRecords[currentSatBeam] != "DETACHED"):
                    if ("HO FAILURE" in entryString):
                        UTSatBeamRecords[currentSatBeam] = "RLF_HO"
                        print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
                    else :
                        UTSatBeamRecords[currentSatBeam] = "RLF"
                    print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
        elif ("Detach request" in entryString) :
            if (currentSatBeam != 0):
                UTSatBeamRecords[currentSatBeam] = "DETACHED"
                print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
        elif ("EVENT_OW_RRC_SIB_READ_FAILURE" in entryString):
            if (currentSatBeam != 0):
                beam = int(re.search("Cell ID = (\d+)",entryString).group(1)) % 32
                print(f"beam:{beam} currentSatBeam:{currentSatBeam} HOPredictionSatBeam:{HOPredictionSatBeam}")
                if (beam == currentSatBeam % 16):
                    if (UTSatBeamRecords[currentSatBeam] != "RLF") and (UTSatBeamRecords[currentSatBeam] != "RLF_HO") and (UTSatBeamRecords[currentSatBeam] != "DETACHED"):
                        UTSatBeamRecords[currentSatBeam] = "SIB_FAIL"
                        print(f"summaryEstimation:{currentSatBeam}:{UTSatBeamRecords[currentSatBeam]}, entryString:{entryString} ")
                elif ((HOPredictionSatBeam !=0) and ((beam == HOPredictionSatBeam % 16) or (beam == (HOPredictionSatBeam +1) % 16) or (beam == (HOPredictionSatBeam -1 ) % 16))):
                    if (UTSatBeamRecords[HOPredictionSatBeam] != "RLF") and (UTSatBeamRecords[HOPredictionSatBeam] != "RLF_HO") and (UTSatBeamRecords[HOPredictionSatBeam] != "DETACHED"):
                        UTSatBeamRecords[HOPredictionSatBeam] = "SIB_FAIL"
                        print(f"summaryEstimation:{HOPredictionSatBeam}:{UTSatBeamRecords[HOPredictionSatBeam]}, entryString:{entryString} ")
                else:
                    pass
        else:
            pass
    else :
        pass
    return currentSatBeam,HOPredictionSatBeam
    
def createMergeFile(ping_file, sortedAlarms, alarmFilterList, modem_logs, prediction_file_path):

    #print(ping_file)
    print(prediction_file_path)
    print(os.getcwd()+ping_file)
    outfile = ping_file.replace("UT","MergedLog_UT", 1)
    print(os.getcwd()+outfile)
    UTSatBeamRecords = {}
    currentSatBeam = 0
    HOPredictionSatBeam = 0
    
    tz_str = '''-12 Y
    -11 X NUT SST
    -10 W CKT HAST HST TAHT TKT
    -9 V AKST GAMT GIT HADT HNY
    -8 U AKDT CIST HAY HNP PST PT
    -7 T HAP HNR MST PDT
    -6 S CST EAST GALT HAR HNC MDT
    -5 R CDT COT EASST ECT EST ET HAC HNE PET
    -4 Q AST BOT CLT COST EDT FKT GYT HAE HNA PYT
    -3 P ADT ART BRT CLST FKST GFT HAA PMST PYST SRT UYT WGT
    -2 O BRST FNT PMDT UYST WGST
    -1 N AZOT CVT EGT
    0 Z EGST GMT UTC WET WT
    1 A CET DFT WAT WEDT WEST
    2 B CAT CEDT CEST EET SAST WAST
    3 C EAT EEDT EEST IDT MSK
    4 D AMT AZT GET GST KUYT MSD MUT RET SAMT SCT
    5 E AMST AQTT AZST HMT MAWT MVT PKT TFT TJT TMT UZT YEKT
    6 F ALMT BIOT BTT IOT KGT NOVT OMST YEKST
    7 G CXT DAVT HOVT ICT KRAT NOVST OMSST THA WIB
    8 H ACT AWST BDT BNT CAST HKT IRKT KRAST MYT PHT SGT ULAT WITA WST
    9 I AWDT IRKST JST KST PWT TLT WDT WIT YAKT
    10 K AEST ChST PGT VLAT YAKST YAPT
    11 L AEDT LHDT MAGT NCT PONT SBT VLAST VUT
    12 M ANAST ANAT FJT GILT MAGST MHT NZST PETST PETT TVT WFT
    13 FJST NZDT
    11.5 NFT
    10.5 ACDT LHST
    9.5 ACST
    6.5 CCT MMT
    5.75 NPT
    5.5 SLT
    4.5 AFT IRDT
    3.5 IRST
    -2.5 HAT NDT
    -3.5 HNT NST NT
    -4.5 HLV VET
    -9.5 MART MIT'''
    tzd = {}
    for tz_descr in map(str.split, tz_str.split('\n')):
        tz_offset = int(float(tz_descr[0]) * 3600)
        for tz_code in tz_descr[1:]:
            tzd[tz_code] = tz_offset
    
    
    if(os.path.exists(os.getcwd() + outfile)):
        os.remove(os.getcwd() + outfile)
        
    writeFile = open(os.getcwd() + outfile,"w+")

    ping_file = os.getcwd() + ping_file
    modem_file = False
    
    if(len(modem_logs) > 0):
        modem_file = open(os.getcwd() + modem_logs[0])
        print(modem_logs[0])
    modem_filenum = 0

    HOPredictionEntry = True
    PingLineEntry = True
    alarmLineEntry = True
    CallLogEntry = True
    HandoverLogEntry = True
    exit_cond = False

    heapOfLeastElementOfAllFiles = []

    if (prediction_file_path != ""):
        #prediction_file_path = os.getcwd() + prediction_file_path    
        csvFile = open(os.getcwd()+ prediction_file_path,"r")
        reader = csv.DictReader(csvFile)
        HOPredictionEntry = next(reader)
        HOPredictionEntryTime = HOPredictionEntry['SimUTCTime']
        HOPredictionEntryTime = parser.parse(HOPredictionEntryTime + "UTC", tzinfos = tzd)
        HOPredictionEntryIndex=0
        heapOfLeastElementOfAllFiles.append((HOPredictionEntryTime,0,HOPredictionEntryIndex,"HO PREDICTION: "+HOPredictionEntry['SimUTCTime'] + ", " + HOPredictionEntry['HoType'] + ", Sat = " + HOPredictionEntry['Sat'] + ", Beam = " + HOPredictionEntry['Beam'] + ", gnId = " + HOPredictionEntry['gnId'] + ", fwdChan = " + HOPredictionEntry['fwdChan'] + ", revChan = " + HOPredictionEntry['revChan'] + ", Info = " + HOPredictionEntry['Info']+"\n"))
    else:
        csvFile = None      
    pingFile=open(ping_file,'r')
    #print(ping_file)
    validTimeEntry = False

    while(validTimeEntry == False):
        PingLineEntry = pingFile.readline()
        #print(PingLineEntry)
        if (PingLineEntry != ""):
            timeString,pingTime = extractTime(PingLineEntry,tzd)
            if (timeString != ""):
                validTimeEntry = True                                       
        else:
            # No valid timestamp in the file; no merge required..
            pingFile.close()  
            writeFile.close()
            modem_file.close()                
            if (csvFile != None):
                csvFile.close() 
            return UTSatBeamRecords
    pingEntryIndex = 0       
    heapOfLeastElementOfAllFiles.append((pingTime,1,pingEntryIndex,"PING          : "+PingLineEntry))
    
    if(len(sortedAlarms) > 0):
        iterSortedAlarms = iter(sortedAlarms)
        alarmLineEntry = next(iterSortedAlarms)
        entryToWrite = alarmLineEntry[1]["formattedRaisedTime"] + ", ClearTime:" + alarmLineEntry[1]["formattedClearTime"] + ", alarmID:" + str(alarmLineEntry[1]["alarmId"]) + ", alarmName:" + alarmLineEntry[1]["alarmName"] + ", reportingEntity:" + alarmLineEntry[1]["reportingEntityName"] + ", faultyEntity:" + alarmLineEntry[1]["faultyEntityName"] + ", entityId: " + alarmLineEntry[1]["entityId"] + ", supportingData:" + alarmLineEntry[1]["supportingData"] + ", Description:" + str(alarmLineEntry[1]["alarmDescription"])+"\n"
        alarmNum = alarmLineEntry[1]["alarmId"]
        alarmIndex = 0
        alarmTime = parser.parse(alarmLineEntry[1]["formattedRaisedTime"] + "UTC", tzinfos=tzd)
        
        try:
            while(alarmNum in alarmFilterList):
                alarmLineEntry = next(iterSortedAlarms) 
                entryToWrite = alarmLineEntry[1]["formattedRaisedTime"] + ", ClearTime:" + alarmLineEntry[1]["formattedClearTime"] + ", alarmID:" + str(alarmLineEntry[1]["alarmId"]) + ", alarmName:" + alarmLineEntry[1]["alarmName"] + ", reportingEntity:" + alarmLineEntry[1]["reportingEntityName"] + ", faultyEntity:" + alarmLineEntry[1]["faultyEntityName"] + ", entityId: " + alarmLineEntry[1]["entityId"] + ", supportingData:" + alarmLineEntry[1]["supportingData"] + ", Description:" + str(alarmLineEntry[1]["alarmDescription"])+"\n"
                alarmNum = alarmLineEntry[1]["alarmId"]
                alarmTime = parser.parse(alarmLineEntry[1]["formattedRaisedTime"] + "UTC", tzinfos=tzd)
            heapOfLeastElementOfAllFiles.append((alarmTime,2,alarmIndex,"ALARM        : "+entryToWrite))
        except:
            print(f"exception occurred {alarmLineEntry}\n")
            pass
    
    if(modem_file != False):
        LogEntry = ""
        while(LogEntry == "" and exit_cond == False):
            LogEntry = getUTLine(modem_file)
            if(LogEntry != ""):
                LogTime = parser.parse(LogEntry[0:25] + "UTC", tzinfos=tzd)
                LogTime = LogTime - timedelta(seconds=18)
                LogIndex = 0
                heapOfLeastElementOfAllFiles.append((LogTime,3,LogIndex,"MDM          : "+LogEntry))
                #print(f"{LogTime} First entry: {LogEntry}\n")
            else:
                modem_filenum = modem_filenum + 1
                if(modem_filenum == len(modem_logs)):
                    exit_cond = True
                else:
                    modem_file = open(os.getcwd() + "\\" + modem_logs[modem_filenum])
                    print(modem_logs[modem_filenum])
            
    
    heapq.heapify(heapOfLeastElementOfAllFiles)
    
    while(heapOfLeastElementOfAllFiles):
        val, list_ind, element_ind, entryString = heapq.heappop(heapOfLeastElementOfAllFiles)
        writeFile.write(entryString)
        currentSatBeam,HOPredictionSatBeam = estimateSummaryState(list_ind,entryString,UTSatBeamRecords,currentSatBeam,HOPredictionSatBeam)
        if (list_ind == 0):
            try:
                HOPredictionEntry = next(reader)
                if (HOPredictionEntry != None):
                    HOPredictionEntryTime = HOPredictionEntry['SimUTCTime']
                    HOPredictionEntryIndex = HOPredictionEntryIndex + 1
                    HOPredictionEntryTime = parser.parse(HOPredictionEntryTime + "UTC", tzinfos = tzd)
                    heapq.heappush(heapOfLeastElementOfAllFiles,(HOPredictionEntryTime,0,HOPredictionEntryIndex,"HO PREDICTION: "+ HOPredictionEntry['SimUTCTime'] + ", " + HOPredictionEntry['HoType'] + ", Sat = " + HOPredictionEntry['Sat'] + ", Beam = " + HOPredictionEntry['Beam'] + ", gnId = " + HOPredictionEntry['gnId'] + ", fwdChan = " + HOPredictionEntry['fwdChan'] + ", revChan = " + HOPredictionEntry['revChan'] + ", Info = " + HOPredictionEntry['Info'] + "\n"))
            except:
                csvFile.close()
        elif (list_ind == 1):
            validTimeEntry = False
            while(validTimeEntry == False):
                PingLineEntry = pingFile.readline()          
                if (PingLineEntry != ""):
                    timeString,pingTime = extractTime(PingLineEntry,tzd)
                    if (timeString != ""):
                        validTimeEntry = True   
                        pingEntryIndex = pingEntryIndex + 1
                        heapq.heappush(heapOfLeastElementOfAllFiles,(pingTime,1,pingEntryIndex,"PING         : "+PingLineEntry))
                else:
                    pingFile.close()
                    validTimeEntry = True                
        elif (list_ind == 2):
            try:
                alarmLineEntry = next(iterSortedAlarms)
                if(alarmLineEntry != None):
                    alarmNum = alarmLineEntry[1]["alarmId"]
                    entryToWrite = alarmLineEntry[1]["formattedRaisedTime"] + ", ClearTime:" + alarmLineEntry[1]["formattedClearTime"] + ", alarmID:" + str(alarmLineEntry[1]["alarmId"]) + ", alarmName:" + alarmLineEntry[1]["alarmName"] + ", reportingEntity:" + alarmLineEntry[1]["reportingEntityName"] + ", faultyEntity:" + alarmLineEntry[1]["faultyEntityName"] + ", entityId: " + alarmLineEntry[1]["entityId"] + ", supportingData:" + str(alarmLineEntry[1]["supportingData"] or 'None') + ", Description:" + str(alarmLineEntry[1]["alarmDescription"] or 'None')+"\n"
                    if(alarmNum not in alarmFilterList):
                        alarmTime = parser.parse(alarmLineEntry[1]["formattedRaisedTime"] + "UTC", tzinfos=tzd)
                    else:
                        while(alarmNum in alarmFilterList):
                            alarmLineEntry = next(iterSortedAlarms)
                            entryToWrite = alarmLineEntry[1]["formattedRaisedTime"] + ", ClearTime:" + alarmLineEntry[1]["formattedClearTime"] + ", alarmID:" + str(alarmLineEntry[1]["alarmId"]) + ", alarmName:" + alarmLineEntry[1]["alarmName"] + ", reportingEntity:" + alarmLineEntry[1]["reportingEntityName"] + ", faultyEntity:" + alarmLineEntry[1]["faultyEntityName"] + ", entityId: " + alarmLineEntry[1]["entityId"] + ", supportingData:" + str(alarmLineEntry[1]["supportingData"] or 'None')+ ", Description:" + str(alarmLineEntry[1]["alarmDescription"] or 'None')+"\n"
                            alarmNum = alarmLineEntry[1]["alarmId"]
                            alarmTime = parser.parse(alarmLineEntry[1]["formattedRaisedTime"] + "UTC", tzinfos=tzd)
                    alarmIndex = alarmIndex + 1
                    heapq.heappush(heapOfLeastElementOfAllFiles,(alarmTime,2,alarmIndex,"ALARM        : "+entryToWrite))

            except:
                pass
        elif (list_ind == 3):
            #print("Popped UTLog Entry\n")
            LogEntry = ""
            while(LogEntry == "" and exit_cond == False):
                LogEntry = getUTLine(modem_file)
                if(LogEntry != ""):
                    #print(f"New Entry: {LogEntry}\n {LogEntry[0:25]}\n")
                    LogTime = parser.parse(LogEntry[0:25] + "UTC", tzinfos=tzd)
                    LogTime = LogTime - timedelta(seconds=18)
                    LogIndex = LogIndex + 1
                    heapq.heappush(heapOfLeastElementOfAllFiles,(LogTime,3,LogIndex,"MDM          : "+LogEntry) )
                else:
                    modem_file.close()
                    modem_filenum = modem_filenum + 1
                    if(modem_filenum == len(modem_logs)):
                        exit_cond = True
                    else:
                        modem_file = open(os.getcwd() + "\\"+ modem_logs[modem_filenum])
                        print(modem_logs[modem_filenum])
    writeFile.close()
    return UTSatBeamRecords
    
def getUTLine(UTlog):
    
    lineToWrite = ""
    while(lineToWrite == ""):
        logLine = UTlog.readline()
        if(logLine == ""):
            return ""
        if("OW RRC OTA Packet" in logLine):
            if ("RRCConnectionRequest" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", "+logLine.strip()
                i = 0
                while (i < 14):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", "+logLine.strip()
                if ("s-TMSI" in logLine):
                    logLine = UTlog.readline()
                    logLine = UTlog.readline()
                    logLine = UTlog.readline()
                    lineToWrite = lineToWrite + ", " + logLine.strip()
                    logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.lstrip()				
            elif ("RRCConnectionReject" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.strip()
                i = 0
                while (i < 15):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif ("RRCConnectionSetupComplete" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                #print(f"{logLine}\n")
                logLine = UTlog.readline()
                #print(f"{logLine}\n")
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + "," + logLine.lstrip()
                #print(f"{lineToWrite}\n")
            elif("RRCConnectionSetup" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.strip()
                i = 0
                while (i < 102):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.strip()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif ("SecurityModeCommand" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif ("SecurityModeComplete" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif ("RRCConnectionReconfigurationComplete" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif ("RRCConnectionReconfiguration" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.strip()
                i = 0
                while (i < 15):
                    logLine = UTlog.readline()
                    i = i + 1
                if ("mobilityControlInfo" in logLine):
                    logLine = UTlog.readline()
                    logLine = UTlog.readline()
                    lineToWrite = lineToWrite + ", " + logLine.strip()
                    logLine = UTlog.readline()
                    logLine = UTlog.readline()
                    lineToWrite = lineToWrite + logLine.strip()
                    i = 0
                    while (i < 20):
                        logLine = UTlog.readline()
                        i = i + 1
                    lineToWrite = lineToWrite + logLine.strip()
                    logLine = UTlog.readline()
                    logLine = UTlog.readline()
                    logLine = UTlog.readline()
                    i = 0
                    while (i < 7):
                        logLine = UTlog.readline()
                        lineToWrite = lineToWrite + logLine.strip()
                        i = i + 1
                    i = 0
                    while (i < 33):
                        logLine = UTlog.readline()
                        i = i + 1                    
                    if ("next-satellite-identity" in logLine):
                        lineToWrite = lineToWrite + ", "+logLine.strip()
                lineToWrite = lineToWrite + "\n"
            elif ("RRCConnectionReestablishmentRequest" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.strip()			
                i = 0
                while (i < 15):
                    logLine = UTlog.readline()
                    i = i + 1
                i=0
                while (i < 4):
                    logLine = UTlog.readline()
                    lineToWrite = lineToWrite + ", " + logLine.strip()
                    i = i + 1
                i = 0
                logLine = UTlog.readline()
                while (i < 3):				
                    logLine = UTlog.readline()
                    lineToWrite = lineToWrite + ", " + logLine.strip()
                    i = i + 1	
                lineToWrite = lineToWrite + "\n"
            elif ("RRCConnectionReestablishmentComplete" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.lstrip()	
            elif ("RRCConnectionReestablishment" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.strip()			
                i = 0
                while (i < 75):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.strip()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif ("SystemInformationBlockType1" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.strip()
                i = 0
                while (i < 34):
                    logLine = UTlog.readline()
                    i = i + 1
                cellIdentity = re.search("\'(.*?)\'", logLine).group(1)
                cellIdentity= cellIdentity.replace(" ","")
                cellIdentity=int(cellIdentity,2)
                lineToWrite = lineToWrite + ", sat:" + str(cellIdentity >>8) + ", beam:" +str(cellIdentity & 0xff) + ", " + logLine.lstrip()
            elif ("SystemInformation" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif ("OwLocationIndication" in logLine):
                lineToWrite = logLine.strip()
                i = 0
                while (i < 17):
                    logLine = UTlog.readline()
                    i = i + 1
                ellipsoidPointWithAltitude = re.search("\'(.*?)\'", logLine).group(1)
                positionString = decodeLatLongAlt(ellipsoidPointWithAltitude)
                lineToWrite = lineToWrite + f"{positionString}" + logLine.lstrip()				
            elif ("UECapabilityInformation" in logLine):
                lineToWrite = logLine.strip()
                i = 0
                while (i < 87):
                    logLine = UTlog.readline()
                    i = i + 1
                i=0
                while (i < 10):				
                    logLine = UTlog.readline()
                    lineToWrite = lineToWrite  +  ", " + logLine.strip()
                    i = i + 1	
                lineToWrite = lineToWrite + "\n"
            else:
                #print(f"skipped {logLine}\n")
                lineToWrite = ""
        elif ("OW NAS EMM" in logLine):
            if("Attach request" in logLine):
                lineToWrite = logLine.strip()
                i = 0
                while (i < 14):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.strip()
                if ("IMSI" in logLine):
                    logLine = UTlog.readline()
                    logLine = UTlog.readline()					
                    i = 0
                    while (i < 15):
                        logLine = UTlog.readline()
                        i = i + 1
                        lineToWrite = lineToWrite + ", " + logLine.strip()
                    lineToWrite = lineToWrite + "\n" 
                else :
                    i = 0
                    while (i < 11):
                        logLine = UTlog.readline()
                        i = i + 1
                    lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif("Authentication request" in logLine):
                lineToWrite = logLine
            elif("Authentication failure" in logLine):
                lineToWrite = logLine
            elif("Authentication response" in logLine):
                lineToWrite = logLine
            elif("Security mode command" in logLine):
                lineToWrite = logLine
            elif("Security mode complete" in logLine):
                lineToWrite = logLine
            elif("Service Request Msg" in logLine):
                lineToWrite = logLine			
            elif("Attach accept" in logLine):
                lineToWrite = logLine.strip()
                i = 0
                while (i < 26):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.strip()
                i = 0
                while (i < 5):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.strip()
                i=0
                while (i < 104):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif("Attach complete Msg" in logLine):
                lineToWrite = logLine.strip()
                i = 0
                while (i < 14):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.lstrip()	
            elif("Detach request Msg" in logLine):
                lineToWrite = logLine.strip()
                i = 0
                while(i < 12):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.strip()
                i = 0
                while(i < 14):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif ("Tracking area update request" in logLine):
                lineToWrite = logLine.strip()
                i = 0
                while(i < 26):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.strip()
                i = 0
                while(i < 68):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif ("Tracking area update accept" in logLine):
                lineToWrite = logLine.strip()
                i = 0
                while(i < 29):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
                #i = 0
                #while(i < 68):
                #    logLine = UTlog.readline()
                #    i = i + 1
                #lineToWrite = lineToWrite + ", " + logLine.lstrip()			
            else:
                lineToWrite = ""
                #print(f"skipped {logLine}\n")
        elif ("OW NAS ESM" in logLine):
            if("Activate default EPS bearer context request" in logLine):
                lineToWrite = logLine.strip()
                i = 0
                while (i < 5):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.strip()
                i=0
                while (i < 55):
                    logLine = UTlog.readline()
                    i = i + 1
                if("ipv4_addr" in logLine):
                    lineToWrite = lineToWrite + ", " + logLine.lstrip()
                else :
                    logLine = UTlog.readline()				
                    logLine = UTlog.readline()
                    if ("ipv4_addr" in logLine):
                        lineToWrite = lineToWrite + ", " + logLine.strip()
                        i=0
                        while (i < 7):
                            logLine = UTlog.readline()
                            i = i + 1
                        if("apn_ambr" in logLine):
                            logLine = UTlog.readline()
                            lineToWrite = lineToWrite + ", " + logLine.strip()							
                            logLine = UTlog.readline()
                            lineToWrite = lineToWrite + ", " + logLine.strip()
                    lineToWrite = lineToWrite + "\n"
            elif ("Activate default EPS bearer context accept Msg" in logLine):
                lineToWrite = logLine			
            elif("Activate dedicated EPS bearer context request" in logLine):
                lineToWrite = logLine.strip()
                i = 0
                while (i < 5):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif("Activate dedicated EPS bearer context accept" in logLine):
                lineToWrite = logLine.strip()
                i = 0
                while (i < 5):
                    logLine = UTlog.readline()
                    i = i + 1
                lineToWrite = lineToWrite + ", " + logLine.lstrip()
            elif("PDN connectivity request" in logLine):
                lineToWrite = logLine
            else:
                lineToWrite = "" 
                #print(f"skipped {logLine}\n")				
        elif("OW ML1 Beam Change Evaluation" in logLine):
            lineToWrite = logLine.strip()
            logLine = UTlog.readline()
            logLine = UTlog.readline()
            lineToWrite = lineToWrite + ", " + logLine.strip()
            logLine = UTlog.readline()
            lineToWrite = lineToWrite + ", " + logLine.strip()
            logLine = UTlog.readline()
            logLine = UTlog.readline()
            lineToWrite = lineToWrite + ", " + logLine.strip()
            logLine = UTlog.readline()
            logLine = UTlog.readline()
            logLine = UTlog.readline()
            logLine = UTlog.readline()
            lineToWrite = lineToWrite + ", " + logLine.lstrip()
        elif("OW Random Access Request (MSG1)" in logLine):
            lineToWrite = logLine.strip()
            logLine = UTlog.readline()			
            logLine = UTlog.readline()	
            logLine = UTlog.readline()	
            lineToWrite = lineToWrite + ", " + logLine.strip()
            i = 0
            while (i < 9):
                logLine = UTlog.readline()
                i = i + 1
            lineToWrite = lineToWrite + ", " + logLine.strip()
            logLine = UTlog.readline()
            lineToWrite = lineToWrite + ", " + logLine.strip()
            i = 0
            while (i < 5):
                logLine = UTlog.readline()
                i = i + 1
            lineToWrite = lineToWrite + ", " + logLine.strip()
            logLine = UTlog.readline()
            lineToWrite = lineToWrite + ", " + logLine.lstrip()
        elif("OW Random Access Response (MSG2)" in logLine):
            lineToWrite = logLine.strip()
            i = 0
            while (i < 6):
                logLine = UTlog.readline()
                i = i + 1
            lineToWrite = lineToWrite + ", " + logLine.strip()
            logLine = UTlog.readline()
            logLine = UTlog.readline()
            lineToWrite = lineToWrite + ", " + logLine.strip()
            logLine = UTlog.readline()
            lineToWrite = lineToWrite + ", " + logLine.lstrip()
        elif("OW UE Identification Message (MSG3)" in logLine):
            lineToWrite = logLine.strip()
            i = 0
            while (i < 8):
                logLine = UTlog.readline()
                i = i + 1
            lineToWrite = lineToWrite + ", " + logLine.strip()
            logLine = UTlog.readline()
            lineToWrite = lineToWrite + ", " + logLine.lstrip()
        elif("OW Contention Resolution Message (MSG4)" in logLine):
            lineToWrite = logLine.strip()
            logLine = UTlog.readline()
            logLine = UTlog.readline()
            lineToWrite = lineToWrite + ", " + logLine.strip()
            logLine = UTlog.readline()
            lineToWrite = lineToWrite + ", " + logLine.strip()
            logLine = UTlog.readline()                                                              
            lineToWrite = lineToWrite + ", " + logLine.lstrip()
        elif("0x1FFB  Event" in logLine):
            if ("EVENT_OW_TRACK_ADVISORY" in logLine) or ("EVENT_OW_RRC_RADIO_LINK_FAILURE_STAT" in logLine) or ("EVENT_OW_RRC_SIB_READ_FAILURE" in logLine):
                lineToWrite = logLine.strip()
                logLine = UTlog.readline()
                logLine = UTlog.readline()
                lineToWrite = lineToWrite + ", " + logLine.lstrip()                				
            else:
                lineToWrite = logLine.lstrip()
        else:
            lineToWrite = ""
            #print(f"{logLine}\n")
    return lineToWrite
    
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
       
def getStartEndTimeFromUTLog(dirpath,ut_index):
    UTLogFiles= fnmatch.filter(os.listdir(dirpath),"UT"+ut_index+"_Log_*.txt")
    startTime = None
    endTime = None
    if(len(UTLogFiles)<1):
        print(f"UT{ut_index}Log_*.txt doesn't exist in current directory..")
        sys.exit(1)

    print(UTLogFiles[0])
    with open(os.path.join(dirpath,UTLogFiles[0]),"r") as UTLog:
        lineEntry = UTLog.readline()
        while (lineEntry != ""):
            aDatePattern = re.compile("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
            dateMatch = aDatePattern.search(lineEntry)
            if (dateMatch !=None):
                timeString=dateMatch.group(0)
                lastLineEntry=lineEntry
                if (startTime == None):
                    startTime=datetime.strptime(timeString,'%Y-%m-%d %H:%M:%S')
                    print(f"startTime:{startTime}")
            lineEntry = UTLog.readline()
        if (startTime == None):
            aDatePattern = re.compile("\d{4}-\d{2}-\d{2}-\d{6}")
            dateMatch = aDatePattern.search(UTLogFiles[0])
            if (dateMatch !=None):
                timeString=dateMatch.group(0)  
                startTime=datetime.strptime(timeString,'%Y-%m-%d-%H%M%S')
                endTime=startTime + timedelta(hours=0, minutes=15)
                print(f"startTime:{startTime} endTime:{endTime}")
            else:
                print("datePattern not matching")
        else:
            if ("Exiting" in lastLineEntry):           
                endTime=datetime.strptime(timeString,'%Y-%m-%d %H:%M:%S')
                print(f"endTime:{endTime}")
            else :
                endTime = startTime + timedelta(hours=0, minutes=15)
                print(f"endTime:{endTime}")
    return startTime,endTime

def fetchAlarm(alarmHistoryFile,alarmStartTimeStr,alarmEndTimeStr):
    myclient = getSSHClient("10.31.128.21", "msat", "oneweb123")

    command = "curl -i --insecure 'https://10.31.128.21/gnems/login' -XPOST -H 'Accept: application/json, text/plain, */*' -H 'Content-Type: application/json;charset=utf-8' --data-binary '{\"username\":\"hughesemsadmin\",\"password\":\"Drinksunnyalike5}\",\"selDbName\":\"oneweb_config_01\"}'"
    mystdin,mystdout,mystderr = myclient.exec_command(command,get_pty=True)
    output = mystdout.read().decode('ascii')
    start = output.find("{", 0, len(output)-1)
    output = output[start:len(output)]
    json_info = json.loads(output)
    token = json_info['data']['token']
    
    print(f"alarmStartTime:{alarmStartTimeStr} endTime:{alarmEndTimeStr}\n")
    command = "curl -i --insecure 'https://10.31.128.21/gnems/api/alarmhistory/filter' -XPOST -H 'Content-Type: application/json' -H 'Authorization: Bearer " + token + "' -H 'selDbName: oneweb_config_01' --data-binary '{\"startDate\":\"" + alarmStartTimeStr + "\",\"endDate\":\"" + alarmEndTimeStr + "\",\"severityList\":[],\"alarmIdList\":[],\"reportingEntityList\":[],\"faultyEntityList\":[],\"entityIdList\":[],\"clearedByList\":[],\"page\":0,\"size\":100}'"
    mystdin,mystdout,mystderr = myclient.exec_command(command,get_pty=True)
    
    output = mystdout.read().decode('ascii')
    start = output.find("{", 0, len(output)-1)
    output = output[start:len(output)]
    data = json.loads(output)
    size = data['data']['totalAlarms']
    if ( size > 100):
        command = "curl -i --insecure 'https://10.31.128.21/gnems/api/alarmhistory/filter' -XPOST -H 'Content-Type: application/json' -H 'Authorization: Bearer " + token + "' -H 'selDbName: oneweb_config_01' --data-binary '{\"startDate\":\"" + alarmStartTimeStr + "\",\"endDate\":\"" + alarmEndTimeStr + "\",\"severityList\":[],\"alarmIdList\":[],\"reportingEntityList\":[],\"faultyEntityList\":[],\"entityIdList\":[],\"clearedByList\":[],\"page\":0,\"size\":"+str(size)+"}'"
        mystdin,mystdout,mystderr = myclient.exec_command(command,get_pty=True)
        output = mystdout.read().decode('ascii')
        start = output.find("{", 0, len(output)-1)
        output = output[start:len(output)]                                          
    
    with open(alarmHistoryFile,"w") as alarmFile:
        alarmFile.write(output)
    alarmFile.close()
    myclient.close()

def filterModemLogs(ut_list,ut_index,startTime,endTime):
    filtered_modem_logs = []
    aDatePattern = re.compile("\d{2}-\d{2}\.\d{2}-\d{2}-\d{2}")
    for dirpath, dirs, files in os.walk('.'):
#        for file in fnmatch.filter(files, ut_list[ut_index][1]+"_OAT_PTU_"+ut_list[ut_index][0]+"*.txt"):
#        for file in fnmatch.filter(files, "OTA_Palermo_Logs_UT_"+ut_list[ut_index][0]+"*.txt"):
        for file in fnmatch.filter(files, ut_list[ut_index][1]+"_PTU_"+ut_list[ut_index][0]+"*.txt"):
            print(file)
            dateMatch = aDatePattern.search(file)
            if (dateMatch !=None):
                print(f"TimePattern matched {file}")
                timeString=dateMatch.group(0)
                modemFileTime =datetime.strptime(str(startTime.year)+"-"+timeString,'%Y-%m-%d.%H-%M-%S')
                print(f"Timeline modemFileTime:{modemFileTime}, startTime:{startTime} endTime:{endTime}")
                if (modemFileTime >= startTime) and (modemFileTime <= endTime):
                    file_path= os.path.join(dirpath,file)
                    filtered_modem_logs.append(file_path)
                    print(f"Appended {file_path}")
    return filtered_modem_logs

def summaryStatusConditionalFormat(workbook):
    format_red = workbook.add_format({'bg_color': '#C00000'})
    format_biege = workbook.add_format({'bg_color': '#f8cbad'})
    format_light_green = workbook.add_format({'bg_color': '#a9d08e'})
    format_dark_green = workbook.add_format({'bg_color': '#548235'})
    format_pink = workbook.add_format({'bg_color': '#ffc7ce'})
    format_light_blue = workbook.add_format({'bg_color': '#9bc2e6'})
    format_turquoise = workbook.add_format({'bg_color': '#bf8f00'})
    format_light_gray = workbook.add_format({'bg_color': '#d9d9d9'})
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'NOT_VISIBLE','format':format_light_gray})
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'DETACHED','format':format_red})
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'RLF','format':format_red})
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'SIB_FAIL','format':format_red}) 
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'PING_FAIL','format':format_biege})    
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'PING_PASS_FAIL','format':format_light_green})
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'PING_PASS','format':format_dark_green})
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'HO_SUCCESS','format':format_light_green})
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'ATTACHED','format':format_light_green})
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'HO_TRIGGERED','format':format_pink})
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'ACQUIRED','format':format_light_blue})
    worksheet.conditional_format(1,1,row,maxcol,{'type': 'text', 'criteria' : 'containing', 'value': 'NOT_ACQ','format':format_turquoise})    

def fetchSatSapMap(sortedAlarms):
    satSapMap = {}
    if(len(sortedAlarms) > 0):
        iterSortedAlarms = iter(sortedAlarms)
        alarmLineEntry = next(iterSortedAlarms)
        try:
            while (alarmLineEntry != None):
                if (alarmLineEntry[1]["alarmId"] == 32503):
                    sat = alarmLineEntry[1]["entityId"]            
                    sap = int(re.search("SAP ID: (\d+),", alarmLineEntry[1]["supportingData"]).group(1))         
                    #print(f"sat:{sat} sap:{sap}")
                    if (sat in satSapMap.keys()):
                        if (sap not in satSapMap[sat]):
                            satSapMap[sat].append(sap)
                    else:
                        satSapMap[sat] = [sap]
                alarmLineEntry = next(iterSortedAlarms)
        except:
            pass
    return satSapMap

if __name__ == "__main__":

    if (len(sys.argv)-1)<1:
        print("The script is called with zero arguments\n format: {} <YYYY-MM-DD>".format(sys.argv[0]))
        sys.exit(1)
    else:
      date=sys.argv[1]
    
    try:
        check_output("net use t: /delete")
    except:
        pass
    check_output("net use t: \\\\10.52.4.68\\gn_126\\HSC_SIV\\"+date)
    os.chdir("t:")

    sortedAlarms = []
    alarmFilterList = []
    modem_logs = []


    if (os.path.exists(os.getcwd() + "\\alarmFilterList.txt")):
        alarmFilterListFile = open(os.getcwd() + "\\alarmFilterList.txt",'r')
        alarmFilterListLine = alarmFilterListFile.readline()
        while(alarmFilterListLine != ""):
            alarmFilterList.append(int(alarmFilterListLine.strip()))
            alarmFilterListLine = alarmFilterListFile.readline()

    prediction_file={"PMO":"","CRO":""}
    for dirpath, dirs, files in os.walk('.'):
        for file in fnmatch.filter(files, 'UtBtHandoverSimulation_ho.csv'):
            if ("croatia" in dirpath):
               prediction_file["CRO"] = os.path.join(dirpath,file)
            else:
               prediction_file["PMO"] = os.path.join(dirpath,file)                       

    #summaryFile = open("UTSummaryStatus.csv","w+")
    workbook =xlsxwriter.Workbook("UTSummaryStatus_"+date+".xlsx")
    worksheet = workbook.add_worksheet()
    row=0
    firstPingFile = True    
    ut_list = {"1":("10","PMO"),"2":("20","PMO"),"3":("30","PMO"),"4":("40","PMO")}
    satSapMap =  {}
    for ut_index in ut_list:                
        prev_dirpath= ""
        for dirpath, dirs, files in os.walk('.'):
            for file in fnmatch.filter(files, 'UT'+ut_index+'_PING_*'):
                ping_file= os.path.join(dirpath,file)
                if (dirpath != prev_dirpath):
                    startTime,endTime = getStartEndTimeFromUTLog(dirpath,ut_index)
                    if (startTime == None):
                        continue
                    prev_dirpath = dirpath
                    alarmStartTime = startTime - timedelta(hours=0, minutes=15)
                    alarmEndTime = endTime + timedelta(hours=0,minutes=15)
                    alarmStartTimeStr = alarmStartTime.strftime('%Y-%m-%d %H:%M:%S')
                    alarmStartTimeInMinutesStr = alarmStartTime.strftime('%Y-%m-%d %H:%M')                    
                    alarmHistoryFile = os.path.join(dirpath,"alarmHistoryData"+str(alarmStartTimeInMinutesStr)+".json")
                    alarmHistoryFile = alarmHistoryFile.replace(":","-")
                    if (os.path.exists(alarmHistoryFile) == False):
                        alarmEndTimeStr = alarmEndTime.strftime('%Y-%m-%d %H:%M:%S') 
                        fetchAlarm(alarmHistoryFile,alarmStartTimeStr,alarmEndTimeStr)
                    with open(alarmHistoryFile,"r") as alarmFile:
                        data = json.load(alarmFile)
                        sortedAlarms=sorted(data['data']['alarmHistoryData'].items(), key=lambda x:x[1]["raisedTime"], reverse=False)
                        if (firstPingFile == True):
                            satSapMap = fetchSatSapMap(sortedAlarms)
                            print(satSapMap)             
                    modem_logs = filterModemLogs(ut_list,ut_index,alarmStartTime,alarmEndTime)
                UTSatBeamRecords = createMergeFile(ping_file, sortedAlarms, alarmFilterList, modem_logs, prediction_file[ut_list[ut_index][1]])           
                if (firstPingFile == True):  
                    summaryString = "UT Ping Test\ Sat-beam"
                    sapString = "SAP"
                    firstPingFile= False
                    worksheet.write(row,0,sapString)
                    worksheet.write(row+1,0,summaryString)
                    col=1
                    for key in UTSatBeamRecords.keys() :
                        sat = key//16
                        cellEntry = str (sat) + "-"+ str(key % 16)
                        #summaryString = summaryString + ", " + cellEntry
                        #sapString = sapString + ", " + str(sat)
                        if (str(sat) in satSapMap.keys()):
                            #sapString = sapString + ", "+str(satSapMap[str(sat)])
                            worksheet.write(row,col,str(satSapMap[str(sat)]))
                        else :
                            #sapString = sapString + ", "
                            worksheet.write(row,col,"")
                            print (f"Sat {sat} not found in satSapMap")                            
                        worksheet.write(row+1,col,cellEntry)
                        col += 1
                    #summaryString = summaryString + "\n"
                    #sapString = sapString +"\n"
                    #summaryFile.write(sapString)
                    #summaryFile.write(summaryString)
                    row += 1
                maxcol = col
                row += 1
                summaryString = file
                worksheet.write(row,0,summaryString)                
                col=1
                for key in UTSatBeamRecords.keys() :
                    #summaryString = summaryString + ", " + UTSatBeamRecords[key]
                    worksheet.write(row,col,UTSatBeamRecords[key])
                    col += 1
                #summaryString = summaryString + "\n"
                #summaryFile.write(summaryString)                
    #summaryFile.close()
    summaryStatusConditionalFormat(workbook)
    workbook.close()

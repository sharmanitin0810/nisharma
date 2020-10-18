#!/usr/bin/env python

##########################################################################################
# PURPOSE: The purpose of this file is to create a connection between AIM and SSM.
#          In addition, AIM will receive and process SSM's messages then sending back a 
#          corresponding response message.  
#
# SOURCE CODE FILE: AIM_Emulator.py
#
# REVISION HISTORY:
# DATE:           AUTHOR:         CHANGE:
# 12-03-18        Thanh Le        Initial Version
# 02-04-19        Thanh Le        Replaced enum errorReasons with constant values
#                                 (Enum is not supported in 2.7 version)
#                                 Handle "response" and "fault" msg type
# 02-19-19        Thanh Le        Used Print() from AIM_Common_Definitions.py
# 03-27-19        Thanh Le        SPR 81206 - Derive the UT# to be used in the SWITCH command 
#                                 to the OCS from IF path number
# 04-09-19        Thanh Le        Used lock object to lock/unlock shared resources b/w threads
# 05-07-19        Thanh Le        SPR 81598 - AIME should send "gain_update" msg with msg type
#                                 as "notification" instead of "response"
# 05-22-19        Thanh Le        SPR 81682 - Sync up with OW_SSM_Antenna ICD ver. 1.10
# 05-31-19        Thanh Le        SPR 81767 - Gain Update enhancement
# 06-04-19        Thanh Le        SPR 81702 - AIME enhancements
# 06-11-19        Thanh Le        SPR 81808 - System Info message enhancement
# 06-19-19        Thanh Le        SPR 81872 - AIM needs to send Gain Update soon after 
#                                             receiving tune_rx/tune_tx commands
# 07-18-19        Thanh Le        SPR 82098 - Support for Static mode in AIME
#                                 
# Copyright 2017 Hughes Network Systems Inc
##########################################################################################

import socket                          # need for socket python module
import sys, os                         # need for logging the printed statement
import threading                       # need for creating timer
import ConfigParser                    # need for reading configuration file
from collections import OrderedDict    # need for Ordered Dictionary

import SSM_Msg_Handler
from AIM_Common_Definitions import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../AEC')
import az_el_checker 


class AIMEmu:
    def __init__(self):

        #### Variables from SSM request messages     
        self.fwdChannelSinrAvailable = False       # in 'forward_channel_status_ready' notification
        self.sendGainUpdates = False               # in 'gain_update_control' request message
        self.gainUpdateIntervalMilliseconds = 500  # in 'gain_update_control' request message
        self.includeTimestamp = False              # in 'timstamp_header' request message 
         
        #### AIM class variables
        self.gainUpdateTimer = 0                   # threading
        self.contactRemovalTimer = 0               # threading
        self.threadLock = threading.Lock()         # Lock object which is used to lock/unlock shared resouces
                                                   # b/w threads (in this case - trackIDDict object & ifPathList)
        self.tIDCounter = 0                 

        # NOTE: Please update this list when supporting new SSM request message(s)
        self.supportedSSMReqMsgList = ["track_advisory", "track", "cancel_track", \
                                       "tune_rx_channel", "cancel_rx_tune", "tune_tx_channel", \
                                       "true_north_set", "gain_update_control", \
                                       "system_info", "system_status", "time_sync", \
                                       "blockage_set", "blockage_clear", \
                                       "reset", "sensor_information", \
                                       "run_diagnostic_test", "api_version_info", \
                                       "timestamp_header", "post_results"]

        # Instantiate the following classes
        self.AIMConfigObj              = AIMConfig()               
        self.ssmNotificationsStructObj = SSMNotifications() 
  
        # Key is the track ID - from track_advisory request message, 
        # Value is track ID Info object
        self.trackIDDict = OrderedDict()    # create an empty ordered dictionary
        
        # Key is the frequency (string type) - from [Rx_Freq_To_Gain_Map] section in AIMEmu.cfg
        # Value is the gaindB value (string type)- from [Rx_Freq_To_Gain_Map] section in AIMEmu.cfg
        self.rxFreqToGainDict = dict()

        # Key is the frequency (string type) - from [Tx_Freq_To_Gain_Map] section in AIMEmu.cfg
        # Value is the gaindB value (string type) - from [Rx_Freq_To_Gain_Map] section in AIMEmu.cfg
        self.txFreqToGainDict = dict()

        # Create an empty IF Path ID Info List
        # Index is the IF Path ID
        self.ifPathIDInfoList = []

        # Parse AIMEmu.cfg file to get the following:
        #         - the Rx_AIM and Rx_SSM port numbers, 
        #         - SSM IP addr, 
        self.ParseAIMEmuCfg()
        
        # UT # from a configuration file should be from 0 to 3
        if(self.AIMConfigObj.utNum < 0 or self.AIMConfigObj.utNum > 3):
            Print("WARNING - The Local UT number - " + str(self.AIMConfigObj.utNum) + \
                  " - is out of range (0 to 3). Exiting AIM emulator...")
            sys.exit(1)

        # Instantiate Az/El Checker class    
        self.AECObj = az_el_checker.AzElChecker(self.AIMConfigObj)   
        
        # This list is used to assign if_path_id number for the track_id
        # Initialize the list with all 0, the size of the IF Path list is the number of IF Path
        # The index of the IF Path List represents the if_path_id,
        # The element at the index will be the track_id
        self.ifPathList = [0] * self.AIMConfigObj.numOfIfPath
        
        # Declare server socket upon which will be listening for UDP messages
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind to the port number that SSM Sim uses to send the request
        # (listening to the SSM request messages) 
        # Notes: It must be the same port as SSM Sim uses
        self.serverSock.bind(("", self.AIMConfigObj.aimRxPort))
       
        # IP address and port of the receiver (SSM)
        self.txAddress = (self.AIMConfigObj.ssmIPAddr, self.AIMConfigObj.ssmRxPort)

        # Start the timer
        self.AIMGenericTimerCallBack()


    ####
    #### This method is used to parse AIMEmu.cfg file,
    #### to extract IP address and port number
    ####
    def ParseAIMEmuCfg(self):
        parser = ConfigParser.RawConfigParser()
        parser.read("AIMEmu.cfg")
        self.AIMConfigObj.ssmIPAddr            = parser.get('AIM_config',"SSM_IP_ADDRESS")
        self.AIMConfigObj.ocsIPAddr            = parser.get('AIM_config',"OCS_IP_ADDRESS")
        self.AIMConfigObj.aimRxPort            = parser.getint('AIM_config',"AIM_RX_PORT")
        self.AIMConfigObj.ssmRxPort            = parser.getint('AIM_config',"SSM_RX_PORT")
        self.AIMConfigObj.ocsRxPort            = parser.getint('AIM_config',"OCS_RX_PORT")
        self.AIMConfigObj.utNum                = parser.getint('AIM_config',"UT_NUMBER")
        self.AIMConfigObj.numOfIfPath          = parser.getint('AIM_config',"NUM_OF_IF_PATH")
        self.AIMConfigObj.utcOffset            = parser.getint('AIM_config',"UTC_OFFSET")
        self.AIMConfigObj.trkAdvCoordTolerance = parser.getfloat('AIM_config',"TRACK_ADVISORY_COORD_TOLERANCE")
        self.AIMConfigObj.trkCoordTolerance    = parser.getfloat('AIM_config',"TRACK_COORD_TOLERANCE")
        self.AIMConfigObj.utPosLat             = parser.getfloat('AIM_config',"UT_POSITION_LAT")
        self.AIMConfigObj.utPosLon             = parser.getfloat('AIM_config',"UT_POSITION_LON")
        self.AIMConfigObj.utPosAlt             = parser.getfloat('AIM_config',"UT_POSITION_ALT")
        self.AIMConfigObj.sedfFilePath         = parser.get('AIM_config',"SEDF_FILE_PATH")
        self.AIMConfigObj.gainUpdateMaxChannels= parser.getint('AIM_config', 'GAIN_UPDATE_MAX_CHANNELS')
        self.AIMConfigObj.printGainUpdateMsg   = parser.getboolean('AIM_config',"PRINT_GAIN_UPDATE")
        self.AIMConfigObj.printFwdChannelStatusMsg = parser.getboolean('AIM_config',"PRINT_FWD_CHANNEL_STATUS")
        self.AIMConfigObj.aimeMode             = parser.get('AIM_config', "AIME_MODE") 

        # Parse System Info section  
        self.AIMConfigObj.vendor                = parser.get('System_info', "VENDOR")
        self.AIMConfigObj.model                 = parser.get('System_info', "MODEL")
        self.AIMConfigObj.utClassification      = parser.get('System_info', "UT_CLASSIFICATION")
        self.AIMConfigObj.serialNum             = parser.get('System_info', "SERIAL_NUMBER")        
        self.AIMConfigObj.fwVerCurrent          = parser.get('System_info', "FW_VERSION_CURRENT")
        self.AIMConfigObj.fwVerFactory          = parser.get('System_info', "FW_VERSION_FACTORY")
        self.AIMConfigObj.intraHandoverOutageMs = parser.getint('System_info', "INTRA_HANDOVER_OUTAGE_MS")
        self.AIMConfigObj.interHandoverOutageMs = parser.getint('System_info', "INTER_HANDOVER_OUTAGE_MS")
        self.AIMConfigObj.timeToNextSatMs       = parser.getint('System_info', "TIME_TO_NEXT_SATELLITE_MS")
        self.AIMConfigObj.timeToMoveOneDegreeUs = parser.getint('System_info', "TIME_TO_MOVE_ONE_DEGREE_US")
        self.AIMConfigObj.minElevationAngle     = parser.get('System_info', "MIN_ELEVATION_ANGLE")

        self.AIMConfigObj.isStationary           = parser.get('System_info', "IS_STATIONARY")
        self.AIMConfigObj.isOriented             = parser.get('System_info', "IS_ORIENTED")
        self.AIMConfigObj.isTrueNorthCalibrated  = parser.get('System_info', "IS_TRUE_NORTH_CALIBRATED")
        self.AIMConfigObj.isFullDuplex           = parser.get('System_info', "IS_FULL_DUPLEX")
        self.AIMConfigObj.isRLDualCarrierCapable = parser.get('System_info', "IS_RL_DUAL_CARRIER_CAPABLE")
        
        # The number of IF Path from a configuration file should be from 1 to 2
        if(self.AIMConfigObj.numOfIfPath < 1 or self.AIMConfigObj.numOfIfPath > 2):
            Print("WARNING - The number of IF Path - " + str(self.AIMConfigObj.numOfIfPath) + \
                  " - is out of range (1 to 2). Exiting AIM emulator...")
            sys.exit(1)
 
        for index in range (self.AIMConfigObj.numOfIfPath):
            # Create an IF Path ID Info object and append it to the IF Path ID Info list
            # The IF Path ID Info object will contain specific info of that IF Path ID
            # such as azimuth/elevation correction, tx/rx delays, azimuth min/max, elevation min/maxt, tilt pitch, tilt roll, and temperature.
            self.ifPathIDInfoList.append(IFPathIDInfo())
            
            self.ifPathIDInfoList[index].azimuthCorrection   = parser.get('System_info', "IF_PATH_ID_" + str(index) + "_AZIMUTH_CORRECTION")
            self.ifPathIDInfoList[index].txDelaysInNs        = parser.getint('System_info', "IF_PATH_ID_" + str(index) + "_TX_DELAY_NS") 
            self.ifPathIDInfoList[index].rxDelaysInNs        = parser.getint('System_info', "IF_PATH_ID_" + str(index) + "_RX_DELAY_NS")
            self.ifPathIDInfoList[index].tiltPitchDegrees    = parser.get('Antenna_sensor_info', "IF_PATH_ID_" + str(index) + "_TILT_PITCH_DEGREES")
            self.ifPathIDInfoList[index].tiltRollDegrees     = parser.get('Antenna_sensor_info', "IF_PATH_ID_" + str(index) + "_TILT_ROLL_DEGREES")
            self.ifPathIDInfoList[index].temperatureDegreesC = parser.get('Antenna_sensor_info', "IF_PATH_ID_" + str(index) + "_TEMPERATURE_DEGREES_C")

        # Map the RX frequency with its gaindB value and store it in RX Frequency to Gain dictionary
        for index in range(len(parser.options('Rx_Freq_To_Gain_Map'))):
            self.rxFreqToGainDict[parser.options('Rx_Freq_To_Gain_Map')[index]] =  \
                       parser.get('Rx_Freq_To_Gain_Map', parser.options('Rx_Freq_To_Gain_Map')[index])

        # Map the TX frequency with its gaindB value and store it in TX Frequency to Gain dictionary
        for index in range(len(parser.options('Tx_Freq_To_Gain_Map'))):
            self.txFreqToGainDict[parser.options('Tx_Freq_To_Gain_Map')[index]] =  \
                       parser.get('Tx_Freq_To_Gain_Map', parser.options('Tx_Freq_To_Gain_Map')[index])
        
        Print ("AIM Emulator starting up with the following parameters:\n"                  + \
                    "AIME Software Version                : 3.0.4\n"                        + \
                    "OneWeb SSM-Antenna ICD Version       : 1.10\n"                         + \
                    "SSM IP Address                       : " + self.AIMConfigObj.ssmIPAddr                 + "\n" + \
                    "OCS IP Address                       : " + self.AIMConfigObj.ocsIPAddr                 + "\n" + \
                    "AIM Rx Port                          : " + str(self.AIMConfigObj.aimRxPort)            + "\n" + \
                    "SSM Rx Port                          : " + str(self.AIMConfigObj.ssmRxPort)            + "\n" + \
                    "OCS Rx Port                          : " + str(self.AIMConfigObj.ocsRxPort)            + "\n" + \
                    "UT Number                            : " + str(self.AIMConfigObj.utNum)                + "\n" + \
                    "Number of IF Path                    : " + str(self.AIMConfigObj.numOfIfPath)          + "\n" + \
                    "UTC Offset                           : " + str(self.AIMConfigObj.utcOffset)            + "\n" + \
                    "Track Advisory Coordinates Tolerance : " + str(self.AIMConfigObj.trkAdvCoordTolerance) + "\n" + \
                    "Track Coordinates Tolerance          : " + str(self.AIMConfigObj.trkCoordTolerance)    + "\n" + \
                    "UT Position Latitude                 : " + str(self.AIMConfigObj.utPosLat)             + "\n" + \
                    "UT Position Longtitude               : " + str(self.AIMConfigObj.utPosLon)             + "\n" + \
                    "UT Position Altitude                 : " + str(self.AIMConfigObj.utPosAlt)             + "\n" + \
                    "SEDF File Path                       : " + self.AIMConfigObj.sedfFilePath              + "\n" + \
                    "Gain Update Max Channels             : " + str(self.AIMConfigObj.gainUpdateMaxChannels)+ "\n" + \
                    "Print Gain Update Notification Msg   : " + str(self.AIMConfigObj.printGainUpdateMsg)   + "\n" + \
                    "Print Fwd Channel Status Notification Msg : " + str(self.AIMConfigObj.printFwdChannelStatusMsg) + "\n" + \
                    "AIME Mode                            : " + self.AIMConfigObj.aimeMode) 


    ####
    #### This method is used to receive messages from SSM Sim.
    #### Based on the message, it will send back the corresponding response msg
    ####
    def ProcessSSMMsg(self):
        while True:
          try:
            data, senderAddress = self.serverSock.recvfrom(4096)

            decoded_data = json.loads(data)
            
            # Will not display the "forward_channel_status" notification msg if 
            # the PRINT_FWD_CHANNEL_STATUS flag from config file is set to false
            if (((decoded_data["header"]["message"] == "forward_channel_status") and \
                 (self.AIMConfigObj.printFwdChannelStatusMsg)) or            \
                 (decoded_data["header"]["message"] != "forward_channel_status")):
                Print("Message received: " + str(data))

            if ( decoded_data["header"]["type"] == "request"):
                self.ProcessSSMRequestMsg(decoded_data)
				
            elif (decoded_data["header"]["type"] == "response"):
                self.ProcessSSMResponseMsg(decoded_data)
				
            elif (decoded_data["header"]["type"] == "notification"):
                self.ProcessSSMNotificationMsg(decoded_data)

            else :
                supportStr = "Message type: " + decoded_data["header"]["type"] + " - Unknown message type. Ignore the message !!!" \
                              + " Supported msg type: request, response, and notification."
                SSM_Msg_Handler.SendDefaultResponse(self, decoded_data["header"]["message"], decoded_data["header"]["tid"])              
                SSM_Msg_Handler.SendErrorResponse(self, decoded_data["header"]["tid"],ERR_REASON_MSG_TYPE_UNKNOWN, supportStr)

          except Exception as e:
              Print("Exception : WARNING " + str(e))

			  
    ####
    #### This method is used to process any required SSM response messages
    #### (just a place holder for now)
    ####
    def ProcessSSMResponseMsg(self, decoded_data) :
        return


    ####
    #### This method is used to process any SSM notification messages
    #### (extract and store any necessary information from the notification msgs)
    ####   
    def ProcessSSMNotificationMsg(self, decoded_data) :
        if (decoded_data["header"]["message"] == "forward_channel_status_ready") :
            self.fwdChannelSinrAvailable = decoded_data["body"]["forward_channel_sinr_available"]
            Print("Forward Channel SINR Available: " +  str(self.fwdChannelSinrAvailable))
            SSM_Msg_Handler.SendFwdChannelStatusCtrReq(self)

        elif (decoded_data["header"]["message"] == "satellite_network_switch") :
            self.ssmNotificationsStructObj.networkType     = decoded_data["body"]["network_type"]
            self.ssmNotificationsStructObj.switchTimestamp = decoded_data["body"]["switch_timestamp"]

        elif (decoded_data["header"]["message"] == "drx_wakeup_time") :
            self.ssmNotificationsStructObj.gpsTimeWeek     = decoded_data["body"]["gps_time_week"]
            self.ssmNotificationsStructObj.gpsTimeMicroSec = decoded_data["body"]["gps_time_us"]


    ####
    #### This method is used to process any SSM Request messages
    #### (extract and store any necessary information from the request msgs)
    ####   
    def ProcessSSMRequestMsg(self, decoded_data):
        # if the request message is currently not being supported (not in supportedSSMReqMsgList)
        # then AIM will construct an error response and send it back to SSM
        if decoded_data["header"]["message"] not in self.supportedSSMReqMsgList :
            supportStr = "Unknown Request Message. " + decoded_data["header"]["message"] + \
                         " is not in the supported SSM request msg list. Ignoring the message !!!"
            SSM_Msg_Handler.SendDefaultResponse(self, decoded_data["header"]["message"], decoded_data["header"]["tid"]) 
            SSM_Msg_Handler.SendErrorResponse(self, decoded_data["header"]["tid"],ERR_REASON_REQ_TYPE_UNKNOWN, supportStr) 
            return
        
        # Below are request messages that we need to extract the information from
        if (decoded_data["header"]["message"] == "track_advisory") :
            SSM_Msg_Handler.ProcessTrackAdvisoryMsg(self, decoded_data)

        elif (decoded_data["header"]["message"] == "track") :
            SSM_Msg_Handler.ProcessTrackMsg(self, decoded_data)

        elif (decoded_data["header"]["message"] == "cancel_track") :
            SSM_Msg_Handler.ProcessCancelTrackMsg(self, decoded_data)

        elif (decoded_data["header"]["message"] == "tune_rx_channel") :
            SSM_Msg_Handler.ProcessTuneRxChannelMsg(self, decoded_data)
        
        elif (decoded_data["header"]["message"] == "cancel_rx_tune") :
            SSM_Msg_Handler.ProcessCancelRxTuneMsg(self, decoded_data)

        elif (decoded_data["header"]["message"] == "tune_tx_channel") :
            SSM_Msg_Handler.ProcessTuneTxChannelMsg(self, decoded_data)

        elif (decoded_data["header"]["message"] == "gain_update_control") :
            SSM_Msg_Handler.ProcessGainUpdateControlMsg(self, decoded_data)

        elif (decoded_data["header"]["message"] == "true_north_set"):
            SSM_Msg_Handler.ProcessTrueNorthSetMsg(self, decoded_data)

        elif (decoded_data["header"]["message"] == "blockage_set"):
            SSM_Msg_Handler.ProcessBlockageSetMsg(self, decoded_data)

        elif (decoded_data["header"]["message"] == "timestamp_header") :
            SSM_Msg_Handler.ProcessTimestampHeaderMsg(self, decoded_data)

        else:            
            self.SendResponse(decoded_data)  


    ####
    #### This method is used to construct and send a response message based on the request from SSM
    ####
    def SendResponse(self, decoded_data):
        msgName     = decoded_data["header"]["message"]
        transID     = decoded_data["header"]["tid"]

        if (msgName == "reset" or msgName == "time_sync" or msgName == "blockage_clear"):
            SSM_Msg_Handler.SendDefaultResponse(self, msgName, transID)
    
        elif (msgName == "system_info"):
            SSM_Msg_Handler.SendSystemInfoResponseMsg(self, msgName, transID)
    
        elif (msgName == "system_status"):
            SSM_Msg_Handler.SendSystemStatusResponseMsg(self, msgName, transID)
    
        elif (msgName == "sensor_information"):
            SSM_Msg_Handler.SendSensorInfoResponseMsg(self, msgName, transID)
    
        elif (msgName == "run_diagnostic_test"):
            SSM_Msg_Handler.SendRunDiagnosticTestResponseMsg(self, msgName, transID)
    
        elif (msgName == "api_version_info"):
            SSM_Msg_Handler.SendApiVersionInfoResponseMsg(self, msgName, transID)
    
        elif (msgName == "post_results"):
            SSM_Msg_Handler.SendPostResultsResponseMsg(self, msgName, transID)
        
        # Here is for safe check only(make sure AIM always returns response msg)
        else :
            SSM_Msg_Handler.SendDefaultResponse(self, msgName, transID)

    ####
    #### This method is used to construct a default header 
    ####
    def ConstructHeader(self, message, tid):
        curTimestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        msgType = "response"
        if (message == "gain_update"):
            msgType = "notification"
        
        if (self.includeTimestamp == False):
            header = "{\"header\": {\"type\": \"" + msgType + "\", \"message\": \"" + message + "\", \"tid\":" + str(tid)+ "},"
        else:
            header = "{\"header\": {\"type\": \"" + msgType + "\", \"message\": \"" + message + "\", \"tid\":" + str(tid)+ ", \"timestamp\": \"" + curTimestamp + "\"},"
    
        return header
 

    ####
    #### This method is used to send a response message back the SSM Sim
    ####
    def SendData(self, senderAddress, message, messageName=""):

        self.serverSock.sendto(message, senderAddress)

        # Will not display the "gain_update" notification msg if
        # the PRINT_GAIN_UPDATE flag from config file is set to false
        if (((messageName == "gain_update") and (self.AIMConfigObj.printGainUpdateMsg)) or (messageName == "")):
            Print("Sent: " + message)


    ####
    #### This method is used to periodically send the notification gain_update message to SSM Sim
    #### - the periodicity is based on the gainUpdate interval from Gain Update Control request msg
    ####   
    def GainUpdateTimerCallBack(self):
        if (self.sendGainUpdates == True):
            SSM_Msg_Handler.SendGainUpdateNotification(self)        

        # Create a timer and start again (periodic timer)
        self.gainUpdateTimer = threading.Timer((float(self.gainUpdateIntervalMilliseconds)/MILLISECONDS_IN_SECOND), self.GainUpdateTimerCallBack)
        self.gainUpdateTimer.start()

    
    ####
    #### A generic periodic timer function callback 
    ####
    def AIMGenericTimerCallBack(self):

        if (self.AIMConfigObj.aimeMode == "DYNAMIC"):
            self.CheckForExpiredContact()        

        # Print out what inside the TrackID Dictionary
#        for key, value in self.trackIDDict.items():
#            print key, " : " , value.endTime
            
#        print ""

        # Print out what inside the IF Path List
#        for index in range (len(self.ifPathList)):
#            print self.ifPathList[index]

        # Periodic timer
        self.contactRemovalTimer = threading.Timer((1), self.AIMGenericTimerCallBack)        
        self.contactRemovalTimer.start()


    ####
    #### This method is used to check the end time of the track_advisory message.
    #### If the end time is less than or equal to the current time, then AIM Emulator will remove the track ID
    #### from the trackIDInfo dictionary
    def CheckForExpiredContact(self):
        currentTimeInSec = int(time.time())
        
        #### LOCK
        self.threadLock.acquire()

        for trackID in self.trackIDDict.keys() :

            # If the current time is greater or equal to the end time of the contact,
            #    then...
            if (currentTimeInSec >=  self.trackIDDict[trackID].endTime) :
                Print("Contact End Time has passed. Removed the trackID from trackID Dictionary")
                # Remove a track ID from trackID Dictionary
                self.trackIDDict.pop(trackID)
                
                # if the track ID is inside the ifPathList, then
                #    set the value back to 0
                if trackID in self.ifPathList:
                    self.ifPathList[self.ifPathList.index(trackID)] = 0                     
 
                # Remove the entry of given track ID from AEC map
                self.AECObj.NotifyEndOfContact(trackID)

        self.threadLock.release()
        #### UNLOCK

    ####
    #### This method is used to get the transaction ID.
    #### The transaction ID will be reset back to 0 when it reaches 4294967295 times 
    ####
    def GetTID(self):
        # 4294967295 - UINT32_MAX
        if (self.tIDCounter == 4294967295):
            self.tIDCounter = 0        

        self.tIDCounter = self.tIDCounter + 1

        return self.tIDCounter
    

####
#### Main() method
####  
if __name__ == '__main__':
    try:
    
        logsDir = "../logs/"

        # Create /logs/ directory if it does not exist
        if not os.path.exists(logsDir):
            os.makedirs(logsDir)

        currentDT = datetime.datetime.now()
        logFileName = "AIMEmu_" + currentDT.strftime("%Y%m%d%H%M%S") + ".log"
    
        # Log every printed statement into an outputfile
        filename = open(logsDir + logFileName,'w')
        sys.stdout = filename
        #print "Anything printed will go to the output file"
        
        aimEmu = AIMEmu()
        
        aimEmu.GainUpdateTimerCallBack()     
        
        aimEmu.ProcessSSMMsg()
    
    except KeyboardInterrupt:
        Print("Going down . . . . ")
        aimEmu.gainUpdateTimer.cancel()
        aimEmu.contactRemovalTimer.cancel()
        sys.exit(10)

    except Exception as e:
        Print("Exceptionnnnn : " + str(e))
        aimEmu.gainUpdateTimer.cancel()
        aimEmu.contactRemovalTimer.cancel()
        sys.exit(11)

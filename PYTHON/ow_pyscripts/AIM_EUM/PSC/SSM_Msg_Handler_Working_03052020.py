#!/usr/bin/env python

##########################################################################################
# PURPOSE: Processing SSM's message and constructing a corresponding response
#
# SOURCE CODE FILE: SSM_Msg_Handler.py
#
# REVISION HISTORY:
# DATE:           AUTHOR:         CHANGE:
# 12-03-18        Thanh Le        Initial Version
# 02-04-19        Thanh Le        Replaced enum errorReasons with constant values
#                                 (Enum is not supported in 2.7 version)
#                                 Handle "response" and "fault" msg type
# 02-19-19        Thanh Le        Used Print() from AIM_Common_Definitions.py
#                                 Removed any unrequired comment lines
#                                 Removed "return" condition when validate Az/El failed
# 03-27-19        Thanh Le        SPR 81206 - Derive the UT# to be used in the SWITCH command 
#                                 to the OCS from IF path number
# 04-09-19        Thanh Le        Used lock object to lock/unlock shared resources b/w threads
# 05-07-19        Thanh Le        SPR 81598 - AIME should send "gain_update" msg with msg type
#                                 as "notification" instead of "response"
# 05-22-19        Thanh Le        SPR 81682 - Sync up with OW_SSM_Antenna ICD ver. 1.10
# 05-31-19        Thanh Le        SPR 81767 - Gain Update Enhancement
# 06-04-19        Thanh Le        SPR 81702 - AIME enhancements
# 06-11-19        Thanh Le        SPR 81808 - System Info message enhancement
# 06-19-19        Thanh Le        SPR 81872 - AIM needs to send Gain Update soon after 
#                                             receiving tune_rx/tune_tx commands
# 07-18-19        Thanh Le        SPR 82098 - Support for Static mode in AIME
#
# Copyright 2017 Hughes Network Systems Inc
##########################################################################################

from AIM_Common_Definitions import *

####
#### This method is used to extract any necessary information from 
#### the track_advisory request msg
####   
def ProcessTrackAdvisoryMsg(self, decoded_data):
    tid     = decoded_data["header"]["tid"]
    trackID = decoded_data["body"]["track_id"]

    Print("Track Advisory Track ID: " + str(trackID))

    if_path_id = 0

    # Empty the Track Advisory Coordinates List when processing new track_advisory request message
    trackAdvisoryCoordinatesList = []

    # Create track ID Info Object
    trackIDInfoObj = TrackIDInfo()

    # If the track ID presents in the IF Path List, then do not assign a new IF Path ID
    if trackID in self.ifPathList :
        supportStr = "Ignoring the track_advisory message. An IF path has already been assigned to this track ID " +  str(self.ifPathList.index(trackID))
        SendDefaultResponse(self, decoded_data["header"]["message"], tid)
        SendErrorResponse(self,tid,ERR_REASON_UNKNOWN_ERROR, supportStr)  
        return

    # If the IF Paths are full, no process any further
    if 0 not in self.ifPathList :
        supportStr =  "All IF paths are in use. Ignoring the track_advisory message"
        SendDefaultResponse(self, decoded_data["header"]["message"], tid)
        SendErrorResponse(self,tid,ERR_REASON_UNKNOWN_ERROR, supportStr)   
        return 

    for index in range (len(decoded_data["body"]["coordinates"])):
        # Add each track advisory coordinates into the track advisory coordinates list
        trackAdvisoryCoordinatesList.append(TrackAdvisoryCoordinates())
        trackAdvisoryCoordinatesList[index].azimuthDegree          = decoded_data["body"]["coordinates"][index]["azimuth_degree"]
        trackAdvisoryCoordinatesList[index].elevationDegree        = decoded_data["body"]["coordinates"][index]["elevation_degree"]
        trackAdvisoryCoordinatesList[index].gpsArrivalTimeWeek     = decoded_data["body"]["coordinates"][index]["gps_arrival_time_week"]
        trackAdvisoryCoordinatesList[index].gpsArrivalTimeMicroSec = decoded_data["body"]["coordinates"][index]["gps_arrival_time_us"]

    # Validate track_advisory's Az/El coordinates
    if(self.AECObj.ValidateTrackAdvisoryAzElCoordinates((trackID%65536), trackAdvisoryCoordinatesList) == False):
        Print("WARNING - TrackAdvisory AzElCoordinates validation FAILED !!!")
#        supportStr = "TrackAdvisory's AzElCoordinates validation FAILED !!!"
#        SendErrorResponse(self,tid,ERR_REASON_UNKNOWN_ERROR, supportStr) 

    # Get the end time in the track advisory request message in UTC second format(last element in the coordinates[] array)
    # UTC End Time in Seconds = GPS_Week * (7*24*60*60) + GPS_Second + 315964800 (fixed offset b/t GPS and UTC) - UTC offset (configurable)
    lastCoordIndex = len(trackAdvisoryCoordinatesList) - 1

    # Time difference between the next to last and the last coordinates 
    timeDiff = (trackAdvisoryCoordinatesList[lastCoordIndex].gpsArrivalTimeMicroSec -  \
               trackAdvisoryCoordinatesList[lastCoordIndex - 1].gpsArrivalTimeMicroSec) / MICROSECONDS_IN_SECOND

    trackIDInfoObj.endTime = (trackAdvisoryCoordinatesList[lastCoordIndex].gpsArrivalTimeWeek * SECONDS_IN_WEEK)            + \
                             (trackAdvisoryCoordinatesList[lastCoordIndex].gpsArrivalTimeMicroSec / MICROSECONDS_IN_SECOND) + \
                             GPS_UTC_OFFSET_IN_SECOND - self.AIMConfigObj.utcOffset + timeDiff                                                 

    #### LOCK
    self.threadLock.acquire()

    for index in range (len(self.ifPathList)) :
        if (self.ifPathList[index] == 0) :
            if_path_id = index
            self.ifPathList[index] = trackID
            trackIDInfoObj.ifPathID = if_path_id
            break
     
    # Store the data end time into a dictionary
    # Key: the track ID 
    # Value: the track ID Info
    self.trackIDDict[trackID] = trackIDInfoObj

    self.threadLock.release()
    #### UNLOCK

    # Construct and send track_advisory response message
    SendTrackAdvisoryResponseMsg(self, if_path_id, trackAdvisoryCoordinatesList, decoded_data)


####
#### This method is used to extract any necessary information from 
#### the track request msg
####   
def ProcessTrackMsg(self, decoded_data):
    tid     = decoded_data["header"]["tid"]
    trackID = decoded_data["body"]["track_id"]    

    SendDefaultResponse(self, decoded_data["header"]["message"], tid)

    if trackID not in self.trackIDDict :
        supportStr = "track_id from Track Request message is not in the trackIDDict. Discarding this track request msg"
        SendErrorResponse(self,tid,ERR_REASON_UNKNOWN_ERROR, supportStr)  
        return
    
    # Empty the Track Coordinates List when processing new track request message
    trackCoordinatesList = []
 
    for index in range (len(decoded_data["body"]["coordinates"])):
        # Add each track coordinates into the track coordinates list
        trackCoordinatesList.append(TrackCoordinates())
        trackCoordinatesList[index].azimuthDegree          = decoded_data["body"]["coordinates"][index]["azimuth_degree"]
        trackCoordinatesList[index].elevationDegree        = decoded_data["body"]["coordinates"][index]["elevation_degree"]
        trackCoordinatesList[index].gpsArrivalTimeWeek     = decoded_data["body"]["coordinates"][index]["gps_arrival_time_week"]
        trackCoordinatesList[index].gpsArrivalTimeMicroSec = decoded_data["body"]["coordinates"][index]["gps_arrival_time_us"]
        trackCoordinatesList[index].dwellTimeMilSec        = decoded_data["body"]["coordinates"][index]["dwell_time_ms"]

    # Validate track's Az/El coordinates
    if(self.AECObj.ValidateTrackCmdAzElCoordinates((trackID%65536), trackCoordinatesList) == False):
        Print("WARNING - Track msg AzElCoordinates validation FAILED !!!")
#        supportStr = "Track's AzElCoordinates validation FAILED !!!"
#        SendErrorResponse(self,tid,ERR_REASON_UNKNOWN_ERROR, supportStr) 


####
#### This method is used to extract any necessary information from 
#### the cancel_track request msg
####   
def ProcessCancelTrackMsg(self, decoded_data) :
    cancelTrackID = decoded_data["body"]["track_id"]
    
    #### LOCK
    self.threadLock.acquire()

    # Remove a track ID from trackID Dictionary
    if cancelTrackID in self.trackIDDict :
        self.trackIDDict.pop(cancelTrackID)

    # if the cancel track ID is inside the ifPathList, then
    #    set the value back to 0
    for index in range (len(self.ifPathList)):
        if (self.ifPathList[index] == cancelTrackID):
            self.ifPathList[index] = 0

    self.threadLock.release()
    #### UNLOCK

    # Remove the entry of given track ID from AEC map
    self.AECObj.NotifyEndOfContact(cancelTrackID)

    SendDefaultResponse(self, decoded_data["header"]["message"], decoded_data["header"]["tid"])


####
#### This method is used to extract any necessary information from 
#### the tune_rx_channel request msg
####   
def ProcessTuneRxChannelMsg(self, decoded_data):
    tid     = decoded_data["header"]["tid"]
    trackID = decoded_data["body"]["track_id"]
    
    SendDefaultResponse(self, decoded_data["header"]["message"], tid)

    if trackID not in self.trackIDDict :
        supportStr = "track_id from Tune Rx Channel Request message is not in the trackIDDict. Discarding the msg"
        SendErrorResponse(self,tid,ERR_REASON_UNKNOWN_ERROR, supportStr) 
        return

    #### LOCK
    self.threadLock.acquire()

    # Empty the List when processing new tune_rx_channel request message
    self.trackIDDict[trackID].rxChannelList = []

    for index in range (len(decoded_data["body"]["channels"])):
        # Add each channel into the rx channels list
        self.trackIDDict[trackID].rxChannelList.append(ChannelInfo()) 
        self.trackIDDict[trackID].rxChannelList[index].channelFreqHz             = decoded_data["body"]["channels"][index]["channel_freq_hz"]
        self.trackIDDict[trackID].rxChannelList[index].gpsActivationTimeWeek     = decoded_data["body"]["channels"][index]["gps_activation_time_week"]
        self.trackIDDict[trackID].rxChannelList[index].gpsActivationTimeMicroSec = decoded_data["body"]["channels"][index]["gps_activation_time_us"]
         
        freqInGhz = (self.trackIDDict[trackID].rxChannelList[index].channelFreqHz) / (GHZ_IN_HZ)        
        if ((freqInGhz >= 10.70) and (freqInGhz <= 12.70)):
            # Issue an invalid path SWITCH command to OCS
            SendSwitchCommand(self, freqInGhz, trackID, "RX", index, True)        
        else:
            Print("WARNING - Rx Channel Freq at index " + str(index) + " - " + str(freqInGhz) + \
                       " - is out of range (10.70 - 12.70 GHz)! Will not send SWITCH command to the OCS.")

    self.threadLock.release()
    #### UNLOCK

    SendGainUpdateNotification(self)

####
#### This method is used to extract any necessary information from 
#### the cancel_rx_tune request msg
####   
def ProcessCancelRxTuneMsg(self, decoded_data):
    tid     = decoded_data["header"]["tid"]
    trackID = decoded_data["body"]["track_id"]
    freqInGhz = 0  

    SendDefaultResponse(self, decoded_data["header"]["message"], decoded_data["header"]["tid"])

    if trackID not in self.trackIDDict :
        supportStr = "track_id from cancel_Rx_tune request message is not in the trackIDDict. Discarding the msg"
        SendErrorResponse(self,tid,ERR_REASON_UNKNOWN_ERROR, supportStr)   
        return

    # Check if the RX Channel List is empty or not
    if (len(self.trackIDDict[trackID].rxChannelList) > 0):
        freqInGhz = (self.trackIDDict[trackID].rxChannelList[0].channelFreqHz) / (GHZ_IN_HZ)        
        if ((freqInGhz < 10.70) or (freqInGhz > 12.70)):
            Print("WARNING - Rx Channel Freq at index 0 - " + str(freqInGhz) + \
                       " - is out of range (10.70 - 12.70 GHz)! Will not send SWITCH command to the OCS.")
            return

    # Issue an invalid path SWITCH command to OCS
    SendSwitchCommand(self, freqInGhz, trackID, "RX", 0, False)

####
#### This method is used to extract any necessary informatin from 
#### the tune_tx_channel request msg
####   
def ProcessTuneTxChannelMsg(self, decoded_data):
    tid     = decoded_data["header"]["tid"]
    trackID = decoded_data["body"]["track_id"]

    SendDefaultResponse(self, decoded_data["header"]["message"], tid)

    if trackID not in self.trackIDDict :
        supportStr =  "track_id from Tune Tx Channel Request message is not in the trackIDDict. Discarding the msg"
        SendErrorResponse(self,tid,ERR_REASON_UNKNOWN_ERROR, supportStr) 
        return

    #### LOCK
    self.threadLock.acquire()
    
    self.trackIDDict[trackID].txChannelObj.channelFreqHz             = decoded_data["body"]["channel_freq_hz"]
    self.trackIDDict[trackID].txChannelObj.gpsActivationTimeWeek     = decoded_data["body"]["gps_activation_time_week"]
    self.trackIDDict[trackID].txChannelObj.gpsActivationTimeMicroSec = decoded_data["body"]["gps_activation_time_us"]

    freqInGhz = (self.trackIDDict[trackID].txChannelObj.channelFreqHz) / (GHZ_IN_HZ)

    CalculateSecondaryTxFreqs(self, freqInGhz, trackID)

    self.threadLock.release()
    #### UNLOCK
    
    SendGainUpdateNotification(self)

    if ((freqInGhz < 14.000) or (freqInGhz > 14.500)):        
        Print("WARNING - Tx Channel Freq - " + str(freqInGhz) + \
                   " - is out of range (14.000 - 14.500 GHz)! Will not send SWITCH command to the OCS.")
        return 

    # Issue a path SWITCH command to OCS
    SendSwitchCommand(self, freqInGhz, trackID, "TX", 0, True)

def CalculateSecondaryTxFreqs(self, txFreqInGhz, trackID):
    # 19.8 MHz =  0.0198 GHz 
    lowerSecondaryTxFreqGHz = txFreqInGhz - 0.0198 
    upperSecondaryTxFreqGHz = txFreqInGhz + 0.0198 
    
    # Convert back to Hz 
    lowerSecondaryTxFreqHz = long(lowerSecondaryTxFreqGHz * GHZ_IN_HZ)
    upperSecondaryTxFreqHz = long(upperSecondaryTxFreqGHz * GHZ_IN_HZ)
    txFreqInHz             = long(txFreqInGhz * GHZ_IN_HZ)

    txChannelNum = GetTxChannel(txFreqInGhz)
    
    # Clear the TX frequency list 
    self.trackIDDict[trackID].txFreqList = []

    if (txChannelNum == 1) :
        if ( lowerSecondaryTxFreqGHz >= 14.000) :
            self.trackIDDict[trackID].txFreqList.append(lowerSecondaryTxFreqHz)

        self.trackIDDict[trackID].txFreqList.append(txFreqInHz)

        if (upperSecondaryTxFreqGHz <= 14.125):    
            self.trackIDDict[trackID].txFreqList.append(upperSecondaryTxFreqHz)

    elif (txChannelNum == 2) :
        if (lowerSecondaryTxFreqGHz > 14.125) :
            self.trackIDDict[trackID].txFreqList.append(lowerSecondaryTxFreqHz)

        self.trackIDDict[trackID].txFreqList.append(txFreqInHz)

        if (upperSecondaryTxFreqGHz <= 14.250):
            self.trackIDDict[trackID].txFreqList.append(upperSecondaryTxFreqHz)
     
    elif (txChannelNum == 3) :
        if (lowerSecondaryTxFreqGHz > 14.250) :
            self.trackIDDict[trackID].txFreqList.append(lowerSecondaryTxFreqHz)

        self.trackIDDict[trackID].txFreqList.append(txFreqInHz)

        if (upperSecondaryTxFreqGHz <= 14.375):
            self.trackIDDict[trackID].txFreqList.append(upperSecondaryTxFreqHz)

    elif (txChannelNum == 4) :
        if (lowerSecondaryTxFreqGHz > 14.375) :
            self.trackIDDict[trackID].txFreqList.append(lowerSecondaryTxFreqHz)

        self.trackIDDict[trackID].txFreqList.append(txFreqInHz)

        if (upperSecondaryTxFreqGHz <= 14.500):
            self.trackIDDict[trackID].txFreqList.append(upperSecondaryTxFreqHz)
    else : 
        Print ("WARNING - TX frequency (" + str(txFreqInGhz) + ") is OUT OF RANGE!!! (14.000 - 14.500 GHz)")


####
#### This method is used to extract any necessary information from 
#### the gain_update_control request msg
####   
def ProcessGainUpdateControlMsg(self, decoded_data):
    self.sendGainUpdates = decoded_data["body"]["send_gain_updates"]
    Print("Send Gain Updates - " + str(self.sendGainUpdates))

    if (self.gainUpdateIntervalMilliseconds != decoded_data["body"]["gain_update_interval_ms"]):
        Print("Gain Update Interval (in ms) changed from " + str(self.gainUpdateIntervalMilliseconds) + \
                                       " to " + str(decoded_data["body"]["gain_update_interval_ms"]))
        self.gainUpdateIntervalMilliseconds = decoded_data["body"]["gain_update_interval_ms"]

    SendDefaultResponse(self, decoded_data["header"]["message"], decoded_data["header"]["tid"])

####
#### This method is used to extract any necessary information from
#### the true_north_set request msg
####    
def ProcessTrueNorthSetMsg(self, decoded_data):
    tid     = decoded_data["header"]["tid"]
    ifPathID   = decoded_data["body"]["if_path_id"]

    SendDefaultResponse(self, decoded_data["header"]["message"], tid)

    if (ifPathID >= self.AIMConfigObj.numOfIfPath):
        supportStr =  "Invalid if_path_id number. Discarding the msg"
        SendErrorResponse(self,tid,ERR_REASON_UNKNOWN_ERROR, supportStr)
        return
    
    # Extract azimuth correction value in degrees  
    if (self.ifPathIDInfoList[ifPathID].azimuthCorrection != decoded_data["body"]["azimuth_correction"]):
        Print("Azimuth Correction changes from " + self.ifPathIDInfoList[ifPathID].azimuthCorrection + \
              " to " + decoded_data["body"]["azimuth_correction"] + " for IF Path ID " + str(ifPathID))
        self.ifPathIDInfoList[ifPathID].azimuthCorrection  = decoded_data["body"]["azimuth_correction"]
    
    # Extract elevation correction value in degrees
    if (self.ifPathIDInfoList[ifPathID].elevationCorrection != decoded_data["body"]["elevation_correction"]):
        Print("Elevation Correction changes from " + self.ifPathIDInfoList[ifPathID].elevationCorrection + \
              " to " + decoded_data["body"]["elevation_correction"] + " for IF Path ID " + str(ifPathID))
        self.ifPathIDInfoList[ifPathID].elevationCorrection = decoded_data["body"]["elevation_correction"]

####
#### This method is used to extract any necessary information from
#### the blockage_set request msg
####
def ProcessBlockageSetMsg(self, decoded_data):

    SendDefaultResponse(self, decoded_data["header"]["message"], decoded_data["header"]["tid"])
    
    for index in range(len(decoded_data["body"]["regions"])):
        ifPathID = decoded_data["body"]["regions"][index]["if_path_id"]

        if (ifPathID >= self.AIMConfigObj.numOfIfPath):
            Print("WARNING - Invalid IF Path ID in Blockage Set request message at entry # " + str(index))
            continue
   
        # Extract minimum azimuth value of the blockage zone in degrees
        if (self.ifPathIDInfoList[ifPathID].azimuthMinDegree != decoded_data["body"]["regions"][index]["azimuth_min_degree"]):
            Print("Azimuth Min Degree changes from " + self.ifPathIDInfoList[ifPathID].azimuthMinDegree + \
                  " to " + decoded_data["body"]["regions"][index]["azimuth_min_degree"] + " for IF Path ID " + str(ifPathID))
            self.ifPathIDInfoList[ifPathID].azimuthMinDegree  = decoded_data["body"]["regions"][index]["azimuth_min_degree"]
    
        # Extract maximum azimuth value of the blockage zone in degrees
        if (self.ifPathIDInfoList[ifPathID].azimuthMaxDegree != decoded_data["body"]["regions"][index]["azimuth_max_degree"]):
            Print("Azimuth Max Degree changes from " + self.ifPathIDInfoList[ifPathID].azimuthMaxDegree + \
                  " to " + decoded_data["body"]["regions"][index]["azimuth_max_degree"] + " for IF Path ID " + str(ifPathID))
            self.ifPathIDInfoList[ifPathID].azimuthMaxDegree  = decoded_data["body"]["regions"][index]["azimuth_max_degree"]
    
        # Extract minimum elevation value of the blockage zone in degrees
        if (self.ifPathIDInfoList[ifPathID].elevationMinDegree != decoded_data["body"]["regions"][index]["elevation_min_degree"]):
            Print("Elevation Min Degree changes from " + self.ifPathIDInfoList[ifPathID].elevationMinDegree + \
                  " to " + decoded_data["body"]["regions"][index]["elevation_min_degree"] + " for IF Path ID " + str(ifPathID))
            self.ifPathIDInfoList[ifPathID].elevationMinDegree  = decoded_data["body"]["regions"][index]["elevation_min_degree"]
    
        # Extract maximum elevation value of the blockage zone in degrees
        if (self.ifPathIDInfoList[ifPathID].elevationMaxDegree != decoded_data["body"]["regions"][index]["elevation_max_degree"]):
            Print("Elevation Max Degree changes from " + self.ifPathIDInfoList[ifPathID].elevationMaxDegree + \
                  " to " + decoded_data["body"]["regions"][index]["elevation_max_degree"] + " for IF Path ID " + str(ifPathID))
            self.ifPathIDInfoList[ifPathID].elevationMaxDegree  = decoded_data["body"]["regions"][index]["elevation_max_degree"]


####
#### This method is used to extract any necessary information from 
#### the timestamp_header request msg
####   
def ProcessTimestampHeaderMsg(self, decoded_data):
    if (self.includeTimestamp != decoded_data["body"]["include_timestamp"]):
        Print("IncludeTimestamp changes from " + str(self.includeTimestamp) + " to " + str(decoded_data["body"]["include_timestamp"]))
        self.includeTimestamp = decoded_data["body"]["include_timestamp"]

    SendDefaultResponse(self, decoded_data["header"]["message"], decoded_data["header"]["tid"])

####
#### This method is used to construct a default response.
#### Apply to any request message which does not have a specific response message
####
def SendDefaultResponse(self, message, tid) :
    header = self.ConstructHeader(message, tid)

    body = "\"body\":{}}"

    response = header + body

    self.SendData(self.txAddress, response)

####
#### This method is used to construct the gain_update notification msg
####
def SendGainUpdateNotification(self):
    
    headerMsg = self.ConstructHeader("gain_update", self.GetTID())

    rxTransitionStr = "\"body\": {\"rx\": ["
 
    #### LOCK
    self.threadLock.acquire()

    # Construct RX message
    rxMsg = ""       
    isFirstTrackIDWithData = True
    for trackID in self.trackIDDict :

        # If the length of the Rx Channels array (in tune_rx_channel msg) is more than 
        # the maximum number of RX channel (in the config file) which we want to send, 
        # then use the max number in the config file as the length to contruct the gain info object for RX 
        if (self.AIMConfigObj.gainUpdateMaxChannels == 99 or     \
            len(self.trackIDDict[trackID].rxChannelList) < self.AIMConfigObj.gainUpdateMaxChannels):
            rxGainInfoLength = len(self.trackIDDict[trackID].rxChannelList)
        else:
            rxGainInfoLength = self.AIMConfigObj.gainUpdateMaxChannels

        # If The rxChannelList is empty, we are not going to append the "," to the rx string
        if ((isFirstTrackIDWithData == False) and (len(self.trackIDDict[trackID].rxChannelList) != 0)):
            rxMsg = rxMsg + ","
        
        for i in range (rxGainInfoLength):

            rxMsg = rxMsg + "{\"track_id\": " + str(trackID)                                                                         \
                          + ",\"channel_freq_hz\": " + str(self.trackIDDict[trackID].rxChannelList[i].channelFreqHz)                 \
                          + ",\"is_valid\": true"                                                                                    \
                          + ",\"gain_dB\": \"" + GetRxgaindBValue(self, str(self.trackIDDict[trackID].rxChannelList[i].channelFreqHz)) + "\""\
                          + ",\"gps_time_week\": "   + str(self.trackIDDict[trackID].rxChannelList[i].gpsActivationTimeWeek)         \
                          + ",\"gps_time_us\": "     + str(self.trackIDDict[trackID].rxChannelList[i].gpsActivationTimeMicroSec) + "}"

            isFirstTrackIDWithData = False

            if (i < rxGainInfoLength-1):
                rxMsg = rxMsg + ","
         
    txTransitionStr = "], \"tx\": ["

    # Construct TX message
    txMsg = ""
    isFirstTrackIDWithData = True
    for trackID in self.trackIDDict :
        # Notes:
        #     When the TX channel's frequency of a particular track_ID is 0, we are considering that TX channel object as empty.
        #     Hence, we will not construct the tx message for that TX channel object 
        if (self.trackIDDict[trackID].txChannelObj.channelFreqHz != 0):

            if (isFirstTrackIDWithData == False):
                txMsg = txMsg + ","
            
            for i in range (len(self.trackIDDict[trackID].txFreqList)):

                txMsg = txMsg + "{\"track_id\": " + str(trackID)                                                                     \
                              + ",\"channel_freq_hz\": " + str(self.trackIDDict[trackID].txFreqList[i])                              \
                              + ",\"is_valid\": true"                                                                                \
                              + ",\"gain_dB\": \"" + GetTxgaindBValue(self, str(self.trackIDDict[trackID].txFreqList[i]))      + "\""\
                              + ",\"gps_time_week\": "   + str(self.trackIDDict[trackID].txChannelObj.gpsActivationTimeWeek)         \
                              + ",\"gps_time_us\": "     + str(self.trackIDDict[trackID].txChannelObj.gpsActivationTimeMicroSec) + "}"
                isFirstTrackIDWithData = False

                if (i < len(self.trackIDDict[trackID].txFreqList)-1):
                    txMsg = txMsg + ","

    txPmaxTransitionStr = "], \"tx_pmax\": ["

    # Construct TX Pmax message
    txPmaxMsg = ""
    isFirstTrackIDWithData = True
    for trackID in self.trackIDDict :
        # Notes:
        #     When the TX channel's frequency of a particular track_ID is 0, we are considering that TX channel object as empty.
        #     Hence, we will not construct the tx pmax message for that TX channel object 
        if (self.trackIDDict[trackID].txChannelObj.channelFreqHz != 0):

            if (isFirstTrackIDWithData == False):
                txPmaxMsg = txPmaxMsg + ","
            
            for i in range (len(self.trackIDDict[trackID].txFreqList)):

                txPmaxMsg = txPmaxMsg + "{\"track_id\": " + str(trackID)                                                                     \
                                      + ",\"channel_freq_hz\": " + str(self.trackIDDict[trackID].txFreqList[i])                              \
                                      + ",\"is_valid\": true"                                                                                \
                                      + ",\"pmax_dB\": \"" + GetTxgaindBValue(self, str(self.trackIDDict[trackID].txFreqList[i]))      + "\""\
                                      + ",\"gps_time_week\": "   + str(self.trackIDDict[trackID].txChannelObj.gpsActivationTimeWeek)         \
                                      + ",\"gps_time_us\": "     + str(self.trackIDDict[trackID].txChannelObj.gpsActivationTimeMicroSec) + "}"       
                isFirstTrackIDWithData = False
    
                if (i < len(self.trackIDDict[trackID].txFreqList)-1):
                    txPmaxMsg = txPmaxMsg + ","

    endStr = "]}}"
    
    gainUpdateNotifMsg = headerMsg + rxTransitionStr + rxMsg + txTransitionStr + txMsg + txPmaxTransitionStr + txPmaxMsg + endStr
    
    self.SendData(self.txAddress, gainUpdateNotifMsg, "gain_update")

    self.threadLock.release()
    #### UNLOCK

####
#### This method is used to construct and send the error response msg
####   
def SendErrorResponse(self, tid, errReason, supportStr):
 
    header = "{\"header\": {\"type\": \"notification\", \"message\": \"error\", \"tid\":" + str(tid)+ "},"

    body = "\"body\": { \"error_reason\": "    + str(errReason)  + ", "   + \
                       "\"error_message\": \""   + supportStr    + "\", " + \
                       "\"error_tid\": "       + str(tid)        + ", "   + \
                       "\"advanced_error_message\": \"\""        + "}}"

    response = header + body
   
    self.SendData(self.txAddress, response)


####
#### This method is used to construct and send the track_advisory response msg
####   
def SendTrackAdvisoryResponseMsg(self, if_path_id, trackAdvisoryCoordinatesList, decoded_data):
    response = ""
    expect_blockage = "false"         

    # To calculate alignment_time_gps in microsecond,
    #      - take the gps arrival time in mircro secconds and add 100 milliseconds
    # if the alignment_time_gps in microsecond is greater than the number of microseconds in a week
    #      - then increase the alignment_time_gps in week to 1
    #      - the new alignment_time_gps in microsecond will be the remainder between
    #              the just calculated "alignment_time_gps_us" and the number of microseconds in a week
    alignment_time_gps_us   = trackAdvisoryCoordinatesList[0].gpsArrivalTimeMicroSec + 100000
    alignment_time_gps_week = trackAdvisoryCoordinatesList[0].gpsArrivalTimeWeek
    
    if (alignment_time_gps_us >= SECONDS_IN_WEEK*1000000):
        alignment_time_gps_week = alignment_time_gps_week + 1
        alignment_time_gps_us = alignment_time_gps_us % (SECONDS_IN_WEEK*1000000)
    
    header =  self.ConstructHeader(decoded_data["header"]["message"], decoded_data["header"]["tid"])
    
    body = "\"body\": { \"track_id\": "                + str(decoded_data["body"]["track_id"]) + ", " + \
                       "\"if_path_id\": "              + str(if_path_id)                       + ", " + \
                       "\"expected_blockage\": "       + (expect_blockage)                     + ", " + \
                       "\"alignment_time_gps_week\": " + str(alignment_time_gps_week)          + ", " + \
                       "\"alignment_time_gps_us\": "   + str(alignment_time_gps_us)            + "}}" 

    response = header + body
    self.SendData(self.txAddress, response)


####        
#### This method is used to construct and send the Forward Channel Status Control Request message
####
def SendFwdChannelStatusCtrReq(self) :

    msgName = "request_forward_channel_status_control" 

    header = "{\"header\": {\"type\": \"request\", \"message\": \"forward_channel_status_control\", \"tid\":" + str(self.GetTID()) + "},"

    if (self.fwdChannelSinrAvailable == False) :
        body = "\"body\": { \"send_forward_channel_status\": false}}"
    elif (self.fwdChannelSinrAvailable == True) :
        body = "\"body\": { \"send_forward_channel_status\": true}}"
    
    response = header + body

    self.SendData(self.txAddress, response)


####
#### This method is used to construct and send the system_info response msg
####   
def SendSystemInfoResponseMsg(self, msgName, tid):
    header = self.ConstructHeader(msgName, tid)

    body = "\"body\": { \"vendor\": \""                   + self.AIMConfigObj.vendor                      + "\", "  + \
                       "\"model\": \""                    + self.AIMConfigObj.model                       + "\", "  + \
                       "\"ut_classification\": \""        + self.AIMConfigObj.utClassification            + "\", "  + \
                       "\"serial_number\": \""            + self.AIMConfigObj.serialNum                   + "\", "  + \
                       "\"fw_version_current\": \""       + self.AIMConfigObj.fwVerCurrent                + "\", "  + \
                       "\"fw_version_factory\": \""       + self.AIMConfigObj.fwVerFactory                + "\", "  + \
                       "\"intra_handover_outage_ms\": "   + str(self.AIMConfigObj.intraHandoverOutageMs)  + ", "    + \
                       "\"inter_handover_outage_ms\": "   + str(self.AIMConfigObj.interHandoverOutageMs)  + ", "    + \
                       "\"time_to_next_satellite_ms\": "  + str(self.AIMConfigObj.timeToNextSatMs)        + ", "    + \
                       "\"time_to_move_one_degree_us\": " + str(self.AIMConfigObj.timeToMoveOneDegreeUs)  + ", "    + \
                       "\"min_elevation_angle\": \""      + self.AIMConfigObj.minElevationAngle           + "\", "  + \
                       "\"num_if_paths\":"                + str(self.AIMConfigObj.numOfIfPath)            + ", "    + \
                       "\"is_stationary\": "              + self.AIMConfigObj.isStationary                + ", "    + \
                       "\"is_oriented\": "                + self.AIMConfigObj.isOriented                  + ", "    + \
                       "\"is_true_north_calibrated\": "   + self.AIMConfigObj.isTrueNorthCalibrated       + ", "    + \
                       "\"is_rl_dual_carrier_capable\": " + self.AIMConfigObj.isRLDualCarrierCapable      + ", "    + \
                       "\"is_full_duplex\": "             + self.AIMConfigObj.isFullDuplex + ", "
    
    # Construct True North Azimuth Correction object
    trueNorthAZCorrection = "\"true_north_azimuth_correction\": ["
    for index in range(self.AIMConfigObj.numOfIfPath):
        trueNorthAZCorrection = trueNorthAZCorrection + "{\"if_path_id\": " + str(index) + "," + \
                                                        "\"azimuth_correction\": \"" + self.ifPathIDInfoList[index].azimuthCorrection + "\"}" 
        if (index < self.AIMConfigObj.numOfIfPath-1):
            trueNorthAZCorrection = trueNorthAZCorrection + ","

    # Construct TX Delays object
    txDelays = "],\"tx_delays\": ["
    for index in range(self.AIMConfigObj.numOfIfPath):
        txDelays = txDelays + "{\"if_path_id\": " + str(index) + "," + \
                              "\"delay_ns\": " + str(self.ifPathIDInfoList[index].txDelaysInNs) + "}"
        if (index < self.AIMConfigObj.numOfIfPath-1):
            txDelays = txDelays + ","

    # Construct RX Delays object
    rxDelays = "],\"rx_delays\": ["
    for index in range(self.AIMConfigObj.numOfIfPath):
        rxDelays = rxDelays + "{\"if_path_id\": " + str(index) + "," + \
                              "\"delay_ns\": " + str(self.ifPathIDInfoList[index].rxDelaysInNs) + "}"
        if (index < self.AIMConfigObj.numOfIfPath-1):
            rxDelays = rxDelays + ","

    end = "]}}"

    response = header + body + trueNorthAZCorrection + txDelays + rxDelays + end
    self.SendData(self.txAddress, response)

####
#### This method is used to construct and send the system_status response msg
####   
def SendSystemStatusResponseMsg(self, msgName, tid):
    header = self.ConstructHeader(msgName, tid)

    body = "\"body\": { \"status\": \"good\", "         + \
                       "\"1pps_gps_time_week\": 947, "  + \
                       "\"1pps_gps_time_us\": 326296}}"  
    response = header + body
    self.SendData(self.txAddress, response)
 
####
#### This method is used to construct and send the sensor_information response msg
####   
def SendSensorInfoResponseMsg(self, msgName, tid):    
    header = self.ConstructHeader(msgName, tid)

    body = "\"body\": { \"sensor\": ["                       
    
    sensorArray = ""
    for index in range(self.AIMConfigObj.numOfIfPath):
        sensorArray = sensorArray + "{\"if_path_id\": " + str(index) + "," + \
                                     "\"tilt_pitch_degrees\": \""    + self.ifPathIDInfoList[index].tiltPitchDegrees    + "\"," + \
                                     "\"tilt_roll_degrees\": \""     + self.ifPathIDInfoList[index].tiltRollDegrees     + "\"," + \
                                     "\"temperature_degrees_c\": \"" + self.ifPathIDInfoList[index].temperatureDegreesC + "\"}" 
        if (index < self.AIMConfigObj.numOfIfPath-1):
            sensorArray = sensorArray + ","

    end = "]}}"

    response = header + body + sensorArray + end
    self.SendData(self.txAddress, response) 

####
#### This method is used to construct and send the run_diagnostic_test response msg
####   
def SendRunDiagnosticTestResponseMsg(self, msgName, tid):
    header = self.ConstructHeader(msgName, tid)

    body = "\"body\": { \"test_result\": \"skipped\", "     + \
                       "\"test_result_code\": 0, "          + \
                       "\"test_result_message\": \"N/A\", " + \
                       "\"test_details\": []}}"
    response = header + body
    self.SendData(self.txAddress, response) 


####
#### This method is used to construct and send the api_version_info response msg
####   
def SendApiVersionInfoResponseMsg(self, msgName, tid):
    header = self.ConstructHeader(msgName, tid)

    body = "\"body\": { \"aim_api_version\": \"1.10\"}}"

    response = header + body
    self.SendData(self.txAddress, response)


####
#### This method is used to construct and send the post_results response msg
####   
def SendPostResultsResponseMsg(self, msgName, tid): 
    header = self.ConstructHeader(msgName, tid)

    body = "\"body\": { \"post_result\": \"not run\", " + \
                       "\"post_info\": []}}"
    response = header + body
    self.SendData(self.txAddress, response)


####
#### This method is used to send a switch command to the OCS
####
def SendSwitchCommand(self, freqInGhz, trackID, IFType, index, isRxOrTx):
    ifPathID     = self.trackIDDict[trackID].ifPathID    
    channelNum   = 0
    weekNum      = 0
    secondOfWeek = 0
    microSeconds = 0

    if (isRxOrTx == False):
        curUTCTimeInSec = int(time.time())
        curGPSTimeInSec = curUTCTimeInSec - GPS_UTC_OFFSET_IN_SECOND + self.AIMConfigObj.utcOffset
        channelNum   = GetRxChannel(freqInGhz)
        trackID      = 0     # send the track ID as 0 to indicate cancel_rx_tune
        weekNum      = int(curGPSTimeInSec / SECONDS_IN_WEEK)
        secondOfWeek = int(curGPSTimeInSec % SECONDS_IN_WEEK)
        microSeconds = 0
    else:
        if (IFType == "RX"):
            channelNum   = GetRxChannel(freqInGhz)
            weekNum      = self.trackIDDict[trackID].rxChannelList[index].gpsActivationTimeWeek
            secondOfWeek = int(self.trackIDDict[trackID].rxChannelList[index].gpsActivationTimeMicroSec / MICROSECONDS_IN_SECOND)
            microSeconds = int(self.trackIDDict[trackID].rxChannelList[index].gpsActivationTimeMicroSec % MICROSECONDS_IN_SECOND)

        else :
            channelNum   = GetTxChannel(freqInGhz)
            weekNum      = self.trackIDDict[trackID].txChannelObj.gpsActivationTimeWeek
            secondOfWeek = int(self.trackIDDict[trackID].txChannelObj.gpsActivationTimeMicroSec / MICROSECONDS_IN_SECOND)
            microSeconds = int(self.trackIDDict[trackID].txChannelObj.gpsActivationTimeMicroSec % MICROSECONDS_IN_SECOND)
    
    # Derive UT number for OCS
    utNum = self.AIMConfigObj.utNum * self.AIMConfigObj.numOfIfPath + ifPathID

    switchCmd = "SWITCH," + str(utNum)                              + "," \
                          + str(ifPathID)                           + "," \
                          + IFType                                  + "," \
                          + str(trackID%65536)                      + "," \
                          + str(channelNum)                         + "," \
                          + str(weekNum)                            + "," \
                          + str(secondOfWeek)                       + "," \
                          + str(microSeconds)

    self.SendData((self.AIMConfigObj.ocsIPAddr, self.AIMConfigObj.ocsRxPort), switchCmd)


####
#### This method is used to get the Rx channel number 
####
def GetRxChannel(freqInGhz):
    if  (freqInGhz >= 10.70 and freqInGhz <= 10.95):
        return 1
    elif (freqInGhz > 10.95 and freqInGhz <= 11.20):
        return 2
    elif (freqInGhz > 11.20 and freqInGhz <= 11.45):
        return 3
    elif (freqInGhz > 11.45 and freqInGhz <= 11.70):
        return 4
    elif (freqInGhz > 11.70 and freqInGhz <= 11.95):
        return 5
    elif (freqInGhz > 11.95 and freqInGhz <= 12.20):
        return 6
    elif (freqInGhz > 12.20 and freqInGhz <= 12.45):
        return 7
    elif (freqInGhz > 12.45 and freqInGhz <= 12.70):
        return 8
    else :
        return 0

####
#### This method is used to get the Tx channel number
####
def GetTxChannel(freqInGhz):
    if  (freqInGhz >= 14.000 and freqInGhz <= 14.125):
        return 1
    elif (freqInGhz > 14.125 and freqInGhz <= 14.250):
        return 2
    elif (freqInGhz > 14.250 and freqInGhz <= 14.375):
        return 3
    elif (freqInGhz > 14.375 and freqInGhz <= 14.500):
        return 4
    else :
        return 0

####
#### This method is used to get the Rx gaindB value based on the give frequency in Hz
#### Return: gaindB value in string format
####
def GetRxgaindBValue(self, freqInHz):
    if freqInHz not in self.rxFreqToGainDict :
        return "640"

    return self.rxFreqToGainDict[freqInHz]

####
#### This method is used to get the Tx gaindB value based on the give frequency in Hz
#### Return: gaindB value in string format
####
def GetTxgaindBValue(self, freqInHz):
    if freqInHz not in self.txFreqToGainDict :
        return "390"

    return self.txFreqToGainDict[freqInHz]


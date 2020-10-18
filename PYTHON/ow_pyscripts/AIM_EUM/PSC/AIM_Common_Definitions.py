#!/usr/bin/env python

##########################################################################################
# PURPOSE:
#
# SOURCE CODE FILE: AIM_Common_Definitions.py
#
# REVISION HISTORY:
# DATE:           AUTHOR:         CHANGE:
# 12-03-18        Thanh Le        Initial Version
# 02-04-19        Thanh Le        Replaced enum errorReasons with constant values
#                                 (Enum is not supported in 2.7 version)
#                                 Handle "response" and "fault" msg type
# 02-19-19        Thanh Le        Moved Print() from AIM_Emulator.py to AIM_Common_Definitions.py
# 05-22-19        Thanh Le        SPR 81682 - Sync up with OW_SSM_Antenna ICD ver. 1.10
# 05-31-19        Thanh Le        SPR 81767 - Gain Update Enhancement
# 06-04-19        Thanh Le        SPR 81702 - AIME enhancements
# 06-11-19        Thanh Le        SPR 81808 - System Info message enhancement
# 07-18-19        Thanh Le        SPR 82098 - Support for Static mode in AIME
#
# Copyright 2017 Hughes Network Systems Inc
##########################################################################################

from __future__ import division        # need for division in Python 2.7 version
import datetime                        # need for getting current time in readable format
import time                            # need for getting current time in second format
import json                            # need for serializing/deserializing json string

MILLISECONDS_IN_SECOND   = 1000       
MICROSECONDS_IN_SECOND   = 1000000
SECONDS_IN_WEEK          = 604800 
GPS_UTC_OFFSET_IN_SECOND = 315964800
GHZ_IN_HZ                = 1000000000.0
                           
# Constant values for ErrorReasons
ERR_REASON_UNAVAILABLE      = 0
ERR_REASON_MSG_TYPE_UNKNOWN = 1
ERR_REASON_REQ_TYPE_UNKNOWN = 2
ERR_REASON_API_INCOMPATIBLE = 3
ERR_REASON_INVALID_JSON     = 4
ERR_REASON_INVALID_FORMAT   = 5
ERR_REASON_UNKNOWN_ERROR    = 6


class AIMConfig:
    def __init__(self):

        #### Variables from configuration file
        self.ssmIPAddr = "127.0.0.1"               # SSM IP Address
        self.ocsIPAddr = "127.0.0.1"               # OCS IP Address
        self.aimRxPort = 57070                     # port # in which AIM Emulator will listen to
                                                   #    for receiving msgs from SSM Simulator
        self.ssmRxPort = 57071                     # port # in which SSM Simulator will listen to
                                                   #    for receiving msgs from AIM Emulator
        self.ocsRxPort = 57072                     # port # in which OCS Simulator will listen to
                                                   #    for receiving msgs from AIM Emulator
        self.utNum = 1                             # UT number
        self.numOfIfPath = 2                       # number of IF path
        self.utcOffset = 18                        # UTC offset (leap seconds)
        self.trkAdvCoordTolerance = 0.1            # Track_Advisory coordinates tolerance
        self.trkCoordTolerance = 0.1               # Track coordinates tolerance
        self.utPosLat = 0                          # Position of the UT (Latitude)
        self.utPosLon = 0                          # Position of the UT (Longtitude)
        self.utPosAlt = 0                          # Position of the UT (Altitude)
        self.sedfFilePath  = "/home/msat/SEDFs"    # SEDF files' directory
        self.gainUpdateMaxChannels = 99            # Maximum channels of gain info object for Tune Rx
        self.printGainUpdateMsg = True             # whether user wants to display GainUpdate
                                                   # msg in the log file or not
        self.printFwdChannelStatusMsg = True       # whether user wants to display Forward Channel Status
                                                   # msg in the log file or not
        self.aimeMode = "DYNAMIC"                  # AIME running mode 

        #### Variables from System Info
        self.vendor = "Intellian"
        self.model = "AT100R"
        self.utClassification = "ENT-12P"
        self.serialNum = "I5600A2890"
        self.fwVerCurrent = "2.1"
        self.fwVerFactory = "1.3"
        self.intraHandoverOutageMs = 1
        self.interHandoverOutageMs = 1
        self.timeToNextSatMs = 5000
        self.timeToMoveOneDegreeUs = 1
        self.minElevationAngle = "30"
        self.isStationary = "true"
        self.isOriented = "true"
        self.isTrueNorthCalibrated = "true"
        self.isFullDuplex = "true"
        self.isRLDualCarrierCapable = "true"


class SSMNotifications:
    def __init__(self):

        # Satellite Network Switch
        self.networkType = ""
        self.switchTimestamp = ""

        # DRX Wakeup Time
        self.gpsTimeWeek = 0
        self.gpsTimeMicroSec = 0


class TrackAdvisoryCoordinates:
    def __init__(self):
        self.azimuthDegree = ""
        self.elevationDegree = ""
        self.gpsArrivalTimeWeek = 0
        self.gpsArrivalTimeMicroSec = 0


class TrackCoordinates:
    def __init__(self):
        self.azimuthDegree = ""
        self.elevationDegree = ""
        self.gpsArrivalTimeWeek = 0
        self.gpsArrivalTimeMicroSec = 0
        self.dwellTimeMilSec = 0


class TrackIDInfo:
    def __init__(self):
        self.startTime = 0
        self.endTime = 0
        self.ifPathID = 0
        self.rxChannelList = []
        self.txChannelObj = ChannelInfo()
        self.txFreqList = []

class ChannelInfo:
    def __init__(self):
        self.channelFreqHz = 0
        self.gpsActivationTimeWeek = 0
        self.gpsActivationTimeMicroSec = 0


class IFPathIDInfo:
    def __init__(self):
        self.txDelaysInNs        = 0              # for 'system_info' response message
        self.rxDelaysInNs        = 0              # for 'system_info' response message
        self.azimuthCorrection   = "0"            # in 'true_north_set' request message
        self.elevationCorrection = "0"            # in 'true_north_set' request message
        self.azimuthMinDegree    = "0"            # in 'blockage_set' request message
        self.azimuthMaxDegree    = "0"            # in 'blockage_set' request message
        self.elevationMinDegree  = "0"            # in 'blockage_set' request message
        self.elevationMaxDegree  = "0"            # in 'blockage_set' request message
        self.tiltPitchDegrees    = "0"            # for 'sensor_information' response message
        self.tiltRollDegrees     = "0"            # for 'sensor_information' response message
        self.temperatureDegreesC = "0"            # for 'sensor_information' response message
        
def Print(printStatement):
    print datetime.datetime.now(), printStatement

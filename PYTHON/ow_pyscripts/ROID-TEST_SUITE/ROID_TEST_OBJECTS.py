#!/usr/bin/env python

from __future__ import division        # need for division in Python 2.7 version
import datetime                        # need for getting current time in readable format
import time                            # need for getting current time in second format
import json                            # need for serializing/deserializing json string

MILLISECONDS_IN_SECOND   = 1000       
MICROSECONDS_IN_SECOND   = 1000000
SECONDS_IN_WEEK          = 604800 
GPS_UTC_OFFSET_IN_SECOND = 315964800
HZ_IN_GHZ                = 1000000000.0
                           
# Constant values for ErrorReasons
ERR_REASON_UNAVAILABLE      = 0
ERR_REASON_MSG_TYPE_UNKNOWN = 1
ERR_REASON_REQ_TYPE_UNKNOWN = 2
ERR_REASON_API_INCOMPATIBLE = 3
ERR_REASON_INVALID_JSON     = 4
ERR_REASON_INVALID_FORMAT   = 5
ERR_REASON_UNKNOWN_ERROR    = 6


class OneWeb_UT_AutomationSuiteConfig:
    def __init__(self):

        #### Variables from configuration file
        self.number_of_ut = 0           # SSM Address
        
       

class UT_Config:
    def __init__(self):

        #### Variables from configuration file
        self.ut_ssm_ip_addr = 0           # SSM Address
        self.
        
       
     
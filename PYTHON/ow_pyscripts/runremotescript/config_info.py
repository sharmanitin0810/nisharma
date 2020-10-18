##################################################################################################################################################
#  Copyright Copyright (c) 2020 Hughes Network System, LLC.
#
#  FILE NAME: config_info.py
#
#  DESCRIPTION: The config class that loads configurable parameters from a config file to be used by the runRemoteTestSuite.py
#
#
#  DATE           NAME          REFERENCE       REASON
#  08/25/2020     S.Krishna         SPR84256    Initial Draft
#
##################################################################################################################################################
import csv

class config_info:
    def __init__(self):
        self.textParam = {}
        self.proxy_server_ip_gw = ""
        self.proxy_server_login_gw = ""
        self.proxy_server_pass_gw = ""
        self.proxy_server_ip_ut = ""
        self.proxy_server_login_ut = ""
        self.proxy_server_pass_ut = ""
        self.server_ip = ""
        self.server_login = ""
        self.server_pass = ""
        self.ut_cnx_ip = ""
        self.ut_cnx_login = ""
        self.ut_cnx_pass = ""
        self.test_server_iperf_cmd_for_cnx = ""
        self.test_server_iperf_cmd_for_ssm = ""
        self.cnx_iperf_cmd = ""
        self.ssm_iperf_cmd = ""
        
    def loadConfig(self, file):
        with open(file, 'r') as f:
          for line in f:
            if "#" in line:
              continue
            line = line.rstrip("\n")
            if "=" in line:
              line = line.split("=")
              line[1] = line[1].strip(" ")
              line[0] = line[0].strip(" ")
              line[1] = line[1].replace('"','')
              line[1] = line[1].replace('\'','')
              #config file parameter name will be key for text file
              self.textParam[line[0]] = line[1]
            elif ":" in line:
              line = line.split(":")
              line[1] = line[1].strip(" ")
              line[0] = line[0].strip(" ")
              line[1] = line[1].replace('"','')
              #config file parameter name will be key for text file
              self.textParam[line[0]] = line[1]
        f.close()

        self.proxy_server_ip_gw = self.textParam["GW_SSH_PROXY_SERVER_IP"]
        self.proxy_server_login_gw = self.textParam["GW_SSH_PROXY_SERVER_LOGIN"]
        self.proxy_server_pass_gw = self.textParam["GW_SSH_SERVER_PROXY_PASSWORD"]
        self.proxy_server_ip_ut = self.textParam["UT_SSH_PROXY_SERVER_IP"]
        self.proxy_server_login_ut = self.textParam["UT_SSH_PROXY_SERVER_LOGIN"]
        self.proxy_server_pass_ut = self.textParam["UT_SSH_SERVER_PROXY_PASSWORD"]
        self.server_ip = self.textParam["TEST_SERVER_IP"]
        self.server_login = self.textParam["TEST_SERVER_LOGIN"]
        self.server_pass = self.textParam["TEST_SERVER_PASSWORD"]
        self.ut_cnx_ip = self.textParam["UT_CNX_IP"]
        self.ut_cnx_login = self.textParam["UT_CNX_LOGIN"]
        self.ut_cnx_pass = self.textParam["UT_CNX_PASSWORD"]
        self.test_server_iperf_cmd_for_cnx = self.textParam["TEST_SERVER_IPERF_COMMAND_FOR_CNX"]
        self.test_server_iperf_cmd_for_ssm = self.textParam["TEST_SERVER_IPERF_COMMAND_FOR_SSM"]
        self.cnx_iperf_cmd = self.textParam["CNX_IPERF_COMMAND"]
        self.ssm_iperf_cmd = self.textParam["SSM_IPERF_COMMAND"]
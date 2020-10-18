Run the following commands to generate win32com py packages for Qualcomm software 

Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

D:\Anaconda3\Lib\site-packages\win32com\client>python makepy.py -i "C:\Program Files (x86)\Qualcomm\QXDM4\QXDM"
Could not locate a type library matching 'C:\Program Files (x86)\Qualcomm\QXDM4\QXDM'

D:\Anaconda3\Lib\site-packages\win32com\client>python makepy.py -i "C:\Program Files (x86)\Qualcomm\QXDM4\QXDM.tlb"
QXDMLib
 {10101010-1962-4443-B554-28AB4645A17B}, lcid=0, major=1, minor=0
 >>> # Use these commands in Python code to auto generate .py support
 >>> from win32com.client import gencache
 >>> gencache.EnsureModule('{10101010-1962-4443-B554-28AB4645A17B}', 0, 1, 0)

D:\Anaconda3\Lib\site-packages\win32com\client>python makepy.py -i "C:\Program Files (x86)\Qualcomm\QPST\bin\QPSTProxyComponents.tlb"
QPSTPROXYCOMPONENTSLib
 {21454A49-2D4B-4F4E-A401-0C2614B1266B}, lcid=0, major=1, minor=0
 >>> # Use these commands in Python code to auto generate .py support
 >>> from win32com.client import gencache
 >>> gencache.EnsureModule('{21454A49-2D4B-4F4E-A401-0C2614B1266B}', 0, 1, 0)

D:\Anaconda3\Lib\site-packages\win32com\client>python makepy.py -i "C:\Program Files (x86)\Qualcomm\QPST\bin\AtmnServer"
Could not locate a type library matching 'C:\Program Files (x86)\Qualcomm\QPST\bin\AtmnServer'

D:\Anaconda3\Lib\site-packages\win32com\client>python makepy.py -i "C:\Program Files (x86)\Qualcomm\QPST\bin\AtmnServer.tlb"
AtmnServer
 {F6F37A12-F62A-4603-8757-6266058CF48E}, lcid=0, major=1, minor=0
 >>> # Use these commands in Python code to auto generate .py support
 >>> from win32com.client import gencache
 >>> gencache.EnsureModule('{F6F37A12-F62A-4603-8757-6266058CF48E}', 0, 1, 0)

D:\Anaconda3\Lib\site-packages\win32com\client>python makepy.py -i "C:\Program Files (x86)\Qualcomm\QPST\bin\QPSTServer"
Could not locate a type library matching 'C:\Program Files (x86)\Qualcomm\QPST\bin\QPSTServer'

D:\Anaconda3\Lib\site-packages\win32com\client>python makepy.py -i "C:\Program Files (x86)\Qualcomm\QCAT 6.x\Bin\QCAT.tlb"
QCAT
 {9A67840B-D27F-45F9-823F-0E0CB5171ED3}, lcid=0, major=1, minor=0
 >>> # Use these commands in Python code to auto generate .py support
 >>> from win32com.client import gencache
 >>> gencache.EnsureModule('{9A67840B-D27F-45F9-823F-0E0CB5171ED3}', 0, 1, 0)

D:\Anaconda3\Lib\site-packages\win32com\client>python makepy.py -i "C:\Program Files (x86)\Qualcomm\QPST\bin\QPSTConfig"
Could not locate a type library matching 'C:\Program Files (x86)\Qualcomm\QPST\bin\QPSTConfig'

D:\Anaconda3\Lib\site-packages\win32com\client>python makepy.py -i "C:\Program Files (x86)\Qualcomm\QPST\bin\SplashLibrary.tlb"
SplashLibrary
 {550FEF2C-89BB-4312-9750-F65A991547D9}, lcid=0, major=1, minor=0
 >>> # Use these commands in Python code to auto generate .py support
 >>> from win32com.client import gencache
 >>> gencache.EnsureModule('{550FEF2C-89BB-4312-9750-F65A991547D9}', 0, 1, 0)

D:\Anaconda3\Lib\site-packages\win32com\client>





C:\ROID_GN_TEST>python ROID_TEST.py
Traceback (most recent call last):
  File "ROID_TEST.py", line 16, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'

C:\ROID_GN_TEST>pip install requests
Collecting requests
  Downloading requests-2.24.0-py2.py3-none-any.whl (61 kB)
     |████████████████████████████████| 61 kB 173 kB/s
Collecting chardet<4,>=3.0.2
  Using cached chardet-3.0.4-py2.py3-none-any.whl (133 kB)
Collecting certifi>=2017.4.17
  Downloading certifi-2020.6.20-py2.py3-none-any.whl (156 kB)
     |████████████████████████████████| 156 kB 2.2 MB/s
Collecting urllib3!=1.25.0,!=1.25.1,<1.26,>=1.21.1
  Downloading urllib3-1.25.10-py2.py3-none-any.whl (127 kB)
     |████████████████████████████████| 127 kB 2.2 MB/s
Collecting idna<3,>=2.5
  Downloading idna-2.10-py2.py3-none-any.whl (58 kB)
     |████████████████████████████████| 58 kB 3.8 MB/s
Installing collected packages: chardet, certifi, urllib3, idna, requests
Successfully installed certifi-2020.6.20 chardet-3.0.4 idna-2.10 requests-2.24.0 urllib3-1.25.10
WARNING: You are using pip version 20.1.1; however, version 20.2.3 is available.
You should consider upgrading via the 'c:\python37\python.exe -m pip install --upgrade pip' command.

C:\ROID_GN_TEST>pip install paramiko
Collecting paramiko
  Downloading paramiko-2.7.2-py2.py3-none-any.whl (206 kB)
     |████████████████████████████████| 206 kB 2.2 MB/s
Collecting cryptography>=2.5
  Downloading cryptography-3.1-cp37-cp37m-win_amd64.whl (1.5 MB)
     |████████████████████████████████| 1.5 MB 2.2 MB/s
Collecting bcrypt>=3.1.3
  Downloading bcrypt-3.2.0-cp36-abi3-win_amd64.whl (28 kB)
Collecting pynacl>=1.0.1
  Downloading PyNaCl-1.4.0-cp37-cp37m-win_amd64.whl (206 kB)
     |████████████████████████████████| 206 kB 3.2 MB/s
Collecting cffi!=1.11.3,>=1.8
  Downloading cffi-1.14.2-cp37-cp37m-win_amd64.whl (178 kB)
     |████████████████████████████████| 178 kB 2.2 MB/s
Collecting six>=1.4.1
  Downloading six-1.15.0-py2.py3-none-any.whl (10 kB)
Collecting pycparser
  Downloading pycparser-2.20-py2.py3-none-any.whl (112 kB)
     |████████████████████████████████| 112 kB 2.2 MB/s
Installing collected packages: pycparser, cffi, six, cryptography, bcrypt, pynacl, paramiko
Successfully installed bcrypt-3.2.0 cffi-1.14.2 cryptography-3.1 paramiko-2.7.2 pycparser-2.20 pynacl-1.4.0 six-1.15.0
WARNING: You are using pip version 20.1.1; however, version 20.2.3 is available.
You should consider upgrading via the 'c:\python37\python.exe -m pip install --upgrade pip' command.

C:\ROID_GN_TEST>
C:\ROID_GN_TEST>
C:\ROID_GN_TEST>
C:\ROID_GN_TEST>python ROID_TEST.py
Traceback (most recent call last):
  File "ROID_TEST.py", line 23, in <module>
    import win32com.client as win32
ModuleNotFoundError: No module named 'win32com'

C:\ROID_GN_TEST>pip install pywin32
Collecting pywin32
  Downloading pywin32-228-cp37-cp37m-win_amd64.whl (9.1 MB)
     |████████████████████████████████| 9.1 MB 2.2 MB/s
Installing collected packages: pywin32
Successfully installed pywin32-228
WARNING: You are using pip version 20.1.1; however, version 20.2.3 is available.
You should consider upgrading via the 'c:\python37\python.exe -m pip install --upgrade pip' command.

C:\ROID_GN_TEST>
C:\ROID_GN_TEST>
C:\ROID_GN_TEST>
C:\ROID_GN_TEST>python ROID_TEST.py
Traceback (most recent call last):
  File "ROID_TEST.py", line 32, in <module>
    from scp import SCPClient
ModuleNotFoundError: No module named 'scp'

C:\ROID_GN_TEST>pip install pyscp
ERROR: Could not find a version that satisfies the requirement pyscp (from versions: none)
ERROR: No matching distribution found for pyscp
WARNING: You are using pip version 20.1.1; however, version 20.2.3 is available.
You should consider upgrading via the 'c:\python37\python.exe -m pip install --upgrade pip' command.

C:\ROID_GN_TEST>pip install scp
Collecting scp
  Downloading scp-0.13.2-py2.py3-none-any.whl (9.5 kB)
Requirement already satisfied: paramiko in c:\python37\lib\site-packages (from scp) (2.7.2)
Requirement already satisfied: cryptography>=2.5 in c:\python37\lib\site-packages (from paramiko->scp) (3.1)
Requirement already satisfied: pynacl>=1.0.1 in c:\python37\lib\site-packages (from paramiko->scp) (1.4.0)
Requirement already satisfied: bcrypt>=3.1.3 in c:\python37\lib\site-packages (from paramiko->scp) (3.2.0)
Requirement already satisfied: six>=1.4.1 in c:\python37\lib\site-packages (from cryptography>=2.5->paramiko->scp) (1.15.0)
Requirement already satisfied: cffi!=1.11.3,>=1.8 in c:\python37\lib\site-packages (from cryptography>=2.5->paramiko->scp) (1.14.2)
Requirement already satisfied: pycparser in c:\python37\lib\site-packages (from cffi!=1.11.3,>=1.8->cryptography>=2.5->paramiko->scp) (2.20)
Installing collected packages: scp
Successfully installed scp-0.13.2
WARNING: You are using pip version 20.1.1; however, version 20.2.3 is available.
You should consider upgrading via the 'c:\python37\python.exe -m pip install --upgrade pip' command.

C:\ROID_GN_TEST>python ROID_TEST.py
Started Program
OneWeb UT AUTOMATED TEST EXECUTION
Main Menu
['10.101.1.40', '10.101.1.30', '10.101.1.10', '10.101.1.20']
Connected UT is : 10.101.1.40 ID : 1
Connected UT is : 10.101.1.30 ID : 2
Connected UT is : 10.101.1.10 ID : 3
Connected UT is : 10.101.1.20 ID : 4
Choose Test Action
0. EXIT TEST SUITE
1. START_CALL
2. STOP_CALL
3. START WAN DOWNLINK IPERF SESSION
4. START WAN UPLINK IPERF SESSION
5. START WAN UPLINK/DOWNLINK IPERF SESSION
6. LOAD LATEST EPHEMERIS
7. COLLECT UT LOGS
8. GET INTERFACE STATUS
9. START QPST SERVER
10. STOP QPST SERVER
Test Action>>9
Main Menu
['10.101.1.40', '10.101.1.30', '10.101.1.10', '10.101.1.20']
Connected UT is : 10.101.1.40 ID : 1
Connected UT is : 10.101.1.30 ID : 2
Connected UT is : 10.101.1.10 ID : 3
Connected UT is : 10.101.1.20 ID : 4
Choose Test Action
0. EXIT TEST SUITE
1. START_CALL
2. STOP_CALL
3. START WAN DOWNLINK IPERF SESSION
4. START WAN UPLINK IPERF SESSION
5. START WAN UPLINK/DOWNLINK IPERF SESSION
6. LOAD LATEST EPHEMERIS
7. COLLECT UT LOGS
8. GET INTERFACE STATUS
9. START QPST SERVER
10. STOP QPST SERVER
Test Action>>



2) Import the modules as shown in the output. 


import sys
import os
import subprocess
from subprocess import check_output, CalledProcessError
import fnmatch
import shutil

if (len(sys.argv)-1)<1:
    print("The script is called with zero arguments\n format: {} <YYYY-MM-DD>".format(sys.argv[0]))
    sys.exit(1)
else:
  date=sys.argv[1]
  check_output("net use t: /delete")
  check_output("net use t: \\\\10.52.4.68\\oat\\"+date)
  os.chdir("t:")

for dirpath, dirs, files in os.walk('.'):
    for file in fnmatch.filter(files, '*.isf'):
	filename= os.path.join(dirpath,file)
	print(filename)
	check_output("\"C:\\Program Files (x86)\\QUALCOMM\\QCAT 6.x\\Bin\\QCAT.exe\" -txt -filter=C:\\Users\\oneweb\\Documents\\QCAT_FILTERS\\OVERVIEW_with_ML1.txt "+filename, shell=True)
	   #check_output("\"C:\\Program Files (x86)\\QUALCOMM\\QCAT 6.x\\Bin\\QCAT.exe\" -analyzer=\"User;Custom;RSRP and RSSI \""  + filename, shell=True)

import paramiko
import subprocess
s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect("10.11.100.155",22,username="oneweb",password='oneweb123',timeout=4)
sftp = s.open_sftp()

stdin, stdout, stderr = s.exec_command('cd /home/oneweb/AmSoni; \
					sha512sum default_ephemeris.csv') 
for line in stdout:
	print("shasum is :",line.strip('\n'))
	

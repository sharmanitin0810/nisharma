import paramiko
import os

process = os.getpid()

print("PID is :",process)
host=input("Please Enter the IP Address of Host")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username='nisharma_hsc', password='oran@123',port=22)
with open ('remote_ouput.txt','w') as file:
	stdin, stdout, stderr = client.exec_command('iperf -s -p 16176 -i 2 -t 10', get_pty=True)
	stdout_final = stdout.read().decode('ascii')
	print(stdout_final)
	file.write("\t Server Output \n")
	file.write(str(stdout_final))

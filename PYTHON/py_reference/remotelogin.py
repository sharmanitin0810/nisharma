import paramiko
import os

host=input("Please Enter the IP Address of Host")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username='nisharma_hsc', password='nitin@0810',port=22)
stdin, stdout, stderr = client.exec_command('sudo ls -lrt', get_pty=True)
print(stdout.read())

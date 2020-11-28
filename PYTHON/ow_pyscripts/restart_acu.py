import os
import paramiko
import time
import subprocess

acu_list = ['10.39.238.20','10.39.238.25'] 

def ssh_client(target_acu):
	client_ssh = paramiko.SSHClient()
	client_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client_ssh.connect(target_acu, username='acu', password='password',port=22)
	return client_ssh

def stop_start_acu(acu_ip,c_pid):
	print("Restarting ACU Simulator : [{}].".format(acu_ip))
	acu_client = ssh_client(acu_ip)
	acu_kill = 'kill -6'+" "+c_pid
	start_acu = '/home/acu/acusim/startacu'
	stdin,stdout,stderr = acu_client.exec_command(acu_kill)
	print("Successfully Stopped the ACU :{} with previous PID :{}".format(acu_ip,c_pid))
	time.sleep(2)
	stdin,stdout,stderr = acu_client.exec_command(start_acu)
	acu_client.close()
	return
	
def check_restart_acu():
	for acu in acu_list:

		print("Verifying the current status of ACU Simulator : [{}]".format(acu))
		acu_client = ssh_client(acu)
		pid_cmd = "ps -ef | grep [s]trk | awk '{print $2}'"
		stdin,stdout,stderr = acu_client.exec_command(str(pid_cmd))
		acu_pid = stdout.read()

		if acu_pid == '':
			print("ACU Simulator : {} is not running currenlty , going to Start it now.".format(acu))
			start_acu = '/home/acu/acusim/startacu'
			stdin,stdout,stderr = acu_client.exec_command(start_acu)
			print("Successfully Started the ACU Simulator..!!")
			time.sleep(1)
			stdin,stdout,stderr = acu_client.exec_command(str(pid_cmd))
			final_pid = stdout.read()
			print("New PID for ACU Simulator : {} is : {}".format(acu,final_pid))

		else:
			print("ACU Simulator :{} is running currently with PID :{} ".format(acu,acu_pid))
			stop_start_acu(acu,acu_pid)
			stdin,stdout,stderr = acu_client.exec_command(str(pid_cmd))
			new_pid = stdout.read()
			print("Successfully restarted the ACU Simulator :{} & new PID is:{}".format(acu,new_pid))
		acu_client.close()
		print("-"*70)

if __name__ == "__main__":

		os.system('clear')
		print(" ######## ACU SIMULATOR RESTART UTILITY #######");print('\n')
		check_restart_acu()

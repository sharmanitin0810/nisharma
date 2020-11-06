import os
import paramiko

jump_ems_ip = "10.31.128.22"
log_server = "10.31.128.13"
rcmd = "ls -lrt | wc -l"


def run_remote_command():

    print("In Run remote command function ...")

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(jump_ems_ip, username='msat', password='oneweb123')
    ssh_client_transport = ssh_client.get_transport()
    src_addr = (jump_ems_ip, 22)
    dest_addr = (log_server, 22)
    jump_channel = ssh_client_transport.open_channel(
        "direct-tcpip", dest_addr, src_addr)

    target = paramiko.SSHClient()
    target.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    target.connect(log_server, username='msat',
                   password='oneweb123', sock=jump_channel)
    stdin, stdout, stderr = target.exec_command(rcmd)
    output = stdout.read().decode('ascii').strip("\n")
    print ("Output is :",output)
    target.close()
    ssh_client.close()


if __name__ == "__main__":

    print("Remote Command Execution Script started ...")
    run_remote_command()

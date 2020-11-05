#!/usr/bin/python
# -----------------------------------------------------------------------------------------
# PURPOSE: To check health status of all the nodes of Ground Network
#
import signal
import sys
import time
import logging
import paramiko
from datetime import datetime
from subprocess import call
import mail_core
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

ipAd = ''
IpList = []

logger = paramiko.util.logging.getLogger()
logging.getLogger("paramiko").setLevel(logging.WARNING)


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


def pingTest(host):
    hostname = str(host)
    cmd = "ping -c 2 " + host
    print cmd
    response = os.system(cmd)
    # and then check the response...
    print response
    logFname = 22
    if response == 0:
        logging.info("Host: with IP: %s is reachable" % (host))
    else:
        logging.warning("Host: with IP: %s is not reachable" % (host))


def checkSystem(host):
    path = '/home/msat/cores/'
    rcmd = 'ls %s | wc -l' % (path)
    listrcmd = 'ls -ltr %s' % (path)
    USERNAME = 'msat'
    PASSWORD = 'oneweb123'
    #print rcmd
    #op = call(rcmd)
    #op = os.system(rcmd)
    #print op
    # sys.exit(0)
    #host = ipAd.replace("'","")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_host_keys(os.path.expanduser(
        os.path.join("~", ".ssh", "known_hosts")))
    try:

        #ssh.connect(ipAd, username="msat", password="oneweb123")
        ssh.connect(host, username=USERNAME, password=PASSWORD, timeout=10)
        stdin, stdout, stderr = ssh.exec_command(rcmd)
        #stdin, stdout, stderr = ssh.exec_command(listrcmd)
        logging.info(
            "*******************Checking core files...*****************")
        output = stdout.read().decode('ascii').strip("\n")
        #output = ssh_stdout.readlines()
        print output
        #logging.info("Core file test output: %s" %(output))
        # ssh_stdin.flush()
	if int(output) == 0:
            logging.info("Core file not generated...")
        else:
            logging.error(" %s Core file generated..." % (output))
            crcmd = 'ls -lrt %s' % (path)
            ssh.connect(host, username=USERNAME, password=PASSWORD, timeout=10)
            stdin, stdout, stderr = ssh.exec_command(crcmd)
            global lines
	    for lines in stdout:
                logging.info("%s" % (lines))
            time.sleep(2)
            ssh.close()
    except:
	  print("unable to generate")

################ Mail Core file data #################################################

def mail():
        print(logFname)
        fromaddr = "nibvalidation@gmail.com"
        toaddr = ["amit.soni@hsc.com","nitin.sharma@hsc.com"]

# instance of MIMEMultipart
        msg = MIMEMultipart()

# storing the senders email address
        msg['From'] = fromaddr

# storing the receivers email address
        msg['To'] = ", ".join(toaddr)

# storing the subject
        msg['Subject'] = "Core_File Status Report GN-1"

# string to store the body of the mail
        body = """Hi Team, 
		
			Todays Core file status Report of Gn Componenets are attached
                        
                        Thanks,
                        Amit Soni  """

# attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

# open the file to be sent
        filename = logFname
        attachment = open("/root/nisharma_hsc/ow_pyscripts/siteTestingScript/log/"+str(logFname), "rb")

# instance of MIMEBase and named as p
        p = MIMEBase('application', 'octet-stream')

# To change the payload into encoded form
        p.set_payload((attachment).read())

# encode into base64
        encoders.encode_base64(p)

        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

# attach the instance 'p' to instance 'msg'
        msg.attach(p)

# creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)

# start TLS for security
        s.starttls()

# Authentication
        s.login(fromaddr, "ifnaqgxdmbfaqhwq")

# Converts the Multipart msg into a string
        text = msg.as_string()

# sending the mail
        s.sendmail(fromaddr, toaddr, text)

# terminating the session
        s.quit()


def main():
    global logFname	
    logFname = datetime.now().strftime('remoteTest_%H_%M_%d_%m_%Y.log')
    print(logFname)
    logging.basicConfig(filename='log/%s' % (logFname), level=logging.DEBUG)
     
    global IpList
    i = 0
    signal.signal(signal.SIGINT, signal_handler)
    global hosts
    hosts = open('site-ip.txt', 'r').read().splitlines()
    for i in range(0, len(hosts)):
        print(hosts[i])
        # print(len(hosts))
        # irint(ip)
        ## Execute tests ##
        pingTest(hosts[i])
        # print("amit")
        checkSystem(hosts[i])
        # print("soni")
    mail()
if __name__ == '__main__':
    main()
    log = 1

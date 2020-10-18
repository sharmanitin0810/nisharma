# Copy over files from a remote server directory as and when they become
# available.
# Date          Author                  Change
# 5/26/11       Sandeep Ahluwalia       Initial create
# 6/30/11       Sandeep Ahluwalia       Do not reload preexisting files
# 7/18/11       Sandeep Ahluwalia       (1) Support for message source and destination
#                                           selection based on the value of message selection field
#                                       (2) FTP session should retry when the socket connection is reset
#                                       (3) Use relative paths when generating message details.
#                                       (4) Do not attempt document generation if no interaction is found
#                                       (5) Do not load PDML files if they are locally present

import time
import os
import sys
#import sftpClient
import paramiko
import hashlib

class AsciiFile:
    """
    Class designed to provide a callback method to save a text line with
    the native line separator (LF-CR on Windows)
    """

    def __init__(self,name=None,mode=''):
        if name:
            self.open(name,mode+'b')
        else:
            self.file = None

    def open(self,name,mode):
        """
        Open the file.
        :param name: Path of the file to be opened
        :param mode: File opening mode
        """
        self.file = open(name,mode+'b')

    def writeline(self,line):
        """
        Save the line of text. Also add a line separator at the end of the line.
        :param line: Text line to be saved.
        """
        self.file.write(line)
        self.file.write(os.linesep)
    
    def writeBinline(self,line):
        """
        Save the line of text without adding line separator.Used to download
        the call tracing binary file.
        :param line: Text line to be saved
        """
        self.file.write(line)

    def close(self):
        """
        Close the text file.
        """
        self.file.close()
        self.file = None

class ChkEphEmsUT:
    
    def __init__(self, server, port, user, password, remoteDir,localDir):
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.remoteDir = remoteDir
        self.localDir = localDir
        self.previousFileSet = set([])

    def EmsFileCheck(self, outputdir = '', callback = None):
       
        port = 22
        ssh_client = paramiko.SSHClient()
        ssh_client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(self.server, self.port, self.user, self.password)


        sftp = ssh_client.open_sftp()
        #sftp = sftpClient.create_sftp_client(self.server,self.port,self.user, self.password,KEYFILEPATH,KEYFILETYPE)
        #print "CALLBACK:", callback
        
        self.previousFileSet = set(os.listdir(self.localDir))
        
        try:
           print("Entring try block ")
           currentFileSet = set(sftp.listdir(self.remoteDir))
           newFiles = currentFileSet - self.previousFileSet
           #print("New Files :",newFiles)
           if newFiles == set():
            print("No New file eph file is detected on EMS")
            return 1
            
           else :
            print("New files detected on EMS ..")
            for newFile in newFiles:
                if ('default_ephemeris' in newFile.split(".")[0]) and (newFile.split(".")[-1]=='csv'):
                    newFilePath = os.path.join(self.remoteDir,newFile)
                    localFilePath = os.path.join(self.localDir,newFile)
                    sftp.get(newFilePath,localFilePath)
                    time.sleep(2)
                    with open (localFilePath,"rb") as file:
                        bytes = file.read()
                        ems_eph_hash = hashlib.sha512(bytes).hexdigest()
                        #print(ems_eph_hash)
                        return ems_eph_hash
                        ssh_client.close()
                      
        except Exception as e:
           print("Exceptionnnnn : " + str(e))
#            ut_sftp.close()
#            ut_sftp = sftpClient.create_sftp_client(UT_HOST_MACHINE, UT_PORT, UT_USERNAME, UT_PASSWORD, KEYFILEPATH, KEYFILETYPE)
#            print ("Re-opened ut_sftp channel")




    
class DirectoryReplicator:
    """
    Replicate a remote directory to a local directory. New files are copied as and
    when they are generated.
    :param server: Remote server
    :param user: Remote user name
    :param password: User's password
    :param remoteDir: Remote directory that needs to be replicated on the local machine
    """

    def __init__(self, server, port, user, password, remoteDir):
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.remoteDir = remoteDir
        self.previousFileSet = set([])


    def Replicate(self, outputdir = '', callback = None):
        """
        This method wakes up every 10 seconds and copies any new files that way have been
        generated on the remote server.
        :param callback: If specified, the callback is called whenever a file transfer
                         is completed.
        """

        sftp = sftpClient.create_sftp_client(self.server,self.port,self.user, self.password,KEYFILEPATH,KEYFILETYPE)
        #print "CALLBACK:", callback
        
        self.previousFileSet = set(os.listdir(LOCAL_DIR))
        
#        newLocalFilePath = os.path.join(LOCAL_DIR,"default_ephemeris.csv")
#        utFilePath       = os.path.join(UT_REMOTE_DIR,"default_ephemeris.csv")
#        ut_sftp = sftpClient.create_sftp_client(UT_HOST_MACHINE, UT_PORT, UT_USERNAME, UT_PASSWORD, KEYFILEPATH, KEYFILETYPE)
        
        while True:
          try:
            currentFileSet = set(sftp.listdir(self.remoteDir))
            newFiles = currentFileSet - self.previousFileSet
            for newFile in newFiles:
                if ('default_ephemeris' in newFile.split(".")[0]) and (newFile.split(".")[-1]=='csv'):
                    newFilePath = os.path.join(self.remoteDir,newFile)
                    localFilePath = os.path.join(LOCAL_DIR,newFile)
                    sftp.get(newFilePath,localFilePath)
                    if callback: callback(newFilePath)
                    
                    # Just want to make sure the new eph file get downloaded 
                    time.sleep(1)
                    # Notes: After awhile, sftp section on the UT will be closed.
                    #        Hence Exception will occur.
                    #        To avoid that, open and close the sftp section each time.
                    # 1. Opens an sftp section to upload the eph file 
                    # 2. Uploads the new eph.csv to the UT controller (Android OS) 
                    #    under /home/nomad/defaultEphemeris/ dir
                    # 3. Pushes the new default_ephemeris.csv to the UT
                    # 4. Closes the sftp section
                    ut_sftp = sftpClient.create_sftp_client(UT_HOST_MACHINE, UT_PORT, UT_USERNAME, UT_PASSWORD, KEYFILEPATH, KEYFILETYPE)
#                    os.rename(localFilePath, newLocalFilePath)
#                    ut_sftp.put(newLocalFilePath,utFilePath)
                    utFilePath = os.path.join(UT_REMOTE_DIR,newFile)
                    ut_sftp.put(localFilePath,utFilePath) 
                    time.sleep(1)
                    print(" Going to Push newly available eph. file to UT..")
                    pushEphemeris()                    
                    time.sleep(1)
                    ut_sftp.close()
 
            self.previousFileSet = currentFileSet
            time.sleep(10)
            

          except Exception as e:
            print("Exceptionnnnn : " + str(e))
#            ut_sftp.close()
#            ut_sftp = sftpClient.create_sftp_client(UT_HOST_MACHINE, UT_PORT, UT_USERNAME, UT_PASSWORD, KEYFILEPATH, KEYFILETYPE)
#            print ("Re-opened ut_sftp channel")


def pushEphemeris():
    """ 
    This method opens an ssh section to remotely execute commands on the remote machine
    """
    print("In pushEphemeris func. to push eph. file on UT")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(str(UT_HOST_MACHINE), username=str(UT_USERNAME), password=str(UT_PASSWORD), allow_agent=False)
    
    stdin, stdout, stderr = client.exec_command('sudo adb shell rm /etc/sha1chksum;                   \
                                                 sudo mv /home/nomad/defaultEphemeris/default_ephemeris_*.csv /home/nomad/defaultEphemeris/default_ephemeris.csv; \
                                                 sudo adb push /home/nomad/defaultEphemeris/default_ephemeris.csv /etc/;         \
                                                 sudo adb shell tail -n 1 /etc/default_ephemeris.csv; \
                                                 adb reboot')
    
#    stdin, stdout, stderr = client.exec_command('ls -lstr /home/acu/tle/defaultEphemeris; \
#                                                 cd /home/acu/tle/defaultEphemeris;       \
#                                                 sh pushEphemeris.sh')

    for line in stdout:
        #print line.strip('\n')
        print ("Succesfully pushed eph. file on UT..!!")
    
    client.close()


def printme(fname):
    print ("Downloading file " ,fname)





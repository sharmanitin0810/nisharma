Puspose: This script is used for testing the helath status of all the nodes of SAC/POP rack of Ground network.

Input: site-ip.txt file consists of ip address of all the nodes of which health is monitored. (sample file attached for reference)

How to run: 
    Add the list of GN components ips in site-ip.txt file and run below command:
    "sudo python siteTesting.py "
    
     - It will run for an hour and will exit by itself on completion. After that you can check the logs for analysing the GN components.



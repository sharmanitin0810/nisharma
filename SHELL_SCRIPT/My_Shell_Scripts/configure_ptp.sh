#########################################################################################
# PURPOSE:To implement & auto-configure linuxptp Centos server. 
# SOURCE CODE FILE: "configure_ptp.sh" 
# RELEASE INFO: O-RAN Bronze release
# REVISION HISTORY:
#          DATE:           AUTHOR:         CHANGE:
#          21-07-2020      Nitin Sharma   Final Version
# USAGE & PRE-REUISITES : 
#	- Interface should support H/W & S/W timestamping on which you want to configure
#	- Run script with Interface name as an Argument 
#	- For Eg: ./configure_ptp.sh eno1 
#-----------------------------------------------------------------------------------------

#!/bin/bash

#Function to verify linuxptp installation
verify_linuxptp()
{
  check_cmd="rpm -qi linuxptp >/dev/null 2>&1"
	eval $check_cmd
	if [ $? == 0 ]
	then
	echo "Linuxptp is already installed...Not Installing Again..!! ";echo
	else
	echo "Linuxptp is not installed ..Installing now ..Please wait ..";echo
	install_cmd="yum install -y linuxptp"
	sleep 1;
	eval $install_cmd >/dev/null 2>&1
		if [ $? == 0 ]
		then 
		echo "Linuxptp is installed successfully ..!!";echo
		else
		echo "Error : Linuxptp auto-installation Aborted..please try installing manually using "$install_cmd" command ";echo
		fi
	fi
}

#Function to start ptp4l & phc2sys services
start_services()
	{
		enable_ptp4l="systemctl enable ptp4l"
		enable_phc2sys="systemctl enable phc2sys"
		start_ptp4l="service ptp4l start"
		start_phc2sys="service phc2sys start"

	if [[ $1 == "phc2sys" ]]
	then
		echo "Starting phc2sys service..";echo
		eval $enable_phc2sys >/dev/null 2>&1
		eval $start_phc2sys  >/dev/null 2>&1
	elif [[ $1 == "ptp4l" ]]
	then 
		echo "Starting ptp4l service..";echo
		eval $enable_ptp4l >/dev/null 2>&1
		eval $start_ptp4l  >/dev/null 2>&1
	else
		echo "Starting both the services..";echo
		eval $enable_phc2sys >/dev/null 2>&1
		eval $start_phc2sys  >/dev/null 2>&1
		eval $enable_ptp4l >/dev/null 2>&1
		eval $start_ptp4l  >/dev/null 2>&1
	fi

	}

#Function to verify status of ptp4l & phc2sys services 
verify_services()
{
	verify_ptp4l="systemctl show -p ActiveState ptp4l | sed 's/ActiveState=//g'"
	verify_phc2ys="systemctl show -p ActiveState phc2sys | sed 's/ActiveState=//g'"
	out_ptp4l=`eval $verify_ptp4l`
	out_phc2sys=`eval $verify_phc2ys`

    #Veriying already configured interfcace vs user input interface
		old_intf=`sudo cat /etc/sysconfig/ptp4l | awk {'gsub(/"/, "", $4);print $4'}`
		echo "Previosuly Configured Interface for PTP : $old_intf";echo
		sed -i "s/$old_intf/$1/g" /etc/sysconfig/ptp4l
		echo "Newly Configured Interface for PTP : $1";echo

	if [ $out_ptp4l == "active" ] && [ $out_phc2sys == "active" ]
		then
		echo "Both "ptp4l" & "phc2sys" service are already Up and Running";echo
		elif [ $out_ptp4l == "active" ] && [ $out_phc2sys == "inactive" ]
		then
		echo "Only "ptp4l" service is Up & running";echo
		start_services phc2sys	
		verify_services
		elif [ $out_ptp4l == "inactive" ] && [ $out_phc2sys == "active"  ]
		then
		echo " Only "phc2sys" service is Up & running";echo
		start_services ptp4l
		verify_services
		else
		echo "Both "ptp4l" & "phc2sys" services are not running....Starting the servies now ...!!";echo
		start_services
		echo "Both the Services are Started  Successfully ..!! :";echo
	fi
}


#Script execution starts from here

eval "clear"
echo "##### O-RAN Linux PTP v2.0 Installer #####";echo

#verifying the user input argument 

	if [ -z "$1" ]
		then 	
		echo "Script Execution Error : No any argument provided "
		echo "Please provide interface name which support Hardware Timestamping"
		echo "For e.g. eno1 (Interface on which you want to configure Linuxptp)";echo
	else 
		echo "Configuring linuxptp on --> "$1" <-- Interface ..please wait .. ";echo
		echo "Verifying Linuxptp is already installed or not";echo 
		sleep 1;
		verify_linuxptp
		echo "Verifying ptp4l & phc2sys service are now running or not";echo
		sleep 1;
		verify_services $1
  fi

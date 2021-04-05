#!/bin/bash

chk_run_ping()
  {
     date_cmd="date"
     get_curr_time=`eval $date_cmd`
     echo "Ping Test Start Time : $get_curr_time"
     echo "Ping Duration : [$1 Seconds]";echo
     echo "Running ping test on Media server (192.168.53.10)"
     sleep 2;

     eval 'ping -c $1 192.168.53.10'
  }

eval "clear"

if [ -z "$1" ]
		then 	
		echo "Script Execution Error : No any argument provided "
		echo "Provide the ping duration (In seconds) "
		echo "For e.g. ./ping_check.sh 40 ";echo
	else 
		chk_run_ping $1
fi


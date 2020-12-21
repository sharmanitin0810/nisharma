#Copyright (c) 2020 Hughes Network System, LLC.
#
#  FILE NAME: get_pdsch_stats.py
#
#  DESCRIPTION: Debug script for getting PDSCH stats.  
#
#           DATE           NAME          REFERENCE       REASON
#       10/19/2020     Abhishek Deb                  Initial Draft
#
#######################################################################################################

import os
import re
import sys
import json
import glob
import argparse
import subprocess

DESCRIPTION = "Debug script for getting PDSCH stats."
SCRIPTS_DIR = os.path.dirname(os.path.realpath(__file__))

class Info:
    def __init__(self, mcs, rbs):
        self.mcs = mcs
        self.rbs = rbs

class Statistics:
    def __init__(self, direction):
        self.info_list = []
        self.mcs_dict = {}
        self.min_rbs = float("inf")
        self.max_rbs = float("-inf")
        self.min_tb_size = float("inf")
        self.max_tb_size = float("-inf")
        self.mapping_data = {}
        self.direction = direction
        self.constant = 0
        self.min_speed = float("inf")
        self.max_speed = float("-inf")
        self.avg_speed = 0
        if self.direction == "ul":
            self.constant = 144
            with open(SCRIPTS_DIR + "/ul_mcs_mapping.json") as dl_mcs_mapping_file:
                self.mapping_data = json.load(dl_mcs_mapping_file)
        else:    
            self.constant = 200
            with open(SCRIPTS_DIR + "/dl_mcs_mapping.json") as ul_mcs_mapping_file:
                self.mapping_data = json.load(ul_mcs_mapping_file)

    def add_info(self, mcs, rbs, tb_size):
        if rbs < self.min_rbs:
            self.min_rbs = rbs
        if rbs > self.max_rbs:
            self.max_rbs = rbs
        if tb_size < self.min_tb_size:
            self.min_tb_size = tb_size
        if tb_size > self.max_tb_size:
            self.max_tb_size = tb_size
        if mcs not in self.mcs_dict:
            self.mcs_dict[mcs] = 1
        else:
            self.mcs_dict[mcs] += 1
        info = Info(mcs, rbs)
        self.info_list.append(info)
    
    def cal_speed(self, rbs, mapping_val):
        speed = 0
        speed = (rbs * self.constant * mapping_val / 0.001) / 1000000
        return speed

    def compute(self):
        not_found = 0
        total_speed = 0
        for info in self.info_list:
            mcs = info.mcs
            rbs = info.rbs
            if str(mcs) in self.mapping_data:
                speed = self.cal_speed(rbs, self.mapping_data[str(mcs)])
                if speed < self.min_speed:
                    self.min_speed = speed
                if speed > self.max_speed:
                    self.max_speed = speed
                total_speed += speed
            else:
                not_found += 1
                print("Could not find MCS info for : " + str(mcs))
        if (len(self.info_list) - not_found) > 0:
            self.avg_speed = total_speed / (len(self.info_list) - not_found)

        print("Analysis for speed for dirction : " + self.direction)
        print("-------------------------------------------------------------")
        print("Min RBs : " + str(self.min_rbs))
        print("Max RBs : " + str(self.max_rbs))
        print("Min TB Size : {} bytes ".format(self.min_tb_size))
        print("Max TB Size : {} bytes ".format(self.max_tb_size))
        print("Min Speed : {:.2f} Mbps".format(self.min_speed))
        print("Max Speed : {:.2f} Mbps".format(self.max_speed))
        print("Avg Speed : {:.2f} Mbps".format(self.avg_speed))
        total_mcs_seen = sum(self.mcs_dict.values())
        if sys.version_info[0] < 3:
            for key, value in self.mcs_dict.iteritems():
                print("MCS : {}  : {:.3f}%".format(key, (value / total_mcs_seen) * 100))
        else:
            for key, value in self.mcs_dict.items():
                print("MCS : {}  : {:.3f}%".format(key, (value / total_mcs_seen) * 100))
        print("-------------------------------------------------------------")

def executeCommand(command):
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
    command_output = proc.communicate()
    return_code = 1 if proc.returncode == None else proc.returncode
    out = command_output[0]
    err = command_output[1]
    return (return_code, out, err)

def get_list_of_isf_files(directory):
    filelist = glob.glob(directory + "\\*.isf")
    return filelist

def generate_txt_from_isf_files(filelist, direction):
    output_filelist = []
    filter_filename = "PUSCH_stat.txt" if direction == "ul" else "PDSCH_stat.txt"
    for filename in filelist:
        output_filename = filename.replace(".isf", ".txt")
        delete_command = "DEL " + output_filename
        executeCommand(delete_command)
        convert_command = "\"C:\\Program Files (x86)\\QUALCOMM\\QCAT 6.x\\Bin\\QCAT.exe\" -txt -filter=\"" + SCRIPTS_DIR + "\\" + filter_filename + "\" " + filename
        return_code, _, _ = executeCommand(convert_command)
        if return_code != 0:
            print("OCAT could not filter file {} with PDSCH filter.".format(filename))
            continue
        if os.path.exists(output_filename):
            output_filelist.append(output_filename)
    return output_filelist

def parse_files(output_directory, filelist, direction):
    rbs_regex = re.compile(r"\s*Number of Resource Blocks\s*=\s*(\d+)")
    mcs_regex = re.compile(r"\s*MCS Index\s*=\s*(\d+)")
    tb_size_regex = re.compile(r"\s*Transport Block Size\s*=\s*(\d+)")
    output_filename = output_directory + "\\PDSCH_out.txt" if direction == "dl" else output_directory + "\\PUSCH_out.txt"
    statistics_obj = Statistics(direction)
    with open(output_filename, "w") as output_file:
        for filename in filelist:
            print("Filename : " + filename)
            output_file.write("Filename : " + filename + "\n")
            with open(filename) as input_file:
                rbs = 0
                mcs = 0
                tb_size = 0
                for line in input_file:
                    if direction == "ul":
                        if "Transport Block Size" in line:
                            if tb_size_regex.search(line).groups()[0]:
                                tb_size = int(tb_size_regex.search(line).groups()[0])
                        if "Number of Resource Blocks" in line: 
                            if rbs_regex.search(line).groups():
                                rbs = int(rbs_regex.search(line).groups()[0])
                        elif "MCS Index" in line:
                            if mcs_regex.search(line).groups():
                                mcs = int(mcs_regex.search(line).groups()[0])
                            statistics_obj.add_info(mcs, rbs, tb_size)
                    else:
                        if "pass" in line.lower():
                            data = line.replace(" ", "").split("|")
                            data = data[1:-1]
                            rnti_type = data[10]
                            if "c" in rnti_type.lower():
                                rbs = int(data[3])
                                tb_size = int(data[14])
                                mcs = int(data[15])
                                statistics_obj.add_info(mcs, rbs, tb_size)
                    output_file.write(line)
    print("Output filename : " + str(output_filename))
    statistics_obj.compute()

def start_parsing(directory, filename, direction):
    if directory:
        directory = directory
        if not os.path.exists(directory):
            print("The directory path does not exists.")
            sys.exit(1)
        input_filelist = get_list_of_isf_files(directory)
        filelist = generate_txt_from_isf_files(input_filelist, direction)
        if filelist:
            parse_files(directory, filelist, direction)
    elif filename:
        if os.path.isdir(filename) or not os.path.exists(filename):
            print("Either the path given is not a file or it does not exists.")
            sys.exit(1)
        filelist = generate_txt_from_isf_files([filename], direction)
        if filelist:
            parse_files(os.path.dirname(filename), filelist, direction)
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = DESCRIPTION)
    parser.add_argument("--dir", help="Directory containing multiple ISF files.")
    parser.add_argument("--file", help="Filename of ISF files.")
    parser.add_argument("--ul", help="Uplink MCS.", action="store_true")
    parser.add_argument("--dl", help="Downlink MCS", action="store_true")
    args = parser.parse_args()

    if not (args.dir or args.file):
        parser.print_help() 
        sys.exit(1)

    if not(args.ul or args.dl):
        parser.print_help()
        sys.exit(1)

    directions = []
    if args.ul:
        directions.append("ul")
    if args.dl:
        directions.append("dl")

    for direction in directions:
        start_parsing(args.dir, args.file, direction)


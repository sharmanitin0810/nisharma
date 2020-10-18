import glob
import os

list_of_files = glob.glob('*.txt') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
print (latest_file)
temp = latest_file
print("Temp :",temp)

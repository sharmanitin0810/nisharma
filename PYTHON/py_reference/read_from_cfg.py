from configparser import ConfigParser 

configure =  ConfigParser()
print (configure.read('basicConfig.cfg'))
print ("Sections : ", configure.sections()) 
host_list = []

host_list.append(configure.get('BASIC_CONFIG','EMS_IP'))
host_list.append(configure.get('BASIC_CONFIG','LOGS_STRING'))
host_list.append(configure.get('BASIC_CONFIG','INPUT_DATA_PATH'))
#data1 = configure.get('BASIC_CONFIG','LOGS_STRING')
#data2 = configure.get('BASIC_CONFIG','INPUT_DATA_PATH')
#print(data1)
print(host_list[:1])
#print(data2)
#print(data)



# Python program to find SHA256 hexadecimal hash string of a file
import hashlib

sample_hash = "2789f17f0f7da2e44b899ab887c0a5879effabce414e37ed1507bbfd3da9b3db468f4940388fd9959149b2b7f52bceeb20627710d3be8e90a6f98d71edd6cab5" 
filename = input("Enter the input file name: ")
with open(filename,"rb") as f:
    bytes = f.read() # read entire file as bytes
    readable_hash = hashlib.sha512(bytes).hexdigest();
    print(readable_hash)

if str(sample_hash)==str(readable_hash):
	print("Hash sum macthes with the iput hash order")
else:
	print("Not maches")



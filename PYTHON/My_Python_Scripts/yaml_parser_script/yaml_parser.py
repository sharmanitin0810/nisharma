import yaml
import os

def read_and_parse():

	with open('values.yaml') as input_file:
 	 my_dict = yaml.safe_load(input_file)

	 print('1. Parsed Values of Branch : image')
 	 out_img_reg = my_dict["image"]["registry"];print('Image-->registery :', out_img_reg)
	 out_img_repo = my_dict["image"]["repository"];print('Image-->repository :',out_img_repo)
	 out_img_tag = my_dict["image"]["tag"];print('Image-->tag :',out_img_tag);print('\n')

	 print('2. Parsed Values of Branch : volumePermissions')
	 out_vol_reg = my_dict["volumePermissions"]["image"]["registry"];print('Vol_Image ---> registery :',out_vol_reg)
	 out_vol_repo = my_dict["volumePermissions"]["image"]["repository"];print('Vol_Image ---> repository :',out_vol_repo)


if __name__ == "__main__":

	os.system("clear")
	print ("**** Reading and parsing the content of a input file *****");print('\n')
	read_and_parse()

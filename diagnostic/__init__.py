import os
from pathlib import Path
import time
import base64

import sys
sys.path.append(os.getcwd())
from service import api_client

import json

# MARK: Generate bs64
def pdf_to_bs64(path_file,path_destination,filename,delimiter=",",multi_bs64=True):
	"""
	Description:

	Argument:
		path_file(path): path to pdf file for converting;
		path_destination(path): destination path of converted pdf (base64 code);
		filename(str): name of pdf file;
		delimiter(char): char to separated the text informations;
		multi_bs64(bool): generate a mult array file or a single;
	"""	

	extension = ".json"
	list_base64 = []

	for pdf_file in os.listdir(path_file):
		filename_pdf = Path(pdf_file).suffix
		
		if filename_pdf == ".pdf":
			with open(os.path.join(path_file,pdf_file), "rb") as f: data = f.read()
			bs64 = base64.b64encode(data).decode("utf-8-sig")

			if multi_bs64 == False:
				abs_path_destination = os.path.join(path_destination,Path(pdf_file).stem+extension)
				if os.path.isfile(abs_path_destination): os.remove(abs_path_destination)
				time.sleep(3)
				
				with open(abs_path_destination, "w") as f: f.write(str([[2020+1/10,bs64]]).replace("'",'"'))
			else: list_base64.append(bs64)

	list_size = len(list_base64)-1

	if multi_bs64 ==  True:
		filename = filename + extension
		abs_path_destination = os.path.join(path_destination,filename)

		if os.path.isfile(abs_path_destination): os.remove(abs_path_destination)
		time.sleep(3)

	
		with open(abs_path_destination, "w") as f: f.write("[")
		for i in range(len(list_base64)):
			if len(list_base64) == 1:
				with open(abs_path_destination, "a") as f: f.write(str([2020+i/10,list_base64[i]]).replace("'",'"'))
			else:
				if i < list_size: 
					with open(abs_path_destination, "a") as f: f.write(str([2020+i/10,list_base64[i]]).replace("'",'"')+delimiter)
				else: 
					with open(abs_path_destination, "a") as f: f.write(str([2020+i/10,list_base64[i]]).replace("'",'"'))
		
		with open(abs_path_destination, "a") as f: f.write("]")


# MARK: Read bs64 Text File
def execute_diagnostic(genbase,run,online,id):
	"""
	Debug process locally, isolating the error in input data or waited output by another api.

	Args:
		gebnase(bool): Used to generate the base64 file, based on structure: [[year, basecode]];
		run(bool): run api cliente (openAI) request;
		online(bool): Used to controll if will be request data to openAI or a previously saved one;
		id(str): Id came from another API to this to identify the who requests each document;
	"""

	path_result = os.path.join(os.getcwd(),"__result")
	if not os.path.exists:  os.makedirs(path_result)
	#filename = "BALANCETE 2T2024_assinado.json"
	#filename = "DRE 2T2024_assinado.json"
	#filename = "BP_2022.json"
	filename = "bs64.json"

	if genbase:
		#pdf_to_bs64(path_file=os.path.join(os.getcwd(),"_file_test/01_baby/text_flow"),path_destination=os.path.join(os.getcwd(),"_file_test"),filename="bs64",delimiter=",",multi_bs64=False)
		#pdf_to_bs64(path_file=os.path.join(os.getcwd(),"_file_test/01_baby/table"),path_destination=os.path.join(os.getcwd(),"_file_test"),filename="bs64",delimiter=",",multi_bs64=False)
		#pdf_to_bs64(path_file=os.path.join(os.getcwd(),"_file_test/03_caveman/text_flow"),path_destination=os.path.join(os.getcwd(),"_file_test"),filename="bs64",delimiter=",",multi_bs64=False)

		pdf_to_bs64(path_file=os.path.join(os.getcwd(),"_file_test/01_baby/multi"),path_destination=os.path.join(os.getcwd(),"_file_test"),filename="bs64",delimiter=",",multi_bs64=True)

	if run:
		with open(os.path.join(os.getcwd(),"config/config.json")) as jsonfile: config_json = json.load(jsonfile)
		with open(os.path.join(os.getcwd(),r"_file_test",filename), 'r', encoding='utf-8') as file: base64 = json.load(file)
		result = api_client(id=id,base64=base64,config_json=config_json,online=online)

		with open(os.path.join(path_result,"result.json"), "w") as f: json.dump(result, f, indent=4)

execute_diagnostic(genbase=False,run=True,online=False,id="762")
import os

from openai import OpenAI
import time
from datetime import datetime

import json

import sys
sys.path.append(os.getcwd())
import model

#MARK: Debug
def debug_code(message,var=None,debug=False):
	"""
	Description:
		Print messages across the process to verify data behaviour.

	Arg:
		message(str): text to identify the code process the message are about;
		var(any): variable values to validade;
		debug(bool): true print's the messages;
	"""

	if debug is True:
		if not var is None: print(f"[Debug] {message}: {var}")
		else: print(f"[Debug] {message}")


# MARK: Customize Output
# def custom_structure(id,key_name,result_set):
# 	"""
# 	Description:
# 		If you need, there is a friendly output structure to java systems.

# 	Arg:
# 		id(str): extends to systems that uses hash codes instead of numeric codes;
# 		open_ai_output(dict): result from openAI parsing the document based of previously formated response;
# 	"""

# 	final_dictionary = {}
# 	final_dictionary[key_name["k1"]] = id
# 	file = []
# 	data = []

# 	for output in result_set:
# 		#data = {}

# 		#for year, category in output[1].items():
# 		for year, category in output.items():
# 			aux = {}

# 			for item, info in category.items():
# 				sub_lst = []

# 				for k,v in info.items():
# 					sub_lst.append({key_name["k10"]: k, key_name["k11"]: v})
			
# 				aux[item] = sub_lst
# 			data[key_name["k5"]] = year
# 			data[key_name["k6"]] = aux
			
# 		file.append({key_name["k3"]: output[0], key_name["k4"]: data})
# 	final_dictionary[key_name["k2"]] = file

# 	return(final_dictionary)

def custom_structure(id,key_name,result_set):
	"""
	Description:
		Friendly output structure to non pythonic languages e.g java's system based on.

	Arg:
		id(str): extends to systems that uses hash codes instead of numeric codes;
		open_ai_output(dict): result from openAI parsing the document based of previously formated response;
	"""

	final_dictionary = {}
	final_dictionary[key_name["k1"]] = id
	file = []
	

	for output in result_set:
		for year, category in output.items():
			aux = {}
			for item, info in category.items():
				sub_lst = []
				for description, value in info.items():
					sub_lst.append({key_name["k10"]: description, key_name["k11"]: value})
			
				aux[item] = sub_lst			
		file.append({key_name["k3"]: year, key_name["k4"]: aux})
	final_dictionary[key_name["k2"]] = file

	return(final_dictionary)


# MARK:Single Documents
def document_unique(key,key_unique,data,add_mult=True):
	"""
	Description:
		Join each dictionary into a single array;
	Arg:
		key(list): list of dictionary keys;
		key_unique(list): identify unique keys to add in array final result;
		double_data(bool): if true add the firt two key,value of dict, else just the first;
	"""

	result = []
	indexes = sorted([key.index(x) for x in key_unique if key.count(x) == 1])

	for idx in indexes:
		result.append( {list(data[idx].keys())[0]: list(data[idx].values())[0]} )

		if len(list(data[idx].keys())) > 1:
			if int(list(data[idx].keys())[1]) == int(max(key_unique)) and add_mult:
				result.append( {list(data[idx].keys())[1]: list(data[idx].values())[1]} )
	
	return(result)

# MARK: Separated Documents
def document_separated(key, data):	
	"""
	Description:
		If documents are unique just ad then, if separated merge then;
	Arg:
		key(list): list of dictionary keys;
		result_set(list): list of dics returned by openAi's api;
	"""

	check_unique =  [int(x) for x in key]
	double_data = True if check_unique.count(max(check_unique)) < 2 else False
	key_unique = [x for x in key if check_unique.count(x) == 1]
	idx_duplicate = [i for i, val in enumerate(check_unique) if val not in key_unique]
	idx_unique = [i for i, val in enumerate(check_unique) if val in key_unique]
	#data_unique = [data[idx] for idx in idx_unique]
	duplicated_data = [data[idx] for idx in idx_duplicate]

	for i in range(int(len(duplicated_data)/2)):
		year_previous = duplicated_data[i]
		year_current = duplicated_data[i+1]

		for year, inner_dict in year_previous.items():

			for category, inner_dict2 in inner_dict.items():
				if category not in year_current[year]: year_current[year][category] = {}

				for item, val in inner_dict2.items():
					if item not in year_current[year][category]: year_current[year][category][item] = val
		
		duplicated_data.pop(i)

	result = document_unique(key=key,key_unique=key_unique,data=data,add_mult=double_data)
	result.extend(duplicated_data)

	return(result)


# MARK:Data Merge
def document_data_merge(result_set):
	"""
	Description:
		Identify which type of structure is: unique documents, unique and separated documents of same context or document unify documents (more then 2 years);
	Arg:
		result_set(list[3]): 
			[0](list): keys corresponding to document years (ordered as [1]);
			[1](dict): list of dics returned by openAi's api;
			[3](int): count of unique keys;
	"""

	year = result_set[0]
	y_complete = [float(x) for x in year]
	y_distinct = [x for x in y_complete if y_complete.count(x) == 1]

	data = result_set[1]
	separated_document = result_set[2]
	result = []

	if len(year) == len(set([int(x) for x in y_complete])):
		if separated_document == 0: result = document_unique(key=y_complete,key_unique=y_distinct,data=data)
		else: result = [{k: v} for k,v  in data[0].items()]
	else: result = document_separated(key=y_complete,data=data)
	
	return(result)


# MARK: openIA Request 
def open_ia_request(base64,token,response_structure,filename,gpt_version,wait_time,debug):
	"""
	Description:
		Send the bs64 file to openIA API and request the parsed data based on model structure.

	Arg:
		base64(list[[float, str]...]): [0] is the document's year, [1] is the base code;
		token(str): token access to openAI requests;
		response_structure(str): json structure to insure correct data format when requesting parsing from openIA API;
		filename(str): name of file send as information in request body;
		gpt_version(str): used different versions to control the requests costs/quality of receveid data;
		wait_time(int): seconds to wait between request openAI API has token time limits between requests;
		debug(bool): print informations of key code parts to check data behaviour;
	"""

	result_set = []
	path_result = os.path.join(os.getcwd(),"__result")
	client = OpenAI(api_key=token)
	with open(response_structure, 'r') as jfile:  rf_schema =  json.load(jfile)

	i = 0
	for array in base64:
		debug_code(f"GPT's read bs64 [[{array[0]}],[{array[1][:20]}...]] request", i, debug)
		api_start = time.time()

		msg = [
			{"role": "system", "content": "Você é um especialista em contabilidade. Você é capaz de localizar as categorias listadas abaixo. Após a extração, você deve devolver os dados no formato JSON"},
			{"role": "user", "content": [
					{"type": "file", "file":  {"filename": f"{filename}", "file_data": f"data:application/pdf;base64,{array[1]}",}	},
					{"type": "text", "text": "Comece analisando duas vezes o documento inteiro. Procure pelas demonstrações contábeis sintetizadas referente os anos da estrutura json fornecida. Utilize a estrutura fornecida para todos os anos presentes no documento"},
				]
			},
		]

		open_ai_output = client.chat.completions.create(
			model = gpt_version,
			messages=msg,
			response_format={
				"type": "json_schema",
				"json_schema": {
					"name": "gpt_parser",
					"schema": rf_schema,
					"strict": False,
				}
			}
		)

		result = json.loads(open_ai_output.choices[0].message.content)
	
		debug_code(message=f"request duration (sec): {(time.time() - api_start)}", debug=debug)
		time.sleep(wait_time)

		debug_code(message=f"request duration (sec): {(time.time() - api_start)}", debug=debug)
		result_set.append((array[0],result))
		i += 1

	if debug:
		path_response_result = os.path.join(path_result,"open_ai_output.json")
		if os.path.exists(path_response_result):  os.remove(path_response_result)	
		with open(path_response_result, "w") as jsf: json.dump(result_set, jsf, indent=4)
		
	return(result_set)

# MARK: Response Format
def request_format(main_key,property,response_structure):
	"""
	Function to format the send structure to openIA. Due to tests, a solid structure implies in less token in addition to an more accurate responses.
	
	Arg: 
		main_key(list);
		property(dict): {name_key: model.object};
		response_strucutre(path): path to save de structure;

	"""
	
	dct = {
		"title": "DocumentParser"
		,"type": "object"
		,"additionalProperties": bool(0)
		,"properties": {}
		,"required": main_key
	}

	for x in main_key:
		dct["properties"][x] = {
			"title": x
			,"type": "object"
			,"additionalProperties": bool(0)
			,"properties": property
			,"required": list(property.keys())
		}

	if os.path.exists(response_structure): os.remove(response_structure)
	time.sleep(5)
	with open(response_structure, "w") as f: json.dump(dct, f, indent=4)


# MARK: openIA Request
def api_client(id,base64,config_json,online=True):
	"""
	Description:
		Send the bs64 file to openIA API and request the parsed data based on model structure.

	Arg:
		id(str): extends to systems that uses hash codes instead of numeric codes;
		base64(list[[float, str]...]): [0] is the document's year, [1] is the base code;
		online(bool): Used to controll if will be request data to openAI or a previously saved one;
	"""

	response_structure = os.path.join(os.getcwd(),"config/response_format.json")
	year = int(datetime.now().year)
	main_key = [str(i) for i in range(year-3,year+1,1)]
	debug = config_json["debug"]
	path_result = os.path.join(os.getcwd(),"__result")	
	cof = config_json["custom_output_format"]
	property = {
		cof["k7"]: model.Asset.model_json_schema()
		,cof["k8"]: model.Liabilities.model_json_schema()
		,cof["k9"]: model.IncomeStatement.model_json_schema()
	}
	base64 = [[float(year), bs_code] for year, bs_code in base64]

	start = time.time()

	if not os.path.exists(response_structure) or config_json["response_format"]:
		request_format(main_key=main_key,property=property,response_structure=response_structure)
	else:
		with open(response_structure, 'r') as jfile: rf_schema =  json.load(jfile)
		
		if int(list(rf_schema["properties"].keys())[-1]) < year:
			request_format(main_key=main_key,property=property,response_structure=response_structure)

	if online:
		result_set = open_ia_request(
			 base64 = base64
			,token = config_json["token"]
			,response_structure = response_structure
			,filename = config_json["filename"]
			,gpt_version = config_json["gpt_version"]
			,wait_time = config_json["sec_wait_between_request"]
			,debug = debug
		)
	else:
		#with open(os.path.join(path_result,"open_ai_output.json")) as jsf: result_set = json.load(jsf)
		#with open(os.path.join(path_result,r"sintetic/result_set_alpha.json")) as jsf: result_set = json.load(jsf)
		#with open(os.path.join(path_result,r"sintetic/result_set_beta.json")) as jsf: result_set = json.load(jsf)
		#with open(os.path.join(path_result,r"sintetic/result_set_beta_II.json")) as jsf: result_set = json.load(jsf)
		with open(os.path.join(path_result,r"sintetic/result_set_omega.json")) as jsf: result_set = json.load(jsf)
	
	result_set = document_data_merge(result_set)

	if debug: 
		with open(os.path.join(path_result,r"input_custom_structure.json"),"w") as jsf:  json.dump(result_set, jsf, indent=4)
			
	final_dictionary = custom_structure(id=id,key_name=config_json["custom_output_format"],result_set=result_set)
	with open(os.path.join(path_result,"result.json"), "w") as f: json.dump(final_dictionary, f, indent=4)
	debug_code(message=f"Total Request duration (sec): {(time.time() - start)}",debug=debug)

	return(final_dictionary)
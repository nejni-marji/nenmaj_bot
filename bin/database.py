#!/usr/bin/env python
import json
from os.path import isfile

def load(path):
	if isfile(path):
		json_file = open(path, 'r')
		database = json.loads(json_file.read())
		json_file.close()
		return database

def dump(path, database):
	json_file = open(path, 'w')
	json_file.write(json.dumps(database))
	json_file.close()
	return None

def start(path, default):
	if isfile(path):
		json_file = open(path, 'r')
		database = json.loads(json_file.read())
		json_file.close()
		return database
	else:
		return default

#!/usr/bin/env python3
from os.path import dirname

import bin.database as db
db_file = dirname(__file__) + '/../private/config.json'
configs = db.load(db_file)
#print(configs)

def set_conf(key, value, database = configs):
	if type(key) == str:
		key = key.split('.')

	if key[0] in database:

		if len(key) > 1:
			return set_conf(key[1:], value, database[key[0]])
		database[key[0]] = value
		db.dump(db_file, configs)
		return None

	if len(key) > 1:
		database[key[0]] = {}
		return set_conf(key[1:], value, database[key[0]])
	database[key[0]] = value
	db.dump(db_file, configs)

def get_conf(key, database = configs):
	if type(key) == str:
		key = key.split('.')
	if key[0] in database:
		if len(key) > 1:
			return get_conf(key[1:], database[key[0]])
		return database[key[0]]
	return None

def del_conf(key, database = configs):
	if type(key) == str:
		key = key.split('.')

	if key[0] in database:

		if len(key) > 1:
			return del_conf(key[1:], database[key[0]])
		database.pop(key[0])
		db.dump(db_file, configs)
		return None

	if len(key) > 1:
		database[key[0]] = {}
		return del_conf(key[1:], database[key[0]])
	try:
		database.pop(key[0])
		db.dump(db_file, configs)
	except:
		return None

def top_conf():
	return configs

def check_conf(key, astype, default):
	value = get_conf(key)
	if astype == bool:
		if value in ['1', 'on', 'True', 'true', 'yes']:
			return True
		if value in ['0', 'off', 'False', 'false', 'no']:
			return False
		return default
	if astype == int:
		try:
			return int(value)
		except (TypeError, ValueError):
			return default
	if astype == str:
		try:
			return str(value)
		except:
			return default
	return default
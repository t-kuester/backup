#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Data model for simple Backup tool.
by Tobias Küster, 2016

Data model for backup tool, as well as helper methods for reading/writing the
model to JSON files.
"""

# TODO makes dates in JSON file human-readable

from config import *
import json

class Directory:
	"""Class representing a single directory.
	"""
	
	def __init__(self, path, archive_type=None, last_backup=0, last_changed=0, include=False):
		self.path = path
		self.archive_type = archive_type or DEFAULT_ARCHIVE_TYPE
		self.last_backup = last_backup
		self.last_changed = last_changed
		self.include = include
		
	def __repr__(self):
		return "Directory({}, {}, {}, {}, {})".format(self.path, self.archive_type, 
				self.last_backup, self.last_changed, self.include)
				

class Configuration:
	"""Class representing the entire configuration for the backup tool.
	"""
	
	def __init__(self, target_dir, name_pattern, directories=None):
		self.target_dir = target_dir
		self.name_pattern = name_pattern
		self.directories = directories or []
		
	def __repr__(self):
		return "Configuration({}, {}, {})".format(self.target_dir, 
				self.name_pattern, self.directories)


def create_initial_config():
	"""Create initial configuration using default values.
	"""
	config = Configuration(DEFAULT_TARGET_DIR, DEFAULT_NAME_PATTERN)
	config.directories.append(Directory("/path/to/directory"))
	return config
	

def load_from_json(json_location):
	"""Load backup configuration from JSON file.
	"""
	with open(json_location, "r") as f:
		config = json.load(f)
		config["directories"] = [Directory(**d) for d in config["directories"]]
		return Configuration(**config)
	
	
def write_to_json(json_location, configuration):
	"""Store backup configuration in JSON file.
	"""
	with open(json_location, "w") as f:
		config = dict(configuration.__dict__)
		config["directories"] = [d.__dict__ for d in config["directories"]]
		json.dump(config, f, sort_keys=True, indent=4, separators=(',', ': '))


def test():
	"""Just for testing basic creation and JSON serialization.
	"""
	TEST_CONFIG = "test_config.json"
	conf = create_initial_config()
	conf.directories.extend([Directory("/path/to/foo", "zip", 1, 2), 
	                         Directory("/path/to/bar", "tar.gz", 3, 4), 
			                 Directory("/path/to/blub", "tar", 5, 6)])
	write_to_json(TEST_CONFIG, conf)
	conf2 = load_from_json(TEST_CONFIG)
	print(conf)
	print(conf2)
	assert str(conf) == str(conf2)

# testing stuff
if __name__=="__main__":
	test()

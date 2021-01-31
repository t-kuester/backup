#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Data model for simple Backup tool.
by Tobias Küster, 2016

Data model for backup tool, as well as helper methods for reading/writing the
model to JSON files.
"""

import json


class Directory:
	"""Class representing a single directory.
	"""
	
	def __init__(self, path, archive_type, last_backup=None, last_changed=None, include=False):
		self.path = path
		self.archive_type = archive_type
		self.last_backup = last_backup
		self.last_changed = last_changed
		self.include = include
		
	def __repr__(self):
		return "Directory(%r, %r, %r, %r, %r)" % (self.path, self.archive_type, 
				self.last_backup, self.last_changed, self.include)
				

class Configuration:
	"""Class representing the entire configuration for the backup tool.
	"""
	
	def __init__(self, target_dir, name_pattern, directories=None):
		self.target_dir = target_dir
		self.name_pattern = name_pattern
		self.directories = directories or []
		
	def __repr__(self):
		return "Configuration(%r, %r, %r)" % (self.target_dir, 
				self.name_pattern, self.directories)


def load_from_json(json_string: str) -> Configuration:
	"""Load backup configuration from JSON string.
	"""
	config = json.loads(json_string)
	config["directories"] = [Directory(**d) for d in config["directories"]]
	return Configuration(**config)
	
	
def write_to_json(configuration: Configuration) -> str:
	"""Store backup configuration in JSON file.
	"""
	config = dict(configuration.__dict__)
	config["directories"] = [d.__dict__ for d in config["directories"]]
	return json.dumps(config, indent=4)


# TESTING

def test():
	"""Just for testing basic creation and JSON serialization.
	"""
	conf = Configuration("target-dir", "name-pattern")
	conf.directories.extend([Directory("/path/to/foo", "zip", 1, 2), 
	                         Directory("/path/to/bar", "tar.gz", 3, 4), 
			                 Directory("/path/to/blub", "tar", 5, 6)])
	string = write_to_json(conf)
	conf2 = load_from_json(string)
	print(conf)
	print(string)
	assert str(conf) == str(conf2)
	assert string == write_to_json(conf2)


if __name__=="__main__":
	test()

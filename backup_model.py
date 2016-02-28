#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Data model for simple Backup tool.
by Tobias Küster, 2016

Data model for backup tool, as well as helper methods for reading/writing the
model to JSON files.
"""

class Directory:
	"""Class representing a single directory.
	"""
	
	def __init__(self, path, last_backup, archive_type, last_changed=None, include=False):
		self.path = path
		self.last_backup = last_backup
		self.archive_type = archive_type
		self.last_changed = last_changed
		self.include = include
		
	def __repr__(self):
		return "Directory({}, {}, {}, {}, {})".format(self.path, self.last_backup, 
				self.archive_type, self.last_changed, self.include)
				

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


def load_from_json(json_location):
	"""Load backup configuration from JSON file.
	"""
	pass
	
def write_to_json(json_location, configuration):
	"""Store backup configuration in JSON file.
	"""
	pass

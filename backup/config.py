# -*- coding: utf8 -*-

"""
Global configuration for simple Backup tool.
by Tobias Küster, 2016

This file contains some variables for global configuration, such as some
useful defaults etc., as well as code for reading and writing the configuration
files to the ~/.config directory.
"""

import os
from contextlib import contextmanager

from backup_model import load_from_json, write_to_json, Configuration


USER_DIR = os.environ["HOME"]
CONFIG_PATH = os.path.join(USER_DIR, ".config", "t-kuester")
CONFIG_FILE = os.path.join(CONFIG_PATH, "backup.json")

DEFAULT_TARGET_PATTERN = "~/BACKUP/{parent}/{dirname} {date}{inc}"
DEFAULT_ARCHIVE_TYPE = "zip"


@contextmanager
def open_config(json_location=CONFIG_FILE):
	"""Open configuration file at given location, or create a new default configuration
	in this place if none exists; then save again to that same file after the 'with' block.
	"""
	try:
		with open(json_location, "r") as f:
			conf = load_from_json(f.read())
	except Exception as e:
		parent, _ = os.path.split(json_location)
		os.makedirs(parent, exist_ok=True)
		conf = Configuration(DEFAULT_TARGET_PATTERN, [])

	yield conf
	
	with open(json_location, "w") as f:
		f.write(write_to_json(conf))
		f.write("\n")

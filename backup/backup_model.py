# -*- coding: utf8 -*-

"""
Data model for simple Backup tool.
by Tobias Küster, 2016

Data model for backup tool, as well as helper methods for reading/writing the
model to JSON files.
"""

import json
import os
import re

from dataclasses import dataclass
from typing import Iterable, List


P_DATE, P_TIME, P_PRNT, P_DIRN, P_INC = "{date}", "{datetime}", "{parent}", "{dirname}", "{inc}"
VALID_PLACEHOLDERS = [P_DATE, P_TIME, P_PRNT, P_DIRN, P_INC]
REQUIRED_PLACEHOLDERS = [P_DIRN]


@dataclass
class Directory:
	"""Class representing a single directory.
	"""

	path: str
	archive_type: str
	last_backup: float = -1.0
	include: bool = False
	incremental: bool = False

	def check_path(self) -> bool:
		"""Check whether the given path is a valid directory."""
		return os.path.isdir(self.path)

	def iter_files(self) -> Iterable[str]:
		"""Iterate all (nested) fiels in the directory, yielding full absolute paths."""
		return (os.path.join(d, f) for d, _, fs in os.walk(self.path) for f in fs)

	def iter_modified(self) -> Iterable[str]:
		"""Iterate modified files only."""
		return (f for f in self.iter_files() if os.path.getmtime(f) > self.last_backup)

	def iter_include(self) -> Iterable[str]:
		"""Iterate all or modified fiels, depending on whether it is a incremental backup."""
		return self.iter_modified() if self.incremental else self.iter_files()

	def update_include(self):
		"""Update this Directory's 'include' flag based on last modification time."""
		self.include = any(self.iter_modified())


@dataclass
class Configuration:
	"""Class representing the entire configuration for the backup tool.
	"""

	target_pattern: str
	directories: List[Directory]

	def check(self):
		"""Check whether target_pattern is valid and all Directories point to actual
		directories; raise exceptions if any of this does not apply.
		"""
		placeholders = re.findall(r"\{.*?\}", self.target_pattern)
		invalid = [p for p in placeholders if p not in VALID_PLACEHOLDERS]
		if invalid:
			raise Exception(f"Invalid Placeholders: {invalid}")
		missing = [p for p in REQUIRED_PLACEHOLDERS if p not in placeholders]
		if missing:
			raise Exception(f"Missing Required Placeholders: {missing}")
		for directory in self.directories:
			if not directory.check_path():
				raise Exception(f"{directory.path} is not a valid directory")

	def update_includes(self):
		"""Update 'include' flag of all contained directories."""
		for directory in self.directories:
			directory.include = directory.check_path() and any(directory.iter_modified())


def load_from_json(json_string: str) -> Configuration:
	"""Load backup configuration from JSON string.
	"""
	config = json.loads(json_string)
	config["directories"] = [Directory(**d) for d in config["directories"]]
	return Configuration(**config)


def write_to_json(conf: Configuration) -> str:
	"""Store backup configuration in JSON file.
	"""
	config = dict(conf.__dict__)
	config["directories"] = [d.__dict__ for d in config["directories"]]
	return json.dumps(config, indent=4)

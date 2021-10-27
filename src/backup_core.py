# -*- coding: utf8 -*-

"""
Core Components for simple Backup tool.
by Tobias Küster, 2016

This module contains the algorithms and the logic for actually creating the
backup. It can also be used for creating a backup from command line. Besides
the actual backup-creation, this also provides helper methods for determining
when a file was changed and whether a new backup is due.
"""

import os
import re
import time
import zipfile
import tarfile
from datetime import datetime as dt
from typing import Iterable

import backup_model
from backup_model import Directory, Configuration
import config


TYPE_ZIP = "zip"
TYPE_TAR = "tar"
KNOWN_TYPES = (TYPE_ZIP, TYPE_TAR)


# BACKUP CREATION

def perform_backup_iter(conf: Configuration) -> Iterable[str]:
	"""Perform the backup, creating archive files of all directories to be
	included in the backup and moving those archives to the appointed target.
	This function is a generator/iterator, yielding after each directory.
	"""
	for directory in conf.directories:
		if directory.include and any(directory.iter_include()):
			yield f"Backing up {directory.path}"
			backup_directory(conf, directory)
			directory.last_backup = time.time()
		else:
			yield f"Skipping {directory.path}"
	yield "Done"


def backup_directory(conf: Configuration, directory: Directory):
	"""Perform the backup for a single directory and move the resulting archive
	to the given target directory.
	"""
	target_file = get_target_file(conf, directory)
	
	tgt_parent, _ = os.path.split(target_file)
	os.makedirs(tgt_parent, exist_ok=True)
	
	archive_actions = {
		TYPE_ZIP: create_zip,
		TYPE_TAR: create_tar
	}
	function = archive_actions[directory.archive_type]
	archive_file = function(directory, target_file)
	

def create_zip(directory: Directory, target_file: str):
	"""Create zip file using given filename containing the directory to_compress
	and all of its files.
	"""
	with zipfile.ZipFile(target_file + ".zip", mode="w") as zip_file:
		for filepath in directory.iter_include():
			zip_file.write(filepath)
	
	
def create_tar(directory: Directory, target_file: str):
	"""Create tar file using given filename containing the directory to_compress
	and all of its files.
	"""
	with tarfile.TarFile(target_file + ".tar", mode="w") as tar_file:
		for filepath in directory.iter_include():
			tar_file.add(filepath)


# HElPER FUNCTIONS

def get_target_file(conf: Configuration, directory: Directory) -> str:
	"""Substitute placeholders and normalize file name, i.e. replace leading '.'
	(hidden files) with '_', but only in directory name, not in target path,
	replace '~' with home dir, and replace multiple '/' with single '/'.
	"""
	src_parent, src_dir = os.path.split(re.sub(r"(?<=/)\.", "_", directory.path))
	placeholders = {
		backup_model.P_DATE: get_date(),
		backup_model.P_TIME: get_date(add_time=True),
		backup_model.P_PRNT: src_parent,
		backup_model.P_DIRN: src_dir,
		backup_model.P_INC: "_inc" if directory.incremental else "",
	}
	target_file = conf.target_pattern
	target_file = re.sub(r"^~", config.USER_DIR, target_file)
	target_file = re.sub(r"\{.*?\}", lambda m: placeholders[m.group()], target_file)
	target_file = re.sub(r"/+", "/", target_file)
	return '.'.join((target_file, directory.archive_type))


def get_date(timestamp=None, add_time=False) -> str:
	"""Get uniformly formatted current date.
	"""
	pattern = "%Y-%m-%d %H:%M:%S" if add_time else "%Y-%m-%d"
	return (dt.now().strftime(pattern) if timestamp is None else
	        "never" if timestamp < 0 else
	        dt.fromtimestamp(timestamp).strftime(pattern))


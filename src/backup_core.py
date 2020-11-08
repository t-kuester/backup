#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Core Components for simple Backup tool.
by Tobias Küster, 2016

This module contains the algorithms and the logic for actually creating the
backup. It can also be used for creating a backup from command line. Besides
the actual backup-creation, this also provides helper methods for determining
when a file was changed and whether a new backup is due.
"""

import os
import shutil
import zipfile
import tarfile
from datetime import datetime as dt
from typing import Iterable

import backup_model
from backup_model import Directory, Configuration


TYPE_ZIP = "zip"
TYPE_TAR = "tar"
KNOWN_TYPES = (TYPE_ZIP, TYPE_TAR)


def determine_last_changes(directory: Directory) -> str:
	"""Determine when has been the last time any of the files in the given
	directory have been changed.
	"""
	last_change = max(os.path.getmtime(f) for f in all_files(directory.path))
	directory.last_changed = get_date(last_change, add_time=True)
	return directory.last_changed
	
	
def determine_include(directory: Directory) -> bool:
	"""Determine whether to include the given directory in the next backup,
	based on the time of the last backup and the time of the last change.
	"""
	backup, change = directory.last_backup, directory.last_changed
	directory.include = bool(not (backup and change) or backup < change)
	return directory.include


def calculate_includes(config: Configuration):
	"""Determine time of last change and consequently whether to include
	each directory of the given backup configuration.
	"""
	for directory in config.directories:
		determine_last_changes(directory)
		inc = determine_include(directory)
		print("including", directory.path, inc)


# BACKUP CREATION

def perform_backup(config: Configuration):
	"""Perform the backup, creating archive files of all directories to be
	included in the backup and moving those archives to the appointed target.
	Like below, but performing the entire backup in one go
	"""
	for s in perform_backup_iter(config):
		print(s)
		
		
def perform_backup_iter(config: Configuration):
	"""Perform the backup, creating archive files of all directories to be
	included in the backup and moving those archives to the appointed target.
	This function is a generator/iterator, yielding after each directory.
	"""
	target_dir = config.target_dir.format(date=get_date())
	if target_dir.startswith("~"):
		target_dir = os.environ["HOME"] + target_dir[1:]
	if not os.path.isdir(target_dir):
		os.makedirs(target_dir)
	for directory in config.directories:
		if directory.include:
			yield f"Backing up {directory.path}"
			backup_directory(directory, config.name_pattern, target_dir)
			directory.last_backup = get_date(add_time=True)
		else:
			yield f"Skipping {directory.path}"
	yield "Done"


def backup_directory(directory: Directory, name_pattern: str, target_dir: str):
	"""Perform the backup for a single directory and move the resulting archive
	to the given target directory.
	"""
	# construct target file name
	parent, dirname = os.path.split(directory.path)
	filename = name_pattern.format(parent=parent, dirname=norm(dirname), date=get_date())
	# create archive file
	archive_actions = {TYPE_ZIP: create_zip, TYPE_TAR: create_tar}
	archive = archive_actions[directory.archive_type](filename, norm(directory.path))
	# move archive file to target directory
	shutil.move(archive, target_dir)


def create_zip(filename: str, to_compress: str) -> str:
	"""Create zip file using given filename containing the directory to_compress
	and all of its files.
	"""
	with zipfile.ZipFile(filename + ".zip", mode="w") as zip_file:
		for filepath in all_files(to_compress):
			zip_file.write(filepath)
		return filename + ".zip"
	
	
def create_tar(filename: str, to_compress: str) -> str:
	"""Create tar file using given filename containing the directory to_compress
	and all of its files.
	"""
	with tarfile.TarFile(filename + ".tar", mode="w") as tar_file:
		for filepath in all_files(to_compress):
			tar_file.add(filepath)
		return filename + ".tar"


# HElPER FUNCTIONS

def all_files(path: str) -> Iterable[str]:
	"""Generate all files in a given directory.
	"""
	return (os.path.join(d, f) for d, _, fs in os.walk(path) for f in fs)


def get_date(timestamp=None, add_time=False) -> str:
	"""Get uniformly formatted current date.
	"""
	pattern = "%Y-%m-%d %H:%M:%S" if add_time else "%Y-%m-%d"
	return (dt.fromtimestamp(timestamp) if timestamp else dt.now()).strftime(pattern)


def norm(dirname: str) -> str:
	"""Remove "." from filename and replace it with "_"
	"""
	return dirname.replace(".", "_")


def main():
	"""This method is executed when started from command line.
	- load config
	- check for last changes in directory
	- perform backup
	- save updated config
	"""
	import config
	with config.open_config() as conf:
		calculate_includes(conf)
		perform_backup(conf)
	
	
if __name__ == "__main__":
	main()

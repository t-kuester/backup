#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Core Components for simple Backup tool.
by Tobias Küster, 2016

This module contains the algorithms and the logic for actually creating the
backup. It can also be used for creating a backup from command line.
"""

import os
import shutil
import zipfile
import tarfile
from datetime import datetime
from typing import Iterable

import backup_model
from backup_model import Directory, Configuration


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
TYPE_ZIP = "zip"
TYPE_TAR = "tar"
KNOWN_TYPES = (TYPE_ZIP, TYPE_TAR)

def determine_last_changes(directory: Directory) -> str:
	"""Determine when has been the last time any of the files in the given
	directory have been changed.
	"""
	last_changed = 0
	for subdir, _, files in os.walk(directory.path):
		for filename in files:
			full_path = os.path.join(subdir, filename)
			changed = os.path.getmtime(full_path)
			last_changed = max(last_changed, changed)

	directory.last_changed = datetime.fromtimestamp(last_changed).strftime(DATE_FORMAT)
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


def perform_backup(config: Configuration):
	"""Perform the backup, creating archive files of all directories to be
	included in the backup and moving those archives to the appointed target.
	"""
	target_dir = config.target_dir.format(date=get_date())
	print("Target dir is", target_dir)
	if not os.path.isdir(target_dir):
		os.makedirs(target_dir)
	for directory in config.directories:
		if directory.include:
			print("Backing up", directory)
			backup_directory(directory, config.name_pattern, target_dir)
			directory.last_backup = datetime.now().strftime(DATE_FORMAT)
		else:
			print("skipping", directory)


def backup_directory(directory: Directory, name_pattern: str, target_dir: str):
	"""Perform the backup for a single directory and move the resulting archive
	to the given target directory.
	"""
	# construct target file name
	path = os.path.split(directory.path)
	parent, dirname = path[-2:]
	date = get_date()
	filename = name_pattern.format(parent=parent, dirname=dirname, date=date)
	# create archive file
	archive_actions = {TYPE_ZIP: create_zip, TYPE_TAR: create_tar}
	archive = archive_actions[directory.archive_type](filename, directory.path)
	# move archive file to target directory
	shutil.move(archive, target_dir)


def create_zip(filename: str, to_compress: str) -> str:
	"""Create zip file using given filename containing the directory to_compress
	and all of its files.
	"""
	zip_file = zipfile.ZipFile(filename + ".zip", mode="w")
	for filepath in all_files(to_compress):
		zip_file.write(filepath)
	zip_file.close()
	return filename + ".zip"
	
	
def create_tar(filename: str, to_compress: str) -> str:
	"""Create tar file using given filename containing the directory to_compress
	and all of its files.
	"""
	tar_file = tarfile.TarFile(filename + ".tar", mode="w")
	for filepath in all_files(to_compress):
		tar_file.add(filepath)
	tar_file.close()
	return filename + ".tar"


def all_files(path: str) -> Iterable[str]:
	"""Generate all files in a given directory.
	"""
	return (os.path.join(d, f) for d, _, fs in os.walk(path) for f in fs)


def get_date() -> str:
	"""Get uniformly formatted current date.
	"""
	return datetime.now().strftime("%Y-%m-%d")


def main():
	"""This method is executed when started from command line.
	- load config
	- check for last changes in directory
	- perform backup
	- save updated config
	"""
	import config
	
	with config.open_config(config.CONFIG_FILE) as conf:
		
		for directory in conf.directories:
			d = determine_last_changes(directory)
			print("last changed", directory, d)
		
		calculate_includes(conf)
		perform_backup(conf)
	
	print("Done.")
	
	
if __name__ == "__main__":
	main()

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


# BACKUP CREATION

def perform_backup(config: Configuration):
	"""Perform the backup, creating archive files of all directories to be
	included in the backup and moving those archives to the appointed target.
	Like below, but performing the entire backup in one go
	"""
	for s in perform_backup_iter(config):
		print(s)
		
		
def perform_backup_iter(config: Configuration) -> Iterable[str]:
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
	src_parent, src_dir = os.path.split(directory.path)
	target_path = name_pattern.format(parent=norm(src_parent), dirname=norm(src_dir), date=get_date())
	target_path_in_target_dir = os.path.join(target_dir, target_path.lstrip("/"))
	tgt_parent, tgt_file = os.path.split(target_path_in_target_dir)
	
	# cd to parent, then only zip dirname
	os.chdir(src_parent)
	
	# create archive file
	archive_actions = {TYPE_ZIP: create_zip, TYPE_TAR: create_tar}
	function = archive_actions[directory.archive_type]
	archive_file = function(tgt_file, src_dir)
	
	# move archive file to target directory
	os.makedirs(tgt_parent, exist_ok=True)
	shutil.move(archive_file, tgt_parent)
	# TODO instead of moving the file to the target dir, just create it in the target dir!
	# TODO check if file exists, then either rename it, or not compress it at all
	#      right now, it compresses the file and then leaves it where it is,
	#      which might be just anywhere


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
	return (dt.now().strftime(pattern) if timestamp is None else
	        "never" if timestamp < 0 else
	        dt.fromtimestamp(timestamp).strftime(pattern))


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

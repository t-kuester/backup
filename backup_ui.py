#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""User interface for simple Backup tool.
by Tobias Küster, 2016

- shows directories to compress, time of last backup, time of last changed, 
  archive type, include in next backup, total file size, etc.
- global options: target directory, add/remove directory, file name patterns
"""

import tkinter
import backup_model, config


class BackupFrame(tkinter.Frame):
	
	def __init__(self, root, conf):
		super().__init__(root)
		self.config = conf
		
		self.grid()

		# Target directory for creating backups
		self.target =  tkinter.StringVar(value=self.config.target_dir)
		tkinter.Label(self, text="Target Directory").grid(row=1, column=0)
		tkinter.Entry(self, textvariable=self.target).grid(row=1, column=1)
		
		# name pattern for backup directory
		self.pattern = tkinter.StringVar(value=self.config.name_pattern)
		tkinter.Label(self, text="Name Pattern").grid(row=2, column=0)
		tkinter.Entry(self, textvariable=self.pattern).grid(row=2, column=1)
		
		# Buttons: Add Directory, create Backup
		tkinter.Button(self, text="Add Directory", command=self.add_directory).grid(row=3, column=0)
		tkinter.Button(self, text="Create Backup", command=self.create_backup).grid(row=3, column=1)
		
		# Info and Config Component for each Directory
		for d in self.config.directories:
			print(d)
			# list of directories: name, last backup, size, changed
			# checkbuttons: include, compress, button: remove
		
	
	def add_directory(self):
		print("adding direcory")
		
	def remove_directory(self, selected):
		print("remove dir", selected)
	
	def create_backup(self):
		print("creating backup...")
		


if __name__ == "__main__":
	# TODO get config file from params or use default
	config_file = config.DEFAULT_CONFIG_LOCATION
	conf = backup_model.load_from_json(config_file)
	print(conf)
	root = tkinter.Tk()
	frame = BackupFrame(root, conf)
	root.mainloop()

	conf.target_dir = frame.target.get()
	conf.name_pattern = frame.pattern.get()
	
	print("writing config...")
	backup_model.write_to_json(config_file, conf)
	print("done")


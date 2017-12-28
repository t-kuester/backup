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
		for i, d in enumerate(self.config.directories):
			print(d)
			# list of directories: name, last backup, size, changed
			# checkbuttons: include, compress, button: remove
			panel = DirectoryPanel(self)
			panel.grid(row=4+i, column=0, columnspan=2, sticky="EW")
			panel.set_directory(d)
		
	
	def add_directory(self):
		print("adding direcory")
		
	def remove_directory(self, selected):
		print("remove dir", selected)
	
	def create_backup(self):
		print("creating backup...")


class DirectoryPanel(tkinter.Canvas):

	def __init__(self, *args, **kwargs):
		tkinter.Canvas.__init__(self, *args, **kwargs)

		self.pathvar = tkinter.StringVar()
		self.backupvar = tkinter.StringVar()
		self.changevar = tkinter.StringVar()
		self.includevar = tkinter.IntVar()

		self.make_entry("Path", 0, tkinter.Entry(self, textvariable=self.pathvar))
		self.make_entry("Last Backup", 1, tkinter.Label(self, textvariable=self.backupvar))
		self.make_entry("Last Change", 2, tkinter.Label(self, textvariable=self.changevar))
		self.make_entry(None, 3, tkinter.Checkbutton(self, text="Include?", variable=self.includevar))
		# TODO archive type

	def make_entry(self, label, row, widget):
		tkinter.Label(self, text=label).grid(row=row, column=0, sticky="NW")
		widget.grid(row=row, column=1, sticky="W")

	def set_directory(self, directory):
		self.directory = directory
		self.pathvar.set(directory.path)
		self.backupvar.set(directory.last_backup)
		self.changevar.set(directory.last_changed)
		self.includevar.set(directory.include)
		# TODO update widgets

	# TODO callback for updating directory object


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
	
	# TODO use with or try/except/finally to ensure writing to file
	print("writing config...")
	backup_model.write_to_json(config_file, conf)
	print("done")

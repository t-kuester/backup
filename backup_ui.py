#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""User interface for simple Backup tool.
by Tobias Küster, 2016

- shows directories to compress, time of last backup, time of last changed, 
  archive type, include in next backup, total file size, etc.
- global options: target directory, add/remove directory, file name patterns
"""

import tkinter, tkinter.messagebox, tkinter.filedialog
import backup_core, backup_model, config
import os


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
		
		# Buttons: Add/Remove Directory
		tkinter.Button(self, text="Add Directory", command=self.add_directory).grid(row=3, column=0, sticky="EW")
		tkinter.Button(self, text="Remove Directory", command=self.remove_directory).grid(row=3, column=1, sticky="EW")
		
		# Optionmenu with directories in the config
		self.selected = tkinter.StringVar()
		self.selected.trace("w", self.update_selected)
		self.directories = tkinter.OptionMenu(self, self.selected, *(d.path for d in self.config.directories))
		self.directories.grid(row=4, column=0, columnspan=2, sticky="EW")
		
		# DirectoryPanel showing the selected directory
		self.panel = DirectoryPanel(self)
		self.panel.grid(row=5, column=0, columnspan=2, sticky="EW")

		# Buttons: Auto-Include, Make Backup
		tkinter.Button(self, text="Auto-Include", command=self.auto_include).grid(row=6, column=0)
		tkinter.Button(self, text="Create Backup", command=self.create_backup).grid(row=6, column=1)

	def get_selected(self):
		p = self.selected.get()
		return next((d for d in self.config.directories if d.path == p), None)

	def update_options(self):
		# ugly hack: https://stackoverflow.com/a/19795103/1639625
		menu = self.directories.children["menu"]
		menu.delete(0, "end")
		for d in (d.path for d in self.config.directories):
			menu.add_command(label=d, command=lambda v=d: self.selected.set(v))

	def update_selected(self, *args):
		self.panel.set_directory(self.get_selected())

	def add_directory(self):
		path = tkinter.filedialog.askdirectory(initialdir=config.USER_DIR)
		if path:
			d = backup_model.Directory(path)
			self.config.directories.append(d)
			self.update_options()
			self.selected.set(d.path)

	def remove_directory(self):
		d = self.get_selected()
		if d:
			self.config.directories.remove(d)
			self.update_options()
			self.selected.set(next((d.path for d in self.config.directories), None))

	def auto_include(self):
		backup_core.calculate_includes(self.config)
		self.update_selected()

	def create_backup(self):
		if tkinter.messagebox.askokcancel("Backup", "Create Backup?"):
			print("creating backup...")
			try:
				backup_core.perform_backup(self.config)
				tkinter.messagebox.showinfo("Backup", "Backup finished; see log for details")
			except Exception as ex:
				tkinter.messagebox.showerror("Backup", "Error: %r; see log for details" % ex)
			self.update_selected()


class DirectoryPanel(tkinter.Canvas):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.pathvar = tkinter.StringVar()
		self.backupvar = tkinter.StringVar()
		self.changevar = tkinter.StringVar()
		self.includevar = tkinter.IntVar()

		self.pathvar.trace("w", self.update_path)
		self.includevar.trace("w", self.update_include)

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
		self.pathvar.set(directory.path if directory else "")
		self.backupvar.set(directory.last_backup if directory else "")
		self.changevar.set(directory.last_changed if directory else "")
		self.includevar.set(directory.include if directory else False)

	def update_path(self, *args):
		if self.directory:
			self.directory.path = self.pathvar.get()

	def update_include(self, *args):
		if self.directory:
			self.directory.include = bool(self.includevar.get())


if __name__ == "__main__":
	# TODO get config file from params or use default
	config_file = config.DEFAULT_CONFIG_LOCATION
	try:
		conf = backup_model.load_from_json(config_file)
	except IOError:
		conf = backup_model.create_initial_config()

	root = tkinter.Tk()
	frame = BackupFrame(root, conf)
	root.title("Backup")
	root.mainloop()

	conf.target_dir = frame.target.get()
	conf.name_pattern = frame.pattern.get()
	
	# TODO use with or try/except/finally to ensure writing to file
	# XXX for testing: do not write
	# print("writing config...")
	# backup_model.write_to_json(config_file, conf)
	# print("done")

#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""User interface for simple Backup tool.
by Tobias Küster, 2020

Second try, based on the UI for the Password Manager, using GTK, too, and a
similar layout.

- big table with directories to be backed up
- some text fields for "global" configuration like name patterns etc.
- buttons for adding and removing directories, and for creating the backup
- automatically save configuration on exit
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import backup_model, backup_core, config


class BackupFrame:
	""" Wrapper-Class for the GTK window and all its elements (but not in itself
	a subclass of Window), including callback methods for different actions.
	"""
	
	def __init__(self, conf):
		self.conf = conf
		
		# Entries for basic Configuration attributes
		self.target = Gtk.Entry()
		self.target.set_text(self.conf.target_dir)
		self.pattern = Gtk.Entry()
		self.pattern.set_text(self.conf.name_pattern)

		# create tool bar and buttons
		header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		header.pack_start(Gtk.Label(label="Target Dir"), False, False, 10)
		header.pack_start(self.target, True, True, 0)
		header.pack_start(Gtk.Label(label="Pattern"), False, False, 10)
		header.pack_start(self.pattern, True, True, 0)
		header.pack_end(create_button("Backup!", self.do_backup, "Create Backup of Selected Directories", False), False, False, 0)
		header.pack_end(create_button("list-remove", self.do_remove, "Mark selected for Removal"), False, False, 0)
		header.pack_end(create_button("list-add", self.do_add, "Add new Entry"), False, False, 0)
		
		# create table model and body section with table view
		self.create_table()
		table_scroller = Gtk.ScrolledWindow()
		table_scroller.add(self.table)
		
		body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		body.pack_start(header, False, False, 0)
		body.pack_start(table_scroller, True, True, 0)

		# put it all together in a window
		self.window = Gtk.ApplicationWindow(title=f"Backup Tool")
		self.window.resize(800, 400)
		self.window.connect("delete-event", lambda *_: self.update_conf())
		self.window.connect("destroy", Gtk.main_quit)
		self.window.add(body)
		self.window.show_all()
		
	def update_conf(self):
		""" Update Configuration from Entries and Directories Table.
		"""
		self.conf.target_dir = self.target.get_text()
		self.conf.name_pattern = self.pattern.get_text()
		self.conf.directories = [backup_model.Directory(*vals) for vals in self.store]
		
	def update_table(self):	
		"""Update table view from configuration, e.g. after updating the dates.
		"""
		self.store.clear()
		for d in self.conf.directories:
			vals = [d.path, d.archive_type, d.last_backup, d.last_changed, d.include]
			self.store.append(vals)

	def do_add(self, widget):
		""" Callback for creating a new Directory entry
		"""
		dialog = Gtk.FileChooserDialog(title="Please choose a folder",
			parent=self.window, action=Gtk.FileChooserAction.SELECT_FOLDER)
		dialog.add_buttons(Gtk.STOCK_CANCEL, False, Gtk.STOCK_OK, True)
		if dialog.run() and dialog.get_filename():
			vals = [dialog.get_filename(), "zip", None, None, False]
			self.store.append(vals)
		dialog.destroy()
	
	def do_remove(self, widget):
		""" Callback for removing the selected Directory entry
		"""
		_, it = self.select.get_selected()
		if it is not None and ask_dialog(self.window, "Remove Directory?"):
			self.store.remove(it)

	def do_backup(self, widget):
		self.update_conf()
		if ask_dialog(self.window, "Create Backup?"):
			try:
				backup_core.calculate_includes(self.conf)
				backup_core.perform_backup(self.conf)
				self.update_table()
				print("Done")
			except Exception as ex:
				print("Error", ex)
	
	def create_table(self):
		""" Create list model and filter model and populate with Directories,
		then create the actual Tree View for showing and editing those values.
		"""
		self.store = Gtk.ListStore(str, str, str, str, bool)
		self.update_table()

		self.table = Gtk.TreeView.new_with_model(self.store)
		self.select = self.table.get_selection()
		
		for i, att in enumerate(["Path", "Type", "Last Backup", "Last Change", "Include?"]):
			renderer = Gtk.CellRendererText() if i != 4 else Gtk.CellRendererToggle()
			if i == 1:
				def edit_func(widget, path, text, i=i):
					self.store[path][i] = text
				renderer.set_property("editable", True)
				renderer.connect("edited", edit_func)
			if i == 4:
				def toggle_func(widget, path, i=i):
					self.store[path][i] ^= True
				renderer.set_property("activatable", True)
				renderer.connect("toggled", toggle_func)
				
			column = Gtk.TreeViewColumn(att, renderer, active=i) if i == 4 else \
			         Gtk.TreeViewColumn(att, renderer, text=i)
			column.set_sort_column_id(i)
			column.set_expand(i == 0)
			self.table.append_column(column)
	
		
def create_button(title, command, tooltip=None, is_icon=True):
	""" Helper function for creating a GTK button with icon and callback
	"""
	button = Gtk.Button.new_from_icon_name(title, Gtk.IconSize.BUTTON) \
	         if is_icon else Gtk.Button.new_with_label(title)
	button.connect("clicked", command)
	button.set_property("relief", Gtk.ReliefStyle.NONE)
	button.set_tooltip_text(tooltip)
	return button


def ask_dialog(parent, title, message=None):
	""" Helper method for opening a simple yes/no dialog and getting the answer
	"""
	dialog = Gtk.MessageDialog(parent=parent, flags=0, 
		message_type=Gtk.MessageType.QUESTION, 
		buttons=Gtk.ButtonsType.YES_NO, text=title)
	dialog.format_secondary_text(message)
	res = dialog.run() == Gtk.ResponseType.YES
	dialog.destroy()
	return res
	

def main():
	with config.open_config(config.CONFIG_FILE) as conf:
		BackupFrame(conf)
		Gtk.main()


if __name__ == "__main__":
	main()

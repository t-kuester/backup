# -*- coding: utf8 -*-

"""
User interface for simple Backup tool.
by Tobias Küster, 2020

Second try, based on the UI for the Password Manager, using GTK, too, and a
similar layout.

- big table with directories to be backed up
- some text fields for "global" configuration like name patterns etc.
- buttons for adding and removing directories, and for creating the backup
- automatically save configuration on exit
"""

import threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from backup_core import get_date, perform_backup_iter, KNOWN_TYPES
from backup_model import Directory


class BackupFrame:
	""" Wrapper-Class for the GTK window and all its elements (but not in itself
	a subclass of Window), including callback methods for different actions.
	"""

	def __init__(self, conf):
		self.conf = conf

		# Entries for basic Configuration attributes
		self.pattern = Gtk.Entry()
		self.pattern.set_text(self.conf.target_pattern)

		# create tool bar and buttons
		header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		header.pack_start(Gtk.Label(label="Target Pattern"), False, False, 10)
		header.pack_start(self.pattern, True, True, 0)
		header.pack_end(create_button("document-save", self.do_backup, "Create Backup of Selected Directories"), False, False, 0)
		header.pack_end(create_button("view-refresh", self.do_refresh, "Refresh Include State"), False, False, 0)
		header.pack_end(create_button("list-remove", self.do_remove, "Remove Directory"), False, False, 0)
		header.pack_end(create_button("list-add", self.do_add, "Add Directory"), False, False, 0)

		# create table model and body section with table view
		self.create_table()
		table_scroller = Gtk.ScrolledWindow()
		table_scroller.add(self.table)

		# progress of the current backup operation
		self.progress = Gtk.ProgressBar()
		self.progress.set_show_text(True)
		self.progress.set_text("")

		self.widgets = [self.table, *header.get_children()]

		# main vertical "box" for all the contents of the window
		body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		body.pack_start(header, False, False, 0)
		body.pack_start(table_scroller, True, True, 0)
		body.pack_end(self.progress, False, False, 0)

		# put it all together in a window
		self.window = Gtk.ApplicationWindow(title="Simple Backup Tool")
		self.window.resize(800, 400)
		self.window.connect("delete-event", lambda *_: self.update_conf())
		self.window.connect("destroy", Gtk.main_quit)
		self.window.add(body)
		self.window.show_all()

	def update_conf(self, check=False):
		""" Update Configuration from Entries and Directories Table.
		"""
		self.conf.target_pattern = self.pattern.get_text()
		def to_directory(values):
			values[2] = values.pop() # replace date string with timestamp
			return Directory(*values)
		self.conf.directories = [to_directory(list(vals)) for vals in self.store]
		if check:
			try:
				self.conf.check()
			except Exception as e:
				show_warning(self.window, "Warning", str(e))

	def update_table(self):
		"""Update table view from configuration, e.g. after updating the dates.
		"""
		self.store.clear()
		for d in self.conf.directories:
			vals = [d.path, d.archive_type, get_date(d.last_backup), d.include, d.incremental, d.last_backup]
			self.store.append(vals)

	def do_add(self, _widget):
		""" Callback for creating a new Directory entry
		"""
		dialog = Gtk.FileChooserDialog(title="Please choose a folder",
			parent=self.window, action=Gtk.FileChooserAction.SELECT_FOLDER)
		dialog.add_buttons(Gtk.STOCK_CANCEL, False, Gtk.STOCK_OK, True)
		if dialog.run() and dialog.get_filename():
			self.update_conf()
			self.conf.directories.append(Directory(dialog.get_filename(), "zip"))
			self.update_table()
		dialog.destroy()

	def do_remove(self, _widget):
		""" Callback for removing the selected Directory entry
		"""
		_, it = self.select.get_selected()
		if it is not None and ask_dialog(self.window, "Remove Directory?"):
			self.store.remove(it)
			self.update_conf()

	def do_refresh(self, _widget):
		""" Calculate include status from last-backup and last-changed
		"""
		self.update_conf(True)
		self.conf.update_includes()
		self.update_table()

	def do_backup(self, _widget):
		""" Create backup of the selected Directories. This uses two concurrent
		processes: one for performing the actual backup, and one for updating
		the UI (the latter can not be done from the backup-thread).
		"""
		self.update_conf(True)
		if ask_dialog(self.window, "Create Backup?"):
			n, done = len(self.conf.directories) + 1, []

			def worker():
				for i, msg in enumerate(perform_backup_iter(self.conf)):
					done.append(msg)

			def update_progress():
				if done:
					self.progress.set_text(done[-1])
					self.progress.set_fraction(len(done) / n)
				all_done = len(done) >= n
				if all_done:
					self.update_table()
				for widget in self.widgets:
					widget.set_sensitive(all_done)
				return not all_done

			GLib.timeout_add(100, update_progress)
			threading.Thread(target=worker).start()

	def create_table(self):
		""" Create list model and filter model and populate with Directories,
		then create the actual Tree View for showing and editing those values.
		"""
		self.store = Gtk.ListStore(str, str, str, bool, bool, float)
		self.update_table()

		self.table = Gtk.TreeView.new_with_model(self.store)
		self.select = self.table.get_selection()

		for i, att in enumerate(["Path", "Type", "Last Backup", "Incl.?", "Incr.?"]):
			if i == 1:
				renderer = Gtk.CellRendererCombo()
				type_list = Gtk.ListStore(str)
				for x in KNOWN_TYPES:
					type_list.append([x])
				def edit_func(_widget, path, text, i=i):
					self.store[path][i] = text
				renderer.set_property("model", type_list)
				renderer.set_property("text-column", 0)
				renderer.set_property("editable", True)
				renderer.connect("edited", edit_func)
			elif i >= 3:
				renderer = Gtk.CellRendererToggle()
				def toggle_func(_widget, path, i=i):
					self.store[path][i] ^= True
				renderer.set_property("activatable", True)
				renderer.connect("toggled", toggle_func)
			else:
				renderer = Gtk.CellRendererText()

			column = Gtk.TreeViewColumn(att, renderer, active=i) if i >= 3 else \
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


def show_warning(parent, title, message):
	""" Helper method for opening a simple yes/no dialog and getting the answer
	"""
	dialog = Gtk.MessageDialog(parent=parent, flags=0,
		message_type=Gtk.MessageType.WARNING,
		buttons=Gtk.ButtonsType.OK, text=title)
	dialog.format_secondary_text(message)
	dialog.run()
	dialog.destroy()

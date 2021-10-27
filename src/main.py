import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import backup_core
import backup_gtk
import config


# ~def main():
	# ~"""This method is executed when started from command line.
	# ~- load config
	# ~- check for last changes in directory
	# ~- perform backup
	# ~- save updated config
	# ~"""
	# ~import config
	# ~with config.open_config() as conf:
		# ~calculate_includes(conf)
		# ~perform_backup(conf)
	
	
def main():
	with config.open_config() as conf:
		backup_gtk.BackupFrame(conf)
		Gtk.main()


if __name__ == "__main__":
	main()

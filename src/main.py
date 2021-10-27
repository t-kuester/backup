"""
Starter file for Simple Backup Tool,
Tobias Küster, 2021

Show either the graphical UI (the default) or run the backup tool in command-line mode,
asking the user which of the previously defined directories should be backed up, or
automatically creating backups for all directories that have been changes since last time.
"""

import argparse

import backup_core
import backup_gtk
import config


def run_commandline(interactive=True):
	"""Run in command-line mode, either asking whether to back up each directory,
	or determining it based on last modification time.
	"""
	with config.open_config() as conf:
		conf.check()

		if interactive:
			for d in conf.directories:
				incl = input(f"Include {d.path}? [y/N] ")
				d.include = incl.lower().startswith("y")
		else:
			conf.update_includes()

		for msg in backup_core.perform_backup_iter(conf):
			print(msg)
		

def run_graphical():
	"""Run with the graphical GTK UI (default).
	"""
	with config.open_config() as conf:
		backup_gtk.BackupFrame(conf)
		backup_gtk.Gtk.main()
	
	
def main():
	"""Set up command line arguments parser and chose which way to use the program.
	"""
	parser = argparse.ArgumentParser(description='Simple Backup Tool.')
	parser.add_argument("--mode", dest="mode", choices=["interactive", "automatic", "graphical"],
	                    default="graphical", required=False,
						help="Interactive: Ask whether to back up each directory first; "
							 "Automatic: Include if modified since last backup; "
							 "Graphical: Show graphical UI (default)")

	args = parser.parse_args()
	if args.mode == "graphical":
		run_graphical()
	else:
		run_commandline(args.mode == "interactive")


if __name__ == "__main__":
	main()

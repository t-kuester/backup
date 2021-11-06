Simple Backup Tool
==================

_2016-2021, Tobias Küster_

This is a very simple tool for creating backups. I made this primarily for my
personal use and still use it regularly. At first it was just a simple script
and a file with the directories I want to back up, but eventually it got a
proper UI and some more convenience features, but it is still very basic.
For instance, detects whether a backup of a directory is needed at all based
on the changed-dates of the files, and can also do simple icremental backups.


Features
--------
* select directories to be backed up
* select `zip` or `tar` archive (for files that can not be compressed)
* detect whether a directory needs to be backed up again
* create and collect backup archives with current date


Configuration and File Formats
------------------------------
The program is started with `python3 backup/main.py`. On the first start,
a configuration file is created in `~/.config/t-kuester/backup.json` holding
the different directories to be backed up as well as some more information.
The file is automatically read when the program is started and updated when it
is closed. The content of the file is explained below.

```json
    {
        "target_pattern": "~/BACKUP/{parent}/{dirname} {date}{inc}",
        "directories": [
            {
                "path": "/home/user/.config",
                "archive_type": "zip",
                "last_backup": "2020-11-07 19:58:41",
                "include": true,
                "incremental": false
            },
            ...
        ]
    }
```

The `target_pattern` indicates the directories where new backups should be stored.
It allows for different placeholders:

* `{date}`: the current date, e.g. `2020-11-07`
* `{datetime}`: the current date and time, e.g. `2020-11-07 19:58:41`
* `{parent}`: the full absolute path of the parent of the directory to be backed up
* `{dirname}`: the name of the actual directory to be backed up
* `{inc}`: can be used to add a suffic `_inc` to incremental backup archives

The `directories` list shows the individual directories to be backed up. Their
defining feature, of course, is the `path`. Besides that, you can chose whether
to use `zip` or `tar` for each directory. The `last_backup` field indicates
exactly that, and is set automatically. The `include` field shows whether the
directory should be included in the next backup and can either be set manually
or derived from the dates of the last backup and change. The `incremental` field
means that only those files will be included into the archive that have been
changed since the last backup (i.e. the backup will be faster, but previous
backups have to be keps in order to restore all files)


User Interface
--------------
As seen in the following figure, the user interface mainly consists of a large
table of all the directories to be backed up and a few buttons and text inputs.
For a description of the individual attributes and placeholders, please refer
to the description of the configuration above.

![Screenshot](backup.png)

* use the _Target Pattern_ entry to define where and how to store
  the created archive files (see above for valid placeholders)
* use the _Add_ and _Remove_ buttons to select new directories to add to the
  list or to remove entries from the list
* the _Refresh_ button is used to check whether any files were changed since
  the last backup and to set the _include_ attribute accordingly
* the _Backup_ button is used to create the actual backup
* the table can be sorted by each of the columns, but only the _Type_, _Incl._
  and _Incr._ columns are editable; valid archive types are `zip` and `tar`
* when the backup has been triggered, the bottom of the UI shows the progress
* the configuration is automatically saved when the UI is closed


Creating Backups
----------------
To create a backup, add and select the directories to be backed up and hit the
_Backup_ button. For each directory, an archive of the selected type is created
and moved to the target directory. If the file or the parent directories start
with a `.` (i.e. indicating that they are hidden) the `.` is replaced with a `_`
in the backup so that no backups are missed when moving them to storage.

Depending on the kind of files to be backed up, you may chose to use either `zip`
(i.e. with compression) or `tar` (without compression), and whether to create an
incremental backup or a full backup. For example:

* for a collection of already compressed files, where new files are added but
  files are rarely removed or changed, you should use `tar` and `incremental`
* for regular, non-compressed files that often change, like a documents folder
  or your mail box, use `zip` and a `non-incremental` backup

_Note:_ Any existing files with the same name in those directories will be
overwritten without further warning!

Afterwards, the collected backups can be moved to the target drive, e.g. a CD,
removeable USB drive, betwork share, or cloud storage.

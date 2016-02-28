# -*- coding: utf8 -*-

"""Global configuration for simple Backup tool.
by Tobias Küster, 2016

This file contains some variables for global configuration, such as some
useful defaults etc.
"""

# what language file to use?
from msg_en import *

DEFAULT_TARGET_DIR = "backup_{date}"
DEFAULT_NAME_PATTERN = "{parent]/{date}_{dir}"
DEFAULT_ARCHIVE_TYPE = "zip"
DEFAULT_CONFIG_LOCATION = ".backup_conf.json"
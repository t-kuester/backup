# -*- coding: utf8 -*-

"""Global configuration for simple Backup tool.
by Tobias Küster, 2016

This file contains some variables for global configuration, such as some
useful defaults etc.
"""

# what language file to use?
from msg_en import *

import os

USER_DIR = os.environ["HOME"]

DEFAULT_TARGET_DIR = os.path.join(USER_DIR, "backup_{date}")
DEFAULT_NAME_PATTERN = "{parent]/{date}_{dirname}"
DEFAULT_ARCHIVE_TYPE = "zip"
DEFAULT_CONFIG_LOCATION = os.path.join(USER_DIR, ".backup_conf.json")
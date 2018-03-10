# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import os
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.utils.environ import get_build_path
# ----------- END: In-App Imports ---------- #

BUILD_PATH = get_build_path()

PROJECT_HOME = 'core'

STATIC_FILE_ROOT_PATH = "src/core.backend/core/backend/static"

STATIC_JS_FILE_PATH = "{}/js".format(STATIC_FILE_ROOT_PATH)
STATIC_CSS_FILE_PATH = "{}/css".format(STATIC_FILE_ROOT_PATH)
STATIC_VIEW_FILE_PATH = "{}/htmls".format(STATIC_FILE_ROOT_PATH)
STATIC_IMAGE_FILE_PATH = "{}/images".format(STATIC_FILE_ROOT_PATH)
STATIC_FONT_FILE_PATH = "{}".format(STATIC_FILE_ROOT_PATH)

CONFIG_FILE_ROOT_PATH = os.path.join(BUILD_PATH, 'ini')

RULES_CONFIG_FILE = os.path.join(CONFIG_FILE_ROOT_PATH, "rules.ini")
MASTER_CONFIG_FILE = os.path.join(CONFIG_FILE_ROOT_PATH, "master.ini")
CLIENT_CONFIG_FILE = os.path.join(CONFIG_FILE_ROOT_PATH, "client.ini")
CLIENT_TEMPLATE_CONFIG_FILE = os.path.join(CONFIG_FILE_ROOT_PATH, "client_tpl.ini")
NODE_TEMPLATE_CONFIG_FILE = os.path.join(CONFIG_FILE_ROOT_PATH, "node_tpl.ini")

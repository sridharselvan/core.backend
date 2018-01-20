# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
# ----------- END: In-App Imports ---------- #


PROJECT_HOME = 'core'

STATIC_FILE_ROOT_PATH = "{}/static".format(PROJECT_HOME)

STATIC_JS_FILE_PATH = "{}/js".format(STATIC_FILE_ROOT_PATH)
STATIC_CSS_FILE_PATH = "{}/css".format(STATIC_FILE_ROOT_PATH)
STATIC_VIEW_FILE_PATH = "{}/htmls".format(STATIC_FILE_ROOT_PATH)
STATIC_IMAGE_FILE_PATH = "{}/images".format(STATIC_FILE_ROOT_PATH)


CONFIG_FILE_ROOT_PATH = "{}/configs".format(PROJECT_HOME)

RULES_CONFIG_FILE = "{}/rules.ini".format(CONFIG_FILE_ROOT_PATH)
MASTER_CONFIG_FILE = "{}/master.ini".format(CONFIG_FILE_ROOT_PATH)
CLIENT_CONFIG_FILE = "{}/client.ini".format(CONFIG_FILE_ROOT_PATH)
CLIENT_TEMPLATE_CONFIG_FILE = "{}/client_tpl.ini".format(CONFIG_FILE_ROOT_PATH)
NODE_TEMPLATE_CONFIG_FILE = "{}/node_tpl.ini".format(CONFIG_FILE_ROOT_PATH)

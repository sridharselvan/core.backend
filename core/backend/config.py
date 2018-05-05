# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import os
import re
import json
from datetime import datetime
#import simplejson as json

from ConfigParser import SafeConfigParser
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from bottle import request
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.backend.constants import (
    RULES_CONFIG_FILE,
    MASTER_CONFIG_FILE,
    CLIENT_CONFIG_FILE,
    NODE_TEMPLATE_CONFIG_FILE,
    CLIENT_TEMPLATE_CONFIG_FILE
)

from core.backend.utils.core_utils import (
    get_unique_id, AutoSession, get_loggedin_user_id
)
from core.constants.code_message import filled_code_message
# ----------- END: In-App Imports ---------- #


__all__ = [
    # All public symbols go here.
]


class Helpers(object):
    def generate_valve_nodes(self, mparser, cparser, cur_sec):
        gpio_pins = mparser.get('master', 'GPIO_PINS').split()

        _node_prefix = mparser.get('master', 'node_prefix')
        _nodes = [(i, "{}_{}".format(_node_prefix, i)) for i in gpio_pins]

        cparser.set(cur_sec, 'ids', ' '.join([e[1] for e in _nodes]))

        for (gpio_pin, node) in _nodes:
            if not cparser.has_section(node):
                cparser.add_section(node)
            for option in mparser.options('valve_properties'):
                if option == 'id':
                    cparser.set(node, option, node)
                elif option == 'gpio_pin':
                    cparser.set(node, option, gpio_pin)
                else:
                    cparser.set(node, option, mparser.get('valve_properties', option))


def generate_client_config():
    """."""

    helper = Helpers()
    #
    # Setup a master config parser
    mparser = SafeConfigParser()
    mparser.read(MASTER_CONFIG_FILE)
    mparser.read(CLIENT_TEMPLATE_CONFIG_FILE)
    mparser.read(NODE_TEMPLATE_CONFIG_FILE)

    #
    # Setup a client config parser
    cparser = SafeConfigParser()
    cparser.read(CLIENT_CONFIG_FILE)

    #
    # Flush the ``cparser`` object to have new values to be configured.
    [cparser.remove_section(section) for section in cparser.sections()]

    # Fileds or sections to be auto poplated on initial run
    populate = mparser.get('init', 'populate').split()

    # config file to be filled fully or partially by clients
    out_config = CLIENT_CONFIG_FILE

    # Check for instruction pattterns e.g., ${call:generate_valve_nodes}$
    pattern = re.compile("""\{\{(.*?)\}\}""")

    for each_section in populate:
        if not cparser.has_section(each_section):
            # create section if not available
            cparser.add_section(each_section)

        _options = mparser.options(each_section)

        for each_option in _options:
            _value = mparser.get(each_section, each_option)
            _callable = [tuple(e.split(':')) for e in pattern.findall(_value)]

            if _callable:
                for instr, expr in _callable:
                    if instr == 'call':
                        getattr(helper, expr)(mparser, cparser, cur_sec=each_section)
            else:
                cparser.set(each_section, each_option, _value)

        with open(out_config, 'wb') as fp:
            cparser.write(fp)


def update_client_config(form_data):

    def compute(value, type_):
        if type_ == 'mins':
            return str(value * 60)
        return str(value * 60 * 60)

    # Setup a client config parser
    cparser = SafeConfigParser()
    cparser.read(CLIENT_CONFIG_FILE)

    _response_dict = {'result': False, 'data': None, 'alert_type': None, 'alert_what': None, 'msg': None}

    if 'sessionData' in form_data:
        form_data.pop('sessionData')

    if 'is_session_valid' in form_data:
        form_data.pop('is_session_valid')

    for section, data in form_data.items():
        if section.strip() == 'on_interrupt' and isinstance(data, dict):
            [cparser.set(section, key, str(value)) for key, value in data.items()]

        if section.strip() == 'nodes' and isinstance(data, dict):
            nodes_section = data['ids'].split(" ")
            for each_node in nodes_section:

                _duration_type = str(form_data[each_node]['duration_type']).lower()

                [cparser.set(
                    each_node,
                    key,
                    compute(int(value), _duration_type) if _duration_type in ('mins', 'hrs', ) and key == 'close_after' else str(value)
                 )
                 for key, value in form_data[each_node].items()
                 ]

    with open(CLIENT_CONFIG_FILE, 'w') as configfile:
        cparser.write(configfile)

    _response_dict['result'] = True
    _response_dict['alert_type'] = 'push_msg'
    _response_dict['alert_what'] = 'msg'
    _response_dict['msg'] = filled_code_message("CM0006") 

    return _response_dict


def view_client_config():
    """."""
    if not os.path.exists(os.path.join(os.getcwd(), CLIENT_CONFIG_FILE)):
        generate_client_config()
    #
    # Setup a client config parser
    cparser = SafeConfigParser()
    cparser.read(CLIENT_CONFIG_FILE)

    _config = dict()
    for each_section in cparser.sections():
        if each_section not in _config:
            _config[each_section] = dict()

        for option, value in cparser.items(each_section):
            if option == 'close_after':
                _duration_type = dict(cparser.items(each_section))['duration_type']
                if _duration_type.strip().lower() == 'mins':
                    value = int(value) / 60
                elif _duration_type.strip().lower() == 'hrs':
                    value = int(value) / 3600

            _config[each_section][option] = value

    return _config



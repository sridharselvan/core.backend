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
#import simplejson as json

from ConfigParser import SafeConfigParser
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from core.deps.bottle import request
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.constants import (
    RULES_CONFIG_FILE,
    MASTER_CONFIG_FILE,
    CLIENT_CONFIG_FILE,
    NODE_TEMPLATE_CONFIG_FILE,
    CLIENT_TEMPLATE_CONFIG_FILE
)
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
    pattern = re.compile("""\$\{(.*?)\}\$""")

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
    return "" #view_client_config()


def view_client_config(out_type='json'):
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
            _config[each_section][option] = value

    if out_type == 'json':
        return json.dumps(_config)
    return _config

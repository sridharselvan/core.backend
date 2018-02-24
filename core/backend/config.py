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

from core.db.model import (
    CodeScheduleTypeModel, JobDetailsModel
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
    # Setup a client config parser
    cparser = SafeConfigParser()
    cparser.read(CLIENT_CONFIG_FILE)

    _response_dict = {'result': False, 'data': None, 'alert_type': None, 'alert_what': None, 'msg': None}

    if 'sessionData' in form_data:
        form_data.pop('sessionData')

    if 'is_session_valid' in form_data:
        form_data.pop('is_session_valid')

    for each_section, each_data in form_data.items():
        for option, value in each_data.items():
            cparser.set(each_section, option, str(value))

    with open(CLIENT_CONFIG_FILE, 'w') as configfile:
        cparser.write(configfile)

    _response_dict['result'] = True
    _response_dict['alert_type'] = 'push_msg'
    _response_dict['alert_what'] = 'msg'
    _response_dict['msg'] = "Data added successfully" 

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
            _config[each_section][option] = value

    return _config

def save_scheduler_config(form_data):

    _response_dict = {'result': False, 'data': None, 'alert_type': None, 'alert_what': None, 'msg': None}

    schedule_data = dict()
    start_date = form_data['start_date']
    string_date = "{0}-{1}-{2} {3}:{4}:00"\
        .format(start_date['year'],start_date['month'],start_date['day'],start_date['hour'],start_date['mins'])    

    with AutoSession() as auto_session:
        code_schedule_type = CodeScheduleTypeModel.fetch_schedule_type_idn(
            auto_session, schedule_type=form_data['type']
        )

        schedule_data['schedule_type_idn'] = code_schedule_type.schedule_type_idn

        schedule_data['start_date'] = datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S")
        schedule_data['job_id'] = get_unique_id()
        schedule_data['user_idn'] = get_loggedin_user_id()

        valve_id = list()
        for valve in form_data['ValveDetails']:
            if valve['selected'] == True:
                valve_id.append(valve['id'])

        schedule_data['params'] = "{0!s}".format(valve_id)
        schedule_data['recurrence'] = form_data['recurs']

        week_id = list()
        for weekday in form_data['weekDays']:
            if weekday['selected'] != False:
                week_id.append(weekday['id'])

        schedule_data['day_of_week'] = "{0!s}".format(week_id)

        # Inserting schedule config into Job details
        job_details_idn = JobDetailsModel.save_schedule_config(
            auto_session, **schedule_data
        ).job_details_idn



    return _response_dict



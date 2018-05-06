# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.model import TransSmsModel
from core.backend.utils.core_utils import decode
from core.constants.code_message import filled_code_message
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]

def dashboard(session):
    _response_dict = {'result': True, 'data': dict(), 'alert_type': None, 'alert_what': None, 'msg': None}

    failed_sms_data = TransSmsModel.fetch_failed_sms(session, data_as_dict=True)

    if not failed_sms_data:
        _response_dict['result'] = False
        _response_dict['msg'] = filled_code_message('CM0034')

    if failed_sms_data:
        for idx, sms_data in enumerate(failed_sms_data):
            failed_sms_data[idx]['user_name'] = decode(sms_data.get('user_name'))

        _response_dict['result'] = True
        _response_dict['data'] = failed_sms_data

    return _response_dict
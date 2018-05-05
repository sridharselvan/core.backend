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
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]

def dashboard(session):
    _response_dict = {'result': True, 'data': dict(), 'alert_type': None, 'alert_what': None, 'msg': None}

    failed_sms_data = TransSmsModel.fetch(
        session, 
        data_as_dict=True, 
        order_by=(TransSmsModel.table.trans_sms_idn, 'desc')
    )
    _response_dict['result'] = True
    _response_dict['data'] = failed_sms_data

    return _response_dict
# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import json as json
import base64
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from bottle import request as brequest
from sqlalchemy.exc import SQLAlchemyError
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db import create_session

from core.db.model import (
    UserModel, UserSessionModel, CodeStatusModel
)
from core.backend.utils.butils import decode_form_data
from core.backend.utils.core_utils import (
    use_transaction, get_unique_id, AutoSession
)
from core.backend.controller.configs import (
    view_client_config
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]

@use_transaction
def authenticate_user(session, *args, **kwargs):
    form_data = kwargs.get('form_data') or dict()
    uname = base64.b64encode(form_data.get('username'))
    passwd = base64.b64encode(form_data.get('password'))

    _response_dict = {'result': dict(), 'status': False, 'alert_type': None, 'alert_what': None, 'msg': None}

    if not uname:
        _response_dict['msg'] = 'Invalid username/password'
        return json.dumps(_response_dict)

    user_data = UserModel.fetch_user_data(session, mode='one', user_name=uname)

    if not user_data:
        _response_dict['msg'] = 'Invalid username/password'
        return _response_dict

    code_status_data = CodeStatusModel.fetch_status_idn(session, status='loggedin')

    _user_session_params = {
        'user_idn': user_data.user_idn,
        'client_ip': brequest.remote_addr,
        'browser_name': brequest.environ.get('HTTP_USER_AGENT'),
        'status_idn': code_status_data.status_idn,
        'unique_session_cd': get_unique_id(),
    }

    user_session_cd = None
    with AutoSession() as auto_session:
        # Inserting user session details
        user_session_cd = UserSessionModel.create_user_session(
            auto_session, **_user_session_params
        ).unique_session_cd

    # Authenticate user credentials
    if user_data.hash1 == passwd:
        _response_dict['result'] = {
            'user_session_cd': user_session_cd,
            'user_idn': user_data.user_idn
        }
        _response_dict['status'] = True
        return _response_dict


@use_transaction
def create_user(session, *args, **kwargs):
    form_data = kwargs.get('form_data') or dict()
    form_data['user_name'] = base64.b64encode(form_data['user_name'])
    form_data['hash1'] = base64.b64encode(form_data['hash1'])
    _response_dict = {'result': False, 'data': dict(), 'alert_type': None, 'alert_what': None, 'msg': None}

    uname = form_data.get('user_name')
    if UserModel.user_exists(session, user_name=uname):
        _response_dict['alert_type'] = 'push_msg'
        _response_dict['alert_what'] = 'msg'
        _response_dict['msg'] = "User Already exists"
        return json.dumps(_response_dict)

    _user = UserModel.create_new_user(session, **form_data)

    _response_dict['alert_type'] = 'push_msg'
    _response_dict['alert_what'] = 'msg'
    _response_dict['msg'] = 'User {} successfully created'.format(_user.user_name)

    return json.dumps(_response_dict)

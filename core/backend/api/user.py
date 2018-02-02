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
from core.backend.controller.configs import (
    view_client_config
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]

class use_transaction(object):

    def __init__(self, _func):
        self._func = _func

    def __call__(self, *args, **kwargs):

        form_data = decode_form_data(brequest.forms)
        session = create_session()
        _response = None

        if form_data:
            kwargs['form_data'] = form_data

        try:
            _response = self._func(session, *args, **kwargs)
        except SQLAlchemyError:
            session.rollback()
        else:
            session.commit()

        return _response


@use_transaction
def authenticate_user(session, *args, **kwargs):
    form_data = kwargs.get('form_data') or dict()
    uname = base64.b64encode(form_data.get('username'))
    passwd = base64.b64encode(form_data.get('password'))

    _response_dict = {'result': False, 'data': None, 'alert_type': None, 'alert_what': None, 'msg': None}

    if not uname:
        _response_dict['msg'] = 'Invalid username/password'
        return json.dumps(_response_dict)

    user_data = UserModel.fetch_user_data(session, mode='one', user_name=uname)

    if not user_data:
        _response_dict['msg'] = 'Invalid username/password'
        return json.dumps(_response_dict)

    _user_session_details = dict()
    _user_session_details['user_idn'] = user_data.user_idn
    _user_session_details['client_ip'] = brequest.remote_addr
    _user_session_details['browser_name'] = brequest.environ.get('HTTP_USER_AGENT')
    code_status_data = CodeStatusModel.fetch_status_idn(session, status='loggedin')
    _user_session_details['status_idn'] = code_status_data.status_idn

    # Inserting user session details
    _user_session = UserSessionModel.create_user_session(session, **_user_session_details)

    # Authenticate user credentials
    if user_data.hash1 == passwd:
        _response_dict['result'] = True
        return json.dumps(_response_dict)


@use_transaction
def create_user(session, *args, **kwargs):
    form_data = kwargs.get('form_data') or dict()
    form_data['user_name'] = base64.b64encode(form_data['user_name'])
    form_data['hash1'] = base64.b64encode(form_data['hash1'])
    _response_dict = {'result': False, 'data': None, 'alert_type': None, 'alert_what': None, 'msg': None}

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

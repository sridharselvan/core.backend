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
from core.db.model import (
    UserModel, UserSessionModel, CodeStatusModel
)
from core.backend.utils.butils import decode_form_data
from core.backend.utils.core_utils import (
    get_unique_id, AutoSession
)

from core.backend.utils.core_utils import encode, decode
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]

def authenticate_user(session, *args, **kwargs):
    form_data = kwargs.get('form_data') or dict()
    uname = encode(form_data.get('username'))
    passwd = encode(form_data.get('password'))

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

        user_session = brequest.environ.get('beaker.session')
        user_session['user_id'] = user_data.user_idn
        user_session['user_session_cd'] = user_session_cd
        user_session.save()

        _response_dict['result'] = {
            'user_session_cd': user_session_cd,
            'user_idn': user_data.user_idn
        }
        _response_dict['status'] = True
    else:
        _response_dict['msg'] = 'Invalid username/password'
    
    return _response_dict


def create_user(session, *args, **kwargs):
    form_data = kwargs.get('form_data') or dict()
    form_data['user_name'] = encode(form_data['user_name'])
    form_data['hash1'] = encode(form_data['hash1'])
    _response_dict = {'result': False, 'data': dict(), 'alert_type': None, 'alert_what': None, 'msg': None}

    uname = form_data.get('user_name')
    is_user_exists = UserModel.user_exists(session, user_name=uname)
    if is_user_exists:
        _response_dict['alert_type'] = 'push_msg'
        _response_dict['alert_what'] = 'msg'
        _response_dict['is_user_exists'] = is_user_exists
        _response_dict['msg'] = "User Already exists"
        return json.dumps(_response_dict)

    _user = UserModel.create_new_user(session, **form_data)

    _response_dict['alert_type'] = 'push_msg'
    _response_dict['alert_what'] = 'msg'
    _response_dict['msg'] = 'User {} successfully created'.format(_user.user_name)

    return _response_dict


def get_user_details(session, user_id):
    _response_dict = {'result': False, 'data': dict(), 'alert_type': None, 'alert_what': None, 'msg': None}
    user_data = UserModel.fetch_user_data(session, mode='one', user_idn=user_id)
    user_details = {
        'user_idn': user_data.user_idn,
        'first_name': user_data.first_name,
        'last_name': user_data.last_name,
        'phone_no1': user_data.phone_no1,
        'phone_no2': user_data.phone_no2,
        'user_name': decode(user_data.user_name)
    }
    if user_data:
        _response_dict['data'] = user_details
    return _response_dict

def update_user_details(session, form_data):
    _response_dict = {'result': False, 'data': dict(), 'alert_type': None, 'alert_what': None, 'msg': None}

    form_data['user_name'] = encode(form_data['user_name'])

    _updates = form_data
    updated_user_details = UserModel.update_user_details(
        session, 
        where_condition={'user_idn':form_data['user_idn']}, 
        updates=_updates
    )

    _response_dict.update({'data': updated_user_details})

    return _response_dict

def forgot_password(session, form_data):
    _response_dict = {'result': False, 'data': dict(), 'alert_type': None, 'alert_what': None, 'msg': None}
    
    form_user_name = encode(form_data['user_name'])
    form_phone_no = form_data['phone_no']
    new_hash = encode(form_data['new_hash'])

    user_data = UserModel.fetch_user_data(session, mode='one', user_name=form_user_name)

    if user_data and user_data.user_name != form_user_name:
        _response_dict['is_user_name_matched'] = False
        return _response_dict

    if user_data and str(user_data.phone_no1) != form_phone_no:
        _response_dict['is_phone_no_matched'] = False
        _response_dict['is_user_name_matched'] = True
        return _response_dict

    if user_data:
        _response_dict['is_phone_no_matched'] = True
        _response_dict['is_user_name_matched'] = True
        updated_user_details = UserModel.update_user_details(
            session, 
            where_condition={'user_name':form_user_name}, 
            updates={
                'hash1': new_hash, 
                'hash2': user_data.hash1
            }
        )

        _response_dict.update({'data': updated_user_details})
        
        
    return _response_dict
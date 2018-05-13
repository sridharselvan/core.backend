# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import json as json
import base64
import random
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from bottle import request as brequest
from sqlalchemy.exc import SQLAlchemyError
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.model import (
    UserModel, UserSessionModel, CodeStatusModel, TransOtpModel,
    ConfigUserSmsModel, CodeSmsEventsModel
)
from core.backend.utils.butils import decode_form_data
from core.backend.utils.core_utils import (
    get_unique_id, AutoSession
)

from core.mq import SimpleSMSPublisher

from core.utils.utils import generate_otp

from core.utils.environ import get_queue_details, get_general_configs

from core.backend.utils.core_utils import encode, decode
from core.constants.code_message import filled_code_message

from core.constants import CONSTANT_EVENT_ALWAYS_SEND_SMS
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
        _response_dict['msg'] = filled_code_message('CM0001')
        return json.dumps(_response_dict)

    user_data = UserModel.fetch_user_data(session, mode='one', user_name=uname)

    if not user_data:
        _response_dict['msg'] = filled_code_message('CM0001')
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
        _response_dict['msg'] = filled_code_message('CM0001')

    return _response_dict


def create_user(session, *args, **kwargs):
    form_data = kwargs.get('form_data') or dict()
    form_data['user_name'] = encode(form_data['user_name'])
    form_data['hash1'] = encode(form_data['hash1'])
    _response_dict = {'result': False, 'data': dict(), 'alert_type': None, 'alert_what': None, 'msg': None}

    uname = form_data.get('user_name')
    form_phone_no = form_data.get('phone_no1')
    is_user_exists = UserModel.user_exists(session, user_name=uname)
    is_phoneno_exists = UserModel.fetch_one(session, phone_no1=form_phone_no)

    if is_phoneno_exists:
        _response_dict['result'] = False
        _response_dict['is_phoneno_exists'] = True
        _response_dict['msg'] = filled_code_message('CM0034')
        return _response_dict

    if is_user_exists:
        _response_dict['alert_type'] = 'push_msg'
        _response_dict['alert_what'] = 'msg'
        _response_dict['is_user_exists'] = is_user_exists
        _response_dict['msg'] = filled_code_message('CM0003')
        return json.dumps(_response_dict)

    _user = UserModel.create_new_user(session, **form_data)

    #
    # user specific sms event configurations are being fed here.
    _sms_events = CodeSmsEventsModel.fetch(session)
    for sms_event in _sms_events:
        ConfigUserSmsModel.insert(session, user_idn=_user.user_idn, code_sms_events_idn=sms_event.code_sms_events_idn)

    _response_dict['result'] = True
    _response_dict['msg'] = filled_code_message('CM0002', user_name=decode(_user.user_name))

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

    _response_dict['msg'] = filled_code_message('CM0007')
    _response_dict.update({'data': updated_user_details})

    return _response_dict

def forgot_password_validation(session, form_data):
    _response_dict = {'result': False, 'data': dict(), 'alert_type': None, 'alert_what': None, 'msg': None}

    form_user_name = encode(form_data['user_name'])
    form_phone_no = form_data['phone_no']

    user_data = UserModel.fetch_user_data(session, mode='one', user_name=form_user_name)

    if not user_data:
        _response_dict['is_user_name_matched'] = False
        return _response_dict

    if user_data.user_name != form_user_name:
        _response_dict['is_user_name_matched'] = False
        return _response_dict

    if str(user_data.phone_no1) != form_phone_no:
        _response_dict['is_phone_no_matched'] = False
        _response_dict['is_user_name_matched'] = True
        return _response_dict

    _response_dict['is_phone_no_matched'] = True
    _response_dict['is_user_name_matched'] = True

    otp_code = generate_otp()

    code_status_data = CodeStatusModel.fetch_status_idn(session, status='pending')

    trans_otp_obj = TransOtpModel.insert(
        session,
        user_idn=user_data.user_idn,
        otp_code=otp_code,
        status_idn=code_status_data.status_idn
    )

    queue_details = get_queue_details()

    phone_number = str(user_data.phone_no1)

    #
    # Push sms notification
    SimpleSMSPublisher().publish(
        sms_event=CONSTANT_EVENT_ALWAYS_SEND_SMS,
        user_idn=user_data.user_idn,
        payload=dict(
            message=filled_code_message('CM0019', otp_code=otp_code),
            number=phone_number,
        )
    )

    _response_dict['data']['is_otp_enabled'] = True
    _response_dict['data']['otp_idn'] = trans_otp_obj.trans_otp_idn
    return _response_dict


def update_password(session, form_data):
    _response_dict = {'result': False, 'data': dict(), 'alert_type': None, 'alert_what': None, 'msg': None}

    form_user_name = encode(form_data['user_name'])
    new_hash = encode(form_data['new_hash'])

    form_otp_code = form_data['otp_code']
    form_otp_idn = form_data['otp_idn']

    trans_otp_obj = TransOtpModel.fetch_one(
        session,
        trans_otp_idn=form_otp_idn
    )

    if not trans_otp_obj:
        _response_dict.update({'result': False, 'msg': filled_code_message('CM0004')})
        return _response_dict

    if str(trans_otp_obj['otp_code']).lower().strip() != str(form_otp_code).lower().strip():
        _response_dict.update({'result': False, 'msg': filled_code_message('CM0005')})
        return _response_dict

    updated_user_details = UserModel.update_user_details(
        session,
        where_condition={'user_name':form_user_name},
        updates={
            'hash1': new_hash
        }
    )

    TransOtpModel.delete(
        session,
        where_condition={'trans_otp_idn': form_otp_idn}
    )

    _response_dict.update({'result': True, 'msg': filled_code_message('CM0020')})

    return _response_dict

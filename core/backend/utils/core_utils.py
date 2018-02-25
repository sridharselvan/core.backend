# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
from uuid import uuid4
import json
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from bottle import request

from sqlalchemy.exc import SQLAlchemyError

import base64
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.model import (
    UserSessionModel, UserActivityModel,
    CodeStatusModel
)

from core.backend.utils.butils import decode_form_data

from core.db import create_session
# ----------- END: In-App Imports ---------- #

def get_unique_id():
    return str(uuid4())

def get_loggedin_user_id():
    user_session = request.environ.get('beaker.session')
    return user_session.get('user_id')

def encode(data):
    return base64.b64encode(data)

def decode(encoded_data):
    return base64.b64decode(encoded_data)


class AutoSession(object):

    def __init__(self):
        self.session = create_session()

    def __enter__(self):
        # make a database connection and return it
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
        finally:
            self.session.close()


class common_route(object):

    def __init__(self, use_transaction=False):
        self.use_transaction = use_transaction
        self.transactional_session = None

    def __call__(self, func):

        self._func = func

        def decor(*args, **kwargs):

            _response = dict()

            if self._func.__name__ in ('on_login', ):

                with AutoSession() as auto_session:
                    return self._func(auto_session, *args, **kwargs)

            user_session = request.environ.get('beaker.session')
            user_id = user_session.get('user_id')
            user_session_cd = user_session.get('user_session_cd')

            if self._func.__name__ in ('logout_user', ):

                with AutoSession() as auto_session:
                    UserSessionModel.logout(
                        auto_session,
                        user_session_cd=user_session_cd,
                        user_idn=user_id
                    )

            else:  

                if self.use_transaction:
                    args = list(args)
                    self.transactional_session = create_session()
                    args[0:0] = [self.transactional_session]

                if not user_session_cd or not user_id:
                    return json.dumps({'is_session_valid' : False})

                with AutoSession() as auto_session:
                    user_has_open_session = UserSessionModel.fetch_active_loggedin_user_session(
                        auto_session, user_idn=user_id, unique_session_cd=user_session_cd
                    )

                if not user_has_open_session:
                    return json.dumps({'is_session_valid' : False})

                try:
                    _response = self._func(*args, **kwargs)
                except SQLAlchemyError:
                    self.transactional_session.rollback()
                else:
                    if self.transactional_session:
                        self.transactional_session.commit()

                _response.update({'is_session_valid' : True})
                return json.dumps(_response)

        return decor
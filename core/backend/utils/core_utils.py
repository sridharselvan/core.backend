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
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.model import (
    UserSessionModel, UserActivityModel
)

from core.backend.utils.butils import decode_form_data

from core.db import create_session
# ----------- END: In-App Imports ---------- #

def get_unique_id():
    return str(uuid4())


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

    def __init__(self, _func):
        self._func = _func

    def __call__(self, *args, **kwargs):

        with AutoSession() as auto_session:
            if self._func.__name__ in ('on_login', ):
                #
                # Session check exclusions
                pass

            else:
                import pdb; pdb.set_trace() ## XXX: Remove This
                user_session = request.environ.get('beaker.session')
                user_id = user_session['user_id']
                user_session_cd = user_session['user_session_cd']
 
                if not user_session_cd or not user_id:
                    return json.dumps({'is_session_valid' : False})

                user_has_open_session = UserSessionModel.fetch_active_user_session(
                    auto_session, user_idn=user_id, unique_session_cd=user_session_cd
                )

                if not user_has_open_session:
                    return json.dumps({'is_session_valid' : False})

        _response = self._func(*args, **kwargs)
        _response.update({'is_session_valid' : True})
        return json.dumps(_response)


class use_transaction(object):

    def __init__(self, _func):
        self._func = _func

    def __call__(self, *args, **kwargs):

        form_data = decode_form_data(request.forms)
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

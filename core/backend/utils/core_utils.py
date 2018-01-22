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
from sqlalchemy.exc import SQLAlchemyError
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.backend.db.model import (
    UserSessionModel, UserActivityModel
)
from core.backend.utils.butils import decode_form_data
from core.backend.db import create_session
from core.backend.deps.bottle import request as brequest
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

        user_name = 'YWRtaW4='
        session_cd = '64d992fd-84de-47c5-978e-9a846abe4319'

        with AutoSession() as auto_session:
            # Inserting user session details
            user_session_detail = UserSessionModel.fetch_active_user_session(
                auto_session, user_name=user_name
            )
            import pdb;pdb.set_trace()

            if user_session_detail.uniqe_session_cd == session_cd:
                call = True

        if call:
            _response = self._func(*args, **kwargs)

        # _user_activity_details = dict()
        # _user_activity_details['user_session_idn'] = _response['data']['user_session_idn']
        # _user_activity_details['is_authorized'] = 1 # todo
        # _user_activity_details['status_idn'] = 4#_response['data']['status_idn']
        # import pdb;pdb.set_trace()

        # with AutoSession() as auto_session:
        #     # Inserting user session details
        #     _user_activity = UserActivityModel.create_user_activity(auto_session, **_user_activity_details)

        return json.dumps(_response)

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
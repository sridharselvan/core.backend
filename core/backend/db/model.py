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
from core.backend.db.saorm import SqlAlchemyORM
from core.backend.db.entity import (
    UserEntity, UserSessionEntity, CodeStatusEntity,
    UserActivityEntity
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


class UserModel(SqlAlchemyORM):
    table = UserEntity

    @classmethod
    def fetch_user_data(cls, session, mode='all', **kwargs):
        modes = ('all', 'one', )
        if mode not in modes:
            raise Exception("Argument mode is not one among {}".format(modes))

        if mode == 'all':
            return cls.fetch(session, **kwargs)
        elif mode == 'one':
            return cls.fetch_one(session, **kwargs)

    @classmethod
    def user_exists(cls, session, **kwargs):
        return True if cls.fetch(session, **kwargs) else False

    @classmethod
    def create_new_user(cls, session, **kwargs):
        return cls.insert(session, **kwargs)

class CodeStatusModel(SqlAlchemyORM):
    table = CodeStatusEntity

    @classmethod
    def fetch_status_idn(cls, session, **kwargs):
        return cls.fetch_one(session, **kwargs)

class UserSessionModel(SqlAlchemyORM):
    table = UserSessionEntity

    @classmethod
    def create_user_session(cls, session, **kwargs):
        return cls.insert(session, **kwargs)

    @classmethod
    def fetch_active_user_session(cls, session, **kwargs):

        if 'is_active' not in kwargs:
            kwargs['is_active'] = 1



        cls.fetch_one()

class UserActivityModel(SqlAlchemyORM):
    table = UserActivityEntity

    @classmethod
    def create_user_activity(cls, session, **kwargs):
        return cls.insert(session, **kwargs)


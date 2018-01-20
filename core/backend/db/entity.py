# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


Base = declarative_base()

class UserEntity(Base):
    __tablename__ = 'user'

    user_idn = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    user_name = Column(String, nullable=False)
    hash1 = Column(String, nullable=False)
    hash2 = Column(String, nullable=True)
    phone_no1 = Column(String, nullable=False)
    phone_no2 = Column(String, nullable=True)
    email_id = Column(String, nullable=True)
    crt_dt = Column(String, nullable=True)
    upd_dt = Column(String, nullable=True)
    is_active = Column(Integer, nullable=True)
    email_id = Column(String, nullable=True)

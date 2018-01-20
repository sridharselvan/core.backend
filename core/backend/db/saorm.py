# -*- coding: utf-8 -*-


# ----------- START: Native Imports ---------- #
from decimal import Decimal
# ----------- END: Native Imports ---------- #

# ----------- START: Local SRE imports ---------- #
# ----------- END: Local SRE Imports ---------- #

# ----------- START: Python Third Party Imports ---------- #
from sqlalchemy import and_
from sqlalchemy.sql.functions import Function
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm import contains_eager, joinedload
# ----------- END: Python Third Party Imports ---------- #

# ----------- START: JIVA Imports ---------- #
# ----------- END: JIVA Imports ---------- #


__all__ = [
    'SqlAlchemyORM',
]

class SqlAlchemyORM(object):

    """A utility ot helper lever super class that holds all the possible
    SQLAlchemy related utilities or helper methods."""

    # Mode mapper for the custom fetch binds.
    mode_map = {
        'one': 'one',
        'all': 'all',
        'count': 'count',
    }

    @classmethod
    def fetch(cls, session, select_cols='*', mode='all', data_as_dict=False, **kwargs):

        """Fetches the Recordset(s) of current Table or joined tables for the
        given filters and specified columns.

        Args:
            session (object): SqlAlchemy session object.
            select_cols (Optional[list]): select column restrictions
            mode (Optional): Query mode e.g., one, all, etc.,
            data_as_dict (Optional[bool]): Flag which determines the format in which result is returned
            \*\*kwargs (keyword Argggument): An arbitrary keyword argument.

        Returns:
            RecordSet(s) if argument execute is ``True`` else query object of curent table.

        """
        def apply_filter(query_object, **kwargs):

            for field, value in kwargs.items():
                query_object = query_object.filter(getattr(cls.table, field) == value)

            return query_object

        query_object = session.query(cls.table)

        query_object = apply_filter(query_object, **kwargs)

        q_obj = getattr(query_object, cls.mode_map[mode], query_object.all)

        result = q_obj()

        if data_as_dict:
            if not isinstance(result, list):
                # this check is required when query.one method gets executed
                result = [result]
            return [cls.to_dict(each_result, query_object) for each_result in result]
        return result

    @classmethod
    def fetch_one(cls, session, select_cols='*', data_as_dict=False, **kwargs):

        """Fetches one record. can be invoked while we expect only one record
        to be present.

        As this API, ``fetch_one`` is intented to respond with a single result
        in-case if no result or multiple result is found, this returns an
        empty ``list()``

        Args:
            session (object): sqlalchemy session object
            select_cols (Optional[list]): select column restrictions
            data_as_dict(boolean): flag to determine if input data is a dict or not
            \*\*kwargs (dict): filter arguments for where clause

        Returns:
            either single result object or a dict or None

        """
        try:
            result = cls.fetch(
                session, select_cols=select_cols, mode='one', data_as_dict=data_as_dict, **kwargs
            )
        except (NoResultFound, MultipleResultsFound):
            #
            # TODO: Log this event if required
            return None
        else:
            if data_as_dict:
                return result[0]
            return result

    @classmethod
    def insert(cls, session, **kwargs):
        """
        Inserts a row for given table with given column details

        Args:
            session (object): sqlalchemy session object
            \*\*kwargs (dict): column values for insert statement

        Returns:
            object : returns current object of inserted row
        """
        import pdb;pdb.set_trace()
        ins_obj = cls.table(**kwargs)
        session.add(ins_obj)
        session.flush()
        return ins_obj

    # TODO: To be deprecated, use SQLAlchemy native support.
    @staticmethod
    def to_dict(result_obj, query_obj=None):
        """
        converts the sqlalchemy object to dictionary containing fields-values mapping

        Args:
            result_obj(object): sqlalchemy collection object/entity object
            query_obj(object): sqlalchemy query object

        Returns:
            dict: dictionary having fields-values mapping
        """
        def _adjust(f_name):
            _attr = getattr(result_obj, f_name, None)

            if isinstance(_attr, Decimal):
                return int(_attr)
            return _attr

        if hasattr(result_obj, '__table__'):
            return {
                c.name: _adjust(c.name)
                for c in result_obj.__table__.columns
            }
        else:
            # Reference snippet -- to be retained for the references
            # cols = query_obj.column_descriptions
            # return { cols[i]['name'] : result_obj[i]  for i in range(len(cols)) }
            #
            return result_obj._asdict()

    @classmethod
    def update(cls, session, updates, where_condition):
        """
        This method is to update the database records.

        Args:
            session (object): SqlAlchemy session object.
            updates (dict): dictionay with key being column name object and
                            value being the new value to be updated in the DB
            where_condition (dict): Query filter parameters
        Returns:
            integer : returns updated rows count
        Raises:
            ``Exception`` when one of the arguments i.e. updates and where_condition are empty
        """
        query_object = session.query(cls.table)
        _msg = "'{}' argument can not be empty"

        if not updates:
            raise Exception(_msg.format('updates'))

        if not where_condition:
            raise Exception(_msg.format('where_condition'))

        filters_list = cls.fetch_filter_conditions(**where_condition)

        for each in filters_list:
            query_object = query_object.filter(each)

        # This is to ensure field with value None is not passed to update method as it populates
        # field with Null
        # TODO: This list can be populated with values which are not to be considered while updating the
        # records
        exclusion_list = [None]

        updates = {key: value for key, value in updates.items() if value not in exclusion_list}

        # [NOTE]: ``synchronize session="fetch"`` performs a select query before
        # the update to find objects that are matched by the update query
        return query_object.update(updates, synchronize_session='fetch')




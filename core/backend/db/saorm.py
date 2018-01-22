# -*- coding: utf-8 -*-


# ----------- START: Native Imports ---------- #
from decimal import Decimal
from collections import namedtuple
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
# ----------- END: Third Party Imports ---------- #

# ----------- START: Python Third Party Imports ---------- #
from sqlalchemy.sql.functions import Function
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.attributes import QueryableAttribute
# ----------- END: Python Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
# ----------- END: In-App Imports ---------- #


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

    # A customized python ``collections.namedtuple`` for the join tables.
    #
    # The second argument ``'table_model, join_on, where_condition'`` is the
    # sequence of variables or attributes to be defined under ``JoinTables``
    # class.
    JoinTables = namedtuple('JoinTables', 'table_model, join_on, where_condition')

    @classmethod
    def join_construct(cls, table_model=None, join_on=None, where_condition=None):

        """Customized namedtuple interface method, which provides the flexilibility
        of creating a named tuple to join the tables with the primary/base tables,
        and this applies the default values to the namedtuples, in case if they
        are not mentioned.

        Note:
            The argument ``join_on`` can take up either primary-foreign key based
            join argument or non primary-foreign key based arguments for example,

            The Argument ``where_condition`` will be applied at the SQL WHERE clause.

            Any multiple join condiotins to be specified as part of the argument ``join_on`` as mentioned below.

        Args:
            table_model (object): object of any SQLAlchemy table model.

            join_on (str | object): SQLAlchemy's ``primary_join`` string or
                column object, on which primary-foreign key relationship exists.

            where_condition (Optional[dict]): dictionary of key-value restrictions.

        Raises:
            ``VoidError`` if invalid arguments are supplied.

        Returns:
            Customized ``collections.namedtuple`` object.

        """
        #
        # make ``where_condition`` as optional, if it's not been passed.
        if where_condition is None:
            where_condition = dict()

        return cls.JoinTables(
            table_model=table_model, join_on=join_on, where_condition=where_condition
        )

    @classmethod
    def fetch_filter_conditions(cls, **kwargs):
        """Appends filter conditions for given cls

        Args:
            \*\*kwargs (dict): contains 'entity active', 'event name' etc.

        Returns:
            list of filter conditions associated with current class

        Raises:
            ``Exception`` if column is not present in the table.

            ``Exception`` if more than a value given for 'not equal to' operator.

            ``UnSupportedError`` if an invalid operator is received as filter.

        Note: In cases where filter condition required is 'IS NULL', it can be
        achieved with 'is' operator (ex:field = ('is', None))

        """

        # Declares list of any item that has to be excluded while framing the filter conditions.
        _exclusion_list = ['', ]

        filter_list = list()

        for field, value in kwargs.items():

            if value in _exclusion_list:
                # Skip if any invalid value is supplied.
                #
                # NOTE: ``None`` should not be excluded from here, as ``None``
                # can be a part of valid expression.
                continue

            field_obj = getattr(cls.table, field, None)

            if not field_obj:
                _msg = "Table {} has no column {}"
                raise Exception(_msg.format(cls.table.__tablename__, field))

            if isinstance(value, (tuple, list)):
                #
                # Any duplicates from the ``attrs`` to be eliminated,
                # as these duplicates will be applied on the query as well.
                operator, attrs = value[0], list(set(value[1:]))

                #
                # Exclude the unwanted items from ``attrs``.  Python
                # ``None`` should not be excluded, as it might have
                # been added purposefully``
                attrs = [item for item in attrs if item not in _exclusion_list]

                if not attrs:
                    _msg = "Invalid or no operand is supplied for operator: '{}'"
                    raise Exception(_msg.format(operator))

                if operator == 'in':
                    if not attrs:
                        _msg = "'{}' operator can only be applied on list of operands, Got '{}'"
                        raise Exception(_msg.format(operator, attrs or list()))
                    filter_list.append(field_obj.in_(attrs))

                elif operator == 'not in':
                    if not attrs:
                        _msg = "'{}' operator can only be applied on list of operands, Got '{}'"
                        raise Exception(_msg.format(operator, attrs or list()))
                    filter_list.append(~field_obj.in_(attrs))

                elif operator == 'not equal to':
                    if len(attrs) != 1:
                        _msg = "'{}' operator can be applied only on single operand, Got '{}'"
                        raise Exception(_msg.format(operator, attrs))
                    filter_list.append(field_obj != (attrs[0]))

                elif operator == 'is':
                    if len(attrs) != 1:
                        _msg = "'{}' operator can be applied only on single operand, Got '{}'"
                        raise Exception(_msg.format(operator, attrs))

                    if attrs[0] is not None:
                        _msg = "'{}' operator can operate only on 'None' operand , Got '{}'"
                        raise Exception(_msg.format(operator, attrs))

                    filter_list.append(field_obj == (attrs[0]))

                elif operator == 'is not':
                    if len(attrs) != 1:
                        _msg = "'{}' operator can be applied only on single operand, Got '{}'"
                        raise Exception(_msg.format(operator, attrs))

                    if attrs[0] is not None:
                        _msg = "'{}' operator can operate only on 'None' operand , Got '{}'"
                        raise Exception(_msg.format(operator, attrs))

                    filter_list.append(field_obj != (attrs[0]))

                elif operator == 'like':
                    if len(attrs) != 1:
                        _msg = "'{}' operator can be applied only on single operand, Got '{}'"
                        raise Exception(_msg.format(operator, attrs))
                    if attrs[0] is None:
                        _msg = "'{}' operator can not operate on 'None' "
                        raise Exception(_msg.format(operator, attrs))
                    filter_list.append(field_obj.like('%' + attrs[0] + '%'))

                else:
                    _msg = "Operator '{}', is not being supported."
                    raise Exception(_msg.format(operator))

            elif value is None:

                # If None is passed as value of a field, it will be skipped.
                # For example if there is an optional search param(according to
                # payload schema) and it has not been passed as part of
                # incoming payload for an api in such case we will end up in
                # passing None as field value (i.e. field=None) to the model method
                # which will get converted to "is null" sql statement giving
                # false results

                pass

            else:

                filter_list.append(field_obj == value)

        return filter_list

    @classmethod
    def prepare_query(cls, query_object, select_cols='*', **kwargs):

        """Applies the custom logics to the Query, such as Joins, eager_load,
        where clause statements, restricting the select columns etc.,

        Args:
            select_cols (Optional[list]): select column restrictions.
            \*\*kwargs (keyword Argument): An arbitrary keyword argument.

        Raises:
            ``InvalidColumnError`` If the Column specified does not exists.

        """

        # ------------------------ DO NOT ALTER ---------------------------- #
        #          THE FOLLOWING SNIPPETS TO BE KEPT IN THE ORDER            #
        # ------------------------ DO NOT ALTER ---------------------------- #

        #
        # List of filters to be applied over the Query.
        _filters = list()

        #
        # Make the ``\*\*kwargs`` clean, i.e, remove any additional fields
        # added to it.
        _join_tables = kwargs.pop('join_tables', list())

        order_by = kwargs.pop('order_clause', list())
        import pdb;pdb.set_trace()
        #
        # Add the join in sequence
        for named_join_tuple in _join_tables:
            query_object = query_object.join(named_join_tuple.table_model.table, named_join_tuple.join_on)

            #
            # Collect filters on the specific/joined tables.
            _filters.extend(
                named_join_tuple.table_model.fetch_filter_conditions(
                    **named_join_tuple.where_condition
                )
            )

        #
        # Collect filters on the current table.
        _filters.extend(cls.fetch_filter_conditions(**kwargs))

        # Apply the collected ``_filters``.
        for each_filter in _filters:
            query_object = query_object.filter(each_filter)

        # order by clause
        for each in order_by:
            query_object = query_object.order_by(each)

        #
        # Apply the select column restrictions
        query_object = cls.apply_select(query_object, select_cols)

        return query_object

    @classmethod
    def apply_select(cls, query_object, select_cols='*'):

        """A custom method to apply the select screens.

        Args:
            select (str | list): ``list`` of columns to be filtered.

        Raises:
            ``Exception`` if field is not a subclass of ``QueryableAttribute``.

        """

        if select_cols == '*':
            # leave this section untouched, as the default select is bound to fetch
            # all the fields of any specific table.
            pass

        elif isinstance(select_cols, (tuple, list)):

            # Select Specific fields.
            for _field_obj in select_cols:

                _allowed_subclasses = (Function, QueryableAttribute, )

                if not isinstance(_field_obj, _allowed_subclasses):
                    _msg = "Specified field {}, is not a subclass of {}"
                    raise Exception(_msg.format(_field_obj, _allowed_subclasses))

            query_object = query_object.with_entities(*select_cols)

        else:
            #
            # Report if the given value of ``select`` is not supported.
            _msg = "Data supplied for Argument select: {}, is invalid"
            raise Exception(_msg.format(select_cols))

        return query_object

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

        query_object = session.query(cls.table)

        query_object = cls.prepare_query(query_object, select_cols=select_cols, **kwargs)

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




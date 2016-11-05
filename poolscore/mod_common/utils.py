import json
import re
import logging
from time import mktime, strptime
from functools import wraps
from datetime import datetime, date
from inspect import getmro

from flask import request, redirect, \
                g, url_for, session, \
                render_template
from flask_sqlalchemy import Pagination
from sqlalchemy.sql import text
from sqlalchemy import inspect
from sqlalchemy.sql.expression import asc as asc_expr, desc as desc_expr
from sqlalchemy.sql.sqltypes import DateTime
from pytz import timezone, utc, all_timezones_set
from pytz.exceptions import UnknownTimeZoneError

from poolscore import app
from poolscore import db

logger = logging.getLogger(__name__)

class ApiError(Exception):

    status_code = 400

    def __init__(self, message, status_code = None, payload = None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        if self.message:
            rv['message'] = self.message
        return rv

class SecurityUtil(object):

    PASSWORD_HASH_METHOD = 'pbkdf2:sha1'

    @staticmethod
    def username_allowed(username = None):
        reserved_usernames = app.config.get('RESERVED_USERNAMES', None)
        if reserved_usernames and username in reserved_usernames:
            return False
        return True

    @staticmethod
    def is_user_password_hashed(password):
        if not password:
            return False
        return True if password.startswith(SecurityUtil.PASSWORD_HASH_METHOD) and \
            password.count('$') >= 2 else False

    @staticmethod
    def create_session(user):
        session["user_id"] = user.id
        session["user_name"] = user.first_name
        session["user_email"] = user.email
        session["user_username"] = user.username
        session["user_timezone"] = user.timezone
        session["logged_in"] = True

    @staticmethod
    def invalidate_session():
        session.pop("user_id", None)
        session.pop("user_name", None)
        session.pop("user_email", None)
        session.pop("user_username", None)
        session.pop("user_timezone", None)
        session["__invalidate__"] = True

    @staticmethod
    def is_authenticated():
        user_id = email = None
        g._user_auth_token = None
        valid = False
        id = session.get('user_id', None)
        if id:
            sql = text('select id, email, username, timezone, active ' +
                'from user where id = :id')
            row = db.engine.execute(sql, id = id).fetchone()
            if row:
                valid = row['active']
                user_id = int(row['id'])
                email = str(row['email'])
                username = str(row['username'])
                tz = str(row['timezone'])
            if valid:
                g._user_auth_token = dict(
                    user_id = user_id,
                    email = email,
                    username = username,
                    timezone = tz)
                try:
                    g._user_tz = timezone(tz) if tz and tz in all_timezones_set else timezone(
                        app.config.get('DEFAULT_USER_TIMEZONE', 'US/Eastern'))
                except UnknownTimeZoneError, e:
                    app.logger.warn("Invalid user timezone '%s'" % tz)
                    g._user_tz = timezone(
                        app.config.get('DEFAULT_USER_TIMEZONE', 'US/Eastern'))
        return valid

    @staticmethod
    def is_admin(id = None):
        '''Too lazy to implement roles so let's just make user #1 the default admin'''
        valid = False
        if id == None:
            id = session.get('user_id', None)
        if id:
            valid = (id == 1)
        return valid

    @staticmethod
    def not_authenticated_error_response():
        return redirect(url_for('auth.login'))

    @staticmethod
    def not_admin_error_response():
        return render_template('403.html'), 403

    @staticmethod
    def not_found_error_response():
        return render_template('404.html'), 404

    @staticmethod
    def requires_auth(**options):
        def requires_auth_decorator(fn):
            @wraps(fn)
            def wrapped(*args, **kwargs):
                if not SecurityUtil.is_authenticated():
                    SecurityUtil.invalidate_session()
                    return SecurityUtil.not_authenticated_error_response()
                return fn(*args, **kwargs)
            return wrapped
        return requires_auth_decorator

    @staticmethod
    def requires_admin(**options):
        def requires_admin_decorator(fn):
            @wraps(fn)
            def wrapped(*args, **kwargs):
                if not SecurityUtil.is_admin():
                    return SecurityUtil.not_admin_error_response()
                return fn(*args, **kwargs)
            return wrapped
        return requires_admin_decorator


class PagerDict(dict):

    def __init__(self, *args, **kwargs):
        super(PagerDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class Util(object):

    VALID_EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

    @staticmethod
    def to_serializable_dict(inst, cls, additional_ignored_fields = None, additional_json_fields = None):
        convert = dict() # Custom converter dict. It should contain 'type': callback_fn() pairs.
        d = dict()

        ignored_fields = []
        if hasattr(cls, 'JSON_SERIALIZATION_IGNORED_FIELDS'):
            fields = getattr(cls, 'JSON_SERIALIZATION_IGNORED_FIELDS')
            if isinstance(fields, (list, tuple)):
                ignored_fields.extend(fields)
        if additional_ignored_fields and isinstance(additional_ignored_fields, (list, tuple)):
            ignored_fields.extend(additional_ignored_fields)

        json_fields = []
        if hasattr(cls, 'JSON_SERIALIZATION_JSON_FIELDS'):
            fields = getattr(cls, 'JSON_SERIALIZATION_JSON_FIELDS')
            if isinstance(fields, (list, tuple)):
                json_fields.extend(fields)
        if additional_json_fields and isinstance(additional_json_fields, (list, tuple)):
            json_fields.extend(additional_json_fields)

        for c in cls.__table__.columns:
            if c.name in ignored_fields:
                continue
            v = getattr(inst, c.name)
            # These fields will have to be converted from json to python types
            if c.name in json_fields:
                d[c.name] = Util._from_json(v)
            else:
                if c.type in convert.keys() and v is not None:
                    try:
                        d[c.name] = convert[c.type](v)
                    except:
                        d[c.name] = "Error:  Failed to covert using ", str(convert[c.type])
                elif type(v) in (datetime, date):
                    if '_user_tz' in g and g._user_tz and app.config.get('LOCALIZE_DATETIME_TO_USER_TIMEZONE', False):
                        d[c.name] = utc.localize(v, is_dst = None).astimezone(g._user_tz).isoformat()
                    else:
                        d[c.name] = v.isoformat()
                elif v is None:
                    d[c.name] = None
                else:
                    d[c.name] = v
        return d

    @staticmethod
    def parse_integer(val, default = 1):
        try:
            return int(val)
        except ValueError:
            return default

    @staticmethod
    def build_pager(request):
        default_page = app.config['PAGER_DEFAULT_PAGE']
        page = max(Util.parse_integer(request.args.get('page',
            default_page), default_page), default_page)
        default_limit = app.config['PAGER_DEFAULT_LIMIT']
        limit = Util.parse_integer(request.args.get('limit', default_limit), default_limit)
        if limit > app.config['PAGER_DEFAULT_LIMIT_MAX']:
            limit = app.config['PAGER_DEFAULT_LIMIT_MAX']
        order = request.args.get('order', app.config['PAGER_DEFAULT_ORDER_BY_FIELD'])
        order_fields = order.split(',')
        order_list = []
        for field in order_fields:
            item = field.strip()
            # Lets see if field ends with desc or asc (name+asc or name+desc).
            if any(c in item for c in '+ '):
                name = item[:item.index('+' if '+' in item else ' ')]
            else:
                name = item
            if re.match('^[a-zA-Z0-9_]+$', name):
                order_list.append(item)
        if not order_list:
            order_list.append(app.config['PAGER_DEFAULT_ORDER_BY_FIELD'])
        return_fields = request.args.get('return_fields', None)
        return_fields_list = None
        if return_fields:
            return_fields_list = return_fields.split(',')
        search = request.args.get('search', None, type = str)
        return PagerDict({
            "page": page,
            "limit": limit,
            "offset": (page - 1) * limit,
            "start": (page - 1) * limit,
            "stop": (page - 1) * limit + limit - 1,
            "order": order_list,
            "search": search,
            "is_search_request": True if search else False,
            "return_fields": return_fields_list
        })

    @staticmethod
    def paginate_with_pager(klass = None, query = None, pager = None, error_out = False):
        return Util.paginate(klass, query, pager.page, pager.offset,
            pager.limit, pager.order, error_out)

    @staticmethod
    def paginate(klass = None, query = None, page = 1, offset = 0, limit = 10, order = None, error_out = False):
        if error_out and page < 1:
            return None
        order_by_exprs = []
        if order:
            if not isinstance(order, list):
                order = [order]
            for item in order:
                order_items = item.split('+' if '+' in item else ' ')
                name = order_items[0]
                is_desc = True if len(order_items) == 2 and \
                    order_items[1].lower() == 'desc' else False
                for column in inspect(klass).columns:
                    if column.name == name:
                        try:
                            expr = getattr(klass, name)
                        except AttributeError:
                            break
                        if is_desc:
                            order_by_exprs.append(desc_expr(expr))
                        else:
                            order_by_exprs.append(asc_expr(expr))
                        break

        items = query.order_by(*order_by_exprs).limit(
            limit).offset(offset).all()
        if not items and page != 1 and error_out:
            return None

        if page == 1 and len(items) < limit:
            total = len(items)
        else:
            total = query.count()
        return Pagination(query, page, limit, total, items)

    @staticmethod
    def _from_json(value):
        if value:
            try:
                return json.loads(value)
            except ValueError:
                logger.error("Unable to parse json value {0}".format(value))
        return None


# Code blatantly stolen from pyactiveresource and Rails' Inflector
# https://github.com/rails/activeresource
class ModelUtil(object):

    PLURALIZE_PATTERNS = [
        (r'(quiz)$', r'\1zes'),
        (r'^(ox)$', r'\1en'),
        (r'([m|l])ouse$', r'\1ice'),
        (r'(matr|vert|ind)(?:ix|ex)$', r'\1ices'),
        (r'(x|ch|ss|sh)$', r'\1es'),
        (r'([^aeiouy]|qu)y$', r'\1ies'),
        (r'(hive)$', r'1s'),
        (r'(?:([^f])fe|([lr])f)$', r'\1\2ves'),
        (r'sis$', r'ses'),
        (r'([ti])um$', r'\1a'),
        (r'(buffal|tomat)o$', r'\1oes'),
        (r'(bu)s$', r'\1ses'),
        (r'(alias|status)$', r'\1es'),
        (r'(octop|vir)us$', r'\1i'),
        (r'(ax|test)is$', r'\1es'),
        (r's$', 's'),
        (r'$', 's')
    ]

    SINGULARIZE_PATTERNS = [
        (r'(quiz)zes$', r'\1'),
        (r'(matr)ices$', r'\1ix'),
        (r'(vert|ind)ices$', r'\1ex'),
        (r'^(ox)en', r'\1'),
        (r'(alias|status)es$', r'\1'),
        (r'(octop|vir)i$', r'\1us'),
        (r'(cris|ax|test)es$', r'\1is'),
        (r'(shoe)s$', r'\1'),
        (r'(o)es$', r'\1'),
        (r'(bus)es$', r'\1'),
        (r'([m|l])ice$', r'\1ouse'),
        (r'(x|ch|ss|sh)es$', r'\1'),
        (r'(m)ovies$', r'\1ovie'),
        (r'(s)eries$', r'\1eries'),
        (r'([^aeiouy]|qu)ies$', r'\1y'),
        (r'([lr])ves$', r'\1f'),
        (r'(tive)s$', r'\1'),
        (r'(hive)s$', r'\1'),
        (r'([^f])ves$', r'\1fe'),
        (r'(^analy)ses$', r'\1sis'),
        (r'((a)naly|(b)a|(d)iagno|(p)arenthe|(p)rogno|(s)ynop|(t)he)ses$',
         r'\1\2sis'),
        (r'([ti])a$', r'\1um'),
        (r'(n)ews$', r'\1ews'),
        (r's$', r'')
    ]

    IRREGULAR = [
        ('person', 'people'),
        ('man', 'men'),
        ('child', 'children'),
        ('sex', 'sexes'),
        ('move', 'moves'),
        #('cow', 'kine') WTF?
    ]

    UNCOUNTABLES = ['equipment', 'information', 'rice', 'money', 'species',
                    'series', 'fish', 'sheep']

    @staticmethod
    def pluralize(singular):
        """Convert singular word to its plural form.

        Args:
            singular: A word in its singular form.

        Returns:
            The word in its plural form.
        """
        if singular in ModelUtil.UNCOUNTABLES:
            return singular
        for i in ModelUtil.IRREGULAR:
            if i[0] == singular:
                return i[1]
        for i in ModelUtil.PLURALIZE_PATTERNS:
            if re.search(i[0], singular):
                return re.sub(i[0], i[1], singular)

    @staticmethod
    def singularize(plural):
        """Convert plural word to its singular form.

        Args:
            plural: A word in its plural form.
        Returns:
            The word in its singular form.
        """
        if plural in ModelUtil.UNCOUNTABLES:
            return plural
        for i in ModelUtil.IRREGULAR:
            if i[1] == plural:
                return i[0]
        for i in ModelUtil.SINGULARIZE_PATTERNS:
            if re.search(i[0], plural):
                return re.sub(i[0], i[1], plural)
        return plural

    @staticmethod
    def camelize(word):
        """Convert a word from lower_with_underscores to CamelCase.

        Args:
            word: The string to convert.
        Returns:
            The modified string.
        """
        return ''.join(w[0].upper() + w[1:]
                       for w in re.sub('[^A-Z^a-z^0-9^:]+', ' ', word).split(' '))

    @staticmethod
    def underscore(word):
        """Convert a word from CamelCase to lower_with_underscores.

        Args:
            word: The string to convert.
        Returns:
            The modified string.
        """
        return re.sub(r'\B((?<=[a-z])[A-Z]|[A-Z](?=[a-z]))',
                      r'_\1', word).lower()



    @staticmethod
    def create_model(klass = None, attributes = None, additional_attributes = None):
        data = ModelUtil._find_attrs_by_class_name(klass, attributes)
        #Removed null check on data to allow creation of empty entities
        model = ModelUtil._update(klass(), data)
        if additional_attributes and isinstance(additional_attributes, dict):
            model = ModelUtil._update(model, additional_attributes)
        return model

    @staticmethod
    def update_model(model = None, attributes = None, additional_attributes = None):
        data = ModelUtil._find_attrs_by_class_name(model.__class__, attributes)
        if data:
            model = ModelUtil._update(model, data, ignore_attrs = True)
            if additional_attributes and isinstance(additional_attributes, dict):
                model = ModelUtil._update(model, additional_attributes)
            return model
        return None

    @staticmethod
    def _update(model = None, attributes = None, ignore_attrs = False):
        if not isinstance(attributes, dict):
            return model
        ins = inspect(model)
        for key, value in attributes.iteritems():
            if hasattr(model, key):
                # ##############################################################
                # Ignore attributes specified in the IGNORE_ATTRIBUTES_ON_UPDATE
                # array. Thios allows for cleaner API endpoints.
                # ##############################################################
                if ignore_attrs and \
                    hasattr(model, 'IGNORE_ATTRIBUTES_ON_UPDATE') and \
                    model.IGNORE_ATTRIBUTES_ON_UPDATE and \
                    key in model.IGNORE_ATTRIBUTES_ON_UPDATE:
                    continue
                # ##############################################################
                if isinstance(value, dict):
                    klass = ModelUtil._find_class_for(key)
                    fetched = ModelUtil._load_child(
                        klass, value, parent_klass = model.__class__)
                    setattr(model, key, fetched)
                elif isinstance(value, list):
                    klass = None
                    # Flush sqlalchemy lists on transient models before
                    # adding new items. Associations are always refreshed.
                    if not ins.transient:
                        setattr(model, key, [])
                    attr = getattr(model, key)
                    for child in value:
                        if isinstance(child, dict):
                            if klass is None:
                                klass = ModelUtil._find_class_for_collection(key)
                            fetched = ModelUtil._load_child(
                                klass, child, parent_klass = model.__class__)
                            if fetched:
                                attr.append(fetched)
                        else:
                            attr.append(child)
                else:
                    # Handle iso8601 dates, and datetime (or date) in general.
                    column = getattr(model.__class__, key)
                    if column and hasattr(column, 'type') and \
                        isinstance(column.type, DateTime):
                        if isinstance(value, date) or \
                            isinstance(value, datetime):
                            setattr(model, key, value)
                        else:
                            if value:
                                parsed_date = ModelUtil._parse_iso8601(value)
                                if parsed_date:
                                    setattr(model, key, parsed_date)
                                else:
                                    logger.warn("Unable to parse datetime value %s for the %s field" % (value, key))
                    else:
                        setattr(model, key, value)
        return model

    @staticmethod
    def _find_attrs_by_class_name(klass, attributes):
        for cls in getmro(klass):
            name = ModelUtil.underscore(cls.__name__)
            if name in attributes:
                return attributes[name]
        return None

    @staticmethod
    def extract_attrs_by_key(klass, attributes, key, remove = True):
        for cls in getmro(klass):
            name = ModelUtil.underscore(cls.__name__)
            if name in attributes and \
                key and key in attributes[name]:
                    if not remove:
                        return attributes[name][key]
                    else:
                        return attributes[name].pop(key)
        return None

    @staticmethod
    def _load_child(klass = None, attributes = None, parent_klass = None):
        if not klass:
            return None
        # Handle association classes. We should find a better way to handle associations,
        # but since we have the only one (MessageUser), this hard-coded hack should work
        # fine, for now.
        if klass.__name__ == 'MessageUser':
            # Take the opposite association. If parent is message take user, if parent is user take message.
            # We'll only be looking for association class with two relationships.
            associations = [relation.mapper.class_ for relation in inspect(klass).relationships]
            child_klass = None
            if len(associations) == 2 and parent_klass:
                if associations[0] == parent_klass:
                    child_klass = associations[1]
                else:
                    child_klass = associations[0]
            if child_klass:
                for key, value in attributes.iteritems():
                    if key == 'id' and hasattr(child_klass, key):
                        if child_klass.__name__ == 'User':
                            return klass(user = child_klass.query.filter_by(id = value).first())
        else:
            for key, value in attributes.iteritems():
                if key == 'id' and hasattr(klass, key):
                    return klass.query.filter_by(id = value).first()
        return None

    @staticmethod
    def _find_class_for_collection(collection_name = None):
        return ModelUtil._find_class_for(ModelUtil.singularize(collection_name))

    @staticmethod
    def _find_class_for(element_name = None, table_name = None):
        from sqlalchemy.orm import mapperlib
        for x in mapperlib._mapper_registry.items():
            if x[0].mapped_table.name == table_name:
                return x[0].class_
            if element_name and x[0].class_.__name__ == ModelUtil.camelize(element_name):
                return x[0].class_
        return None

    @staticmethod
    def _parse_iso8601(iso8601 = None):
        # TODO: Make this function better.
        # This function is complete bs. Parsing iso8601 dates is very hard.
        # We should use some proper lib, such as aniso8601, or dateutils.
        # Also, do we care about py 3.x?
        if not iso8601 or not isinstance(iso8601, basestring):
            return None
        iso8601 = iso8601.strip()
        try:
            struct = strptime(
                iso8601.replace("-", ""), "%Y%m%dT%H:%M:%S")
            return datetime.fromtimestamp(mktime(struct))
        except ValueError, ex:
            logger.error(ex)
        return None

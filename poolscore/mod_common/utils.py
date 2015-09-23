import json
import re
from functools import wraps

from flask import request, Response, redirect, \
                g, url_for, session, abort, jsonify, \
                json, current_app, make_response
from sqlalchemy.sql import text
from pytz import timezone, utc, all_timezones_set
from pytz.exceptions import UnknownTimeZoneError

from poolscore import app
from poolscore import db

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
    def not_authenticated_error_response():
        return redirect(url_for('auth.login'))


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

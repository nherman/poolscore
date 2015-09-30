from sqlalchemy import event, insert
from sqlalchemy.ext.declarative import declared_attr

from flask import g

from poolscore.mod_common.utils import Util
from poolscore import db
from poolscore import app

class PermissionsError(Exception):
    pass

class Base(db.Model):

    __abstract__  = True
    __table_args__ = {'mysql_collate': 'utf8_unicode_ci', 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    JSON_SERIALIZATION_IGNORED_FIELDS = [
        "password",
    ]

    # These attributes are ignored for the UPDATE statements
    IGNORE_ATTRIBUTES_ON_UPDATE = ['id', 'date_created', 'date_modified']

    id = db.Column(db.Integer, primary_key = True)
    date_created = db.Column(db.DateTime, default = db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default = db.func.current_timestamp(),
        onupdate = db.func.current_timestamp())
    active = db.Column(db.Boolean, nullable = False, default = True)

    @classmethod
    def secure_all(cls):
        '''return all objects the user has permission to view'''
        return cls.secure_query().all()

    @classmethod
    def secure_query(cls):
        '''return modified query to filter results based on user permissions'''

        if g._user_auth_token["user_id"] == None:
            raise PermissionsError

        return cls.query.join(EntityUser, cls.id == EntityUser.row_id).\
            filter(cls.__name__ == EntityUser.entity, g._user_auth_token["user_id"] == EntityUser.user_id)




@event.listens_for(Base, 'before_update', propagate=True)
def before_update_listener(mapper, connection, target):
    if (g._user_auth_token["user_id"]):
        perms = EntityUser.query.filter_by(entity = target.__class__.__name__, row_id = target.id)
        for p in perms:
            if p.user_id == g._user_auth_token["user_id"]:
                return
    raise PermissionsError()


@event.listens_for(Base, 'after_insert', propagate=True)
def after_insert_listener(mapper, connection, target):
    statement = insert(EntityUser).values(entity=target.__class__.__name__, row_id=target.id, user_id=g._user_auth_token["user_id"])
    connection.execute(statement)


class EntityUser(db.Model):

    __tablename__ = "entityuser"

    # Entity Name
    entity = db.Column(db.String(32), primary_key=True)
    # Row ID
    row_id = db.Column(db.Integer, primary_key=True)
    # USer ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    # New instance instantiation procedure
    def __init__(self, entity = None, row_id = None, user_id = None):
        self.entity = entity
        self.row_id = row_id
        self.user_id = user_id

    def __repr__(self):
        return '<EntityUser %r, row: %r, uid: %r>' % (self.entity, self.row_id, self.user_id)



class Session(Base):

    __tablename__ = 'session'

    def __init__(self, session_id = None, data = None, expiration = None):
        self.session_id = session_id
        self.data = data
        self.expiration = expiration

    # Session Id
    session_id = db.Column(db.String(255), nullable = False, unique = True)
    # Session data
    data = db.Column(db.LargeBinary, nullable = True)
    # Session expiration time in seconds
    expiration = db.Column(db.Integer, default = 0, nullable = False)

    def __repr__(self):
        return '<Session %r, %r>' % (self.id, self.session_id)

    @property
    def serialize(self):
        return Util.to_serializable_dict(self, self.__class__)


from sqlalchemy import event, insert
from sqlalchemy.ext.declarative import declared_attr

from flask import g

from poolscore.mod_common.utils import Util, SecurityUtil
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
    IGNORE_ATTRIBUTES_ON_UPDATE = ['id', 'date_created', 'date_modified', 'ordinal']

    id = db.Column(db.Integer, primary_key = True)
    date_created = db.Column(db.DateTime, default = db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default = db.func.current_timestamp(),
        onupdate = db.func.current_timestamp())
    active = db.Column(db.Boolean, nullable = False, default = True)
    deleted = db.Column(db.Boolean, nullable = True, default = False)

    @classmethod
    def secure_all(cls):
        '''return all objects the user has permission to view'''
        return cls.secure_query().all()

    @classmethod
    def secure_query(cls):
        '''return modified query to filter results based on user permissions'''

        if g._user_auth_token["user_id"] == None:
            raise PermissionsError

        query = cls._query().join(EntityUser, cls.id == EntityUser.row_id).\
            filter(cls.__name__ == EntityUser.entity, g._user_auth_token["user_id"] == EntityUser.user_id)

        return query

    @classmethod
    def _query(cls, hide_deleted = True):
        q = cls.query
        if (hide_deleted):
            q = q.filter(cls.deleted != True)
        return q

    @classmethod
    def has_entityUser(cls, row_id = None, user_id = None):
        if (user_id == None):
            user_id = g._user_auth_token["user_id"]  
        if (row_id != None and user_id != None):            
            perms = EntityUser.query.filter_by(entity = cls.__name__, row_id = row_id, user_id = user_id).count()
            return (perms > 0)
        return False

    def has_permission(self, user_id = None):
        return SecurityUtil.is_admin() or self.__class__.has_entityUser(row_id = self.id, user_id = user_id)

    def grant_permission(self, user_id, connection = None):
        if user_id != None:
            existing_permission = EntityUser.query.filter_by(entity=self.__class__.__name__, row_id=self.id, user_id=user_id).first()

            if existing_permission == None:
                statement = insert(EntityUser).values(entity=self.__class__.__name__, row_id=self.id, user_id=user_id)

                if connection != None:
                    connection.execute(statement)
                else:
                    connection = db.engine.connect()
                    connection.execute(statement)
                    connection.close()

    def revoke_permission(self, user_id):
        if user_id != None and user_id != g._user_auth_token["user_id"]:
            entityuser = EntityUser.query.filter_by(entity=self.__class__.__name__, row_id=self.id, user_id=user_id).first()

            if entityuser != None:
                db.session.delete(entityuser)

    def delete(self):
        self.deleted = True
        self.active = False
        db.session.merge(self)


@event.listens_for(Base, 'before_update', propagate=True)
def before_update_listener(mapper, connection, target):
    if not target.has_permission(g._user_auth_token["user_id"]):
        raise PermissionsError()


@event.listens_for(Base, 'after_insert', propagate=True)
def after_insert_listener(mapper, connection, target):
    target.grant_permission(g._user_auth_token["user_id"], connection)


class EntityUser(db.Model):

    __tablename__ = "entityuser"

    # Entity Name
    entity = db.Column(db.String(32), primary_key=True)
    # Row ID
    row_id = db.Column(db.Integer, primary_key=True)
    # User ID
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


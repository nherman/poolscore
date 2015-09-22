from poolscore.mod_common.utils import Util
from poolscore import db
from poolscore import app

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


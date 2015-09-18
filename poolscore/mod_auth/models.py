from sqlalchemy.orm import relationship, backref
from sqlalchemy.exc import SQLAlchemyError
from werkzeug import check_password_hash, generate_password_hash

from poolscore import db
from poolscore.mod_common import models as common_models
from poolscore.mod_common.utils import Util, ModelUtil


def _extract_profile_dict(klass, attributes):
    key = ModelUtil.singularize(klass.__tablename__)
    if attributes and isinstance(attributes, dict) and key in attributes:
        profile = attributes[key]
        if isinstance(profile, dict):
            return profile
    return None

# User model
class User(common_models.Base):

    __tablename__ = 'user'
   
    # User First Name
    first_name = db.Column(db.String(128), nullable = False)
    # User Last Name
    last_name = db.Column(db.String(128), nullable = True)
    # User email
    email = db.Column(db.String(128), nullable = False, index = True, unique = True)
    # Username
    username = db.Column(db.String(128), nullable = False, index = True, unique = True)
    # User password
    password = db.Column(db.String(192), nullable = False)
    # User timezone
    timezone = db.Column(db.String(64), nullable = False, default = 'US/Eastern')

    # New instance instantiation procedure
    def __init__(self, first_name = None,
        last_name = None, email = None,
        username = None, password = None,
        active = False):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password = password
        self.active = active

    def __repr__(self):
        return '<User %r, %r, %r>' % (self.id, self.email, self.username)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_password(self, attributes = None):
        profile = _extract_profile_dict(User, attributes)
        if profile:
            password = profile.get('password')
            old_password = profile.get('_password')
            if self.check_password(old_password) and password:
                self.password = password
                return True
        return False

    def update_profile(self, attributes = None):
        profile = _extract_profile_dict(User, attributes)
        if profile:
            self.first_name = profile.get('first_name')
            self.last_name = profile.get('last_name')
            return True
        return False

    @property
    def serialize(self):
        d = Util.to_serializable_dict(self, self.__class__)
#        d['groups'] = [group.serialize_shallow for group in self.groups]
#        d['roles'] = [role.serialize for role in self.roles]
        return d

    @property
    def serialize_text(self):
        name = "{0} {1}".format(self.first_name, 
            self.last_name if self.last_name else "").strip()
        return "%s%s" % ("%s@%s" % (self.username, self.xmpp_domain,),
            "=%s" % name if name else "")

    @property
    def serialize_shallow(self):
        d = Util.to_serializable_dict(self, self.__class__)
        return d

    @property
    def serialize_profile(self):
        return dict(
            id = self.id,
            first_name = self.first_name,
            last_name = self.last_name,
            email = self.email,
            username = self.username,
            vcard = self.vcard)

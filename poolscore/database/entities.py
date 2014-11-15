#models
class Base(object):
    DEFAULT_VALUES = {}

    def __init__(self, **kwargs):
        self._data = kwargs
        for key in self.DEFAULT_VALUES:
            if key not in self._data:
                self._data[key] = self.DEFAULT_VALUES[key]

    def __getattr__(self, name):
        if not name in self._data:
            raise AttributeError("Cannot find attribute " + name + ".")
        return self._data[name]

    def __setattr__(self, name, value):
        if name == "_data":
            super(Base, self).__setattr__(name, value)
        else:
            if "_data" in self.__dict__:
                self.__dict__["_data"][name] = value

    @classmethod
    def get_table_name(self):
        return self.__name__.lower()


class Account(Base):
    DEFAULT_VALUES = {
        'active':           True
    }        
class League(Base):
    pass

class Division(Base):
    pass

class Team(Base):
    pass

class Player(Base):
    pass

class Tourney(Base):
    DEFAULT_VALUES = {
        'home_matches':     0,
        'away_matches':     0,
        'in_progress':      True,
        'locked':           False
    }

class Match(Base):
    DEFAULT_VALUES = {
        'home_games':       0,
        'away_games':       0,
        'in_progress':      True,
        'locked':           False
    }

class Game(Base):
    DEFAULT_VALUES = {
        'innings':          0,
        'in_progress':      True,
        'locked':           False
    }
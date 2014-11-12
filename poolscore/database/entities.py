#models
class Base(object):

    #abstract init method
    def __init__(self, **kwargs):
        self._data = kwargs

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
    pass
        
class League(Base):
    pass

class Division(Base):
    pass

class Team(Base):
    pass

class Player(Base):
    pass

class Tourney(Base):
    pass

class Match(Base):
    pass

class Game(Base):
    pass

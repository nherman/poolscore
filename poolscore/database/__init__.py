###
# Database initialization and helpers
###
import sqlite3 as lite
import os
from .entities import User

LOCAL_DIR = os.path.abspath(os.path.dirname(__file__))  
DEFAULT_DB_PATH = os.path.join(LOCAL_DIR, 'poolscore.db')

class DbManager():
    '''Class db:
    handle basic database connection and querying
    '''

    def __init__(self):
        self.db = None

    def open(self, db_config=None):
        '''get new db connection'''

        if self.db is None:
            if db_config == None:
                db_config = DEFAULT_DB_PATH
            self.db = lite.connect(db_config)
            self.db.row_factory = self.make_dicts
        return self

    def close(self):
        '''close existing db connection'''

        if self.db is not None:
            self.db.close()

    def make_dicts(self, cursor, row):
        '''sqlite3 row factory
        force db connection to always return dictionaries
        '''

        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def init_db(self):
        '''drop and recreate db'''

        if self.db == None:
            get()

        schema = os.path.join(LOCAL_DIR, 'schema.sql')
        with os.open(schema, 'r') as f:
            self.db.cursor().executescript(f.read())
        self.db.commit()

    def bootstrap_db(self):
        '''insert dev data into database'''
        if self.db == None:
            get()

        sql = os.path.join(LOCAL_DIR, 'bootstrap.sql')
        with os.open(sql, mode='r') as f:
            self.db.cursor().executescript(f.read())
        self.db.commit()

    def query_db(self, query, args=(), one=False):
        '''query helper: handles creating cursor and executing queries'''

        if self.db == None:
            raise StandardError("Cannot query database: db connection not opened")

        cur = self.db.execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    def get_instance_by_id(self, cls, id):
        if (cls.__tablename__ != None and id != None):
            statement = "SELECT * FROM " + cls.__tablename__ + " tbl WHERE tbl.id=?"
            data = self.query_db(statement, [id], one=True)
            return cls(data)

    def get_password_by_username(self, username):
        return self.query_db('SELECT a.active, p.password FROM accounts a JOIN password p ON a.id = p.account_id WHERE a.username=?', [username], one=True)

    def get_user_by_name(self, username):
        if (username != None):
            data = self.query_db("SELECT * FROM accounts WHERE accounts.username=?",
                [username], one=True)
            return User(data)


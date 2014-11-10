###
# Database initialization and helpers
###
from datetime import datetime
import sqlite3 as lite
import os
from .entities import Account

LOCAL_DIR = os.path.abspath(os.path.dirname(__file__))  
DEFAULT_DB_PATH = "/tmp/poolscore.db"

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

    def __execute_sql__(self, query, args=()):
        '''execute a query and return the cursor'''

        if self.db == None:
            raise StandardError("Cannot query database: db connection not opened")

        return self.db.execute(query, args)

    def query_db(self, query, args=(), one=False):
        '''query DB and return results'''
        cur = self.__execute_sql__(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    def update_db(self, query, args=(), one=False):
        '''upate DB and return id of last updated row'''
        cur = self.__execute_sql__(query, args)
        self.db.commit()
        lastRowId = cur.lastrowid
        cur.close()
        return lastRowId

    def getInstanceById(self, cls, id):
        if (cls.__tablename__ != None and id != None):
            statement = "SELECT * FROM " + cls.__tablename__ + " tbl WHERE tbl.id=?"
            data = self.query_db(statement, [id], one=True)
            return cls(**data)

    def storeInstance(self, inst):
        if ('id' in inst.__dict__):
            #assume row already exists and do update
            vals = []
            sql = "UPDATE " + inst.__tablename__ + " SET "

            for key in inst.__dict__.keys():
                if (not key in ["id","date_created"]):
                    sql += key + " = ?,"
                    if (key == "date_modified"):
                        vals.append(datetime.now())
                    else:
                        vals.append(inst.__dict__[key])
            sql = sql[:-1] #remove trailing comma

            sql += " WHERE id = ?"
            vals.append(inst.id)

            print(sql)

            return self.update_db(sql, vals)

        else:
            key_list = ",".join(inst.__dict__.keys())
            vals = "?,"*len(inst.__dict__.keys())
            vals = vals[:-1]
            sql = "INSERT into {0} ({1}) VALUES ({2})".format(inst.__tablename__, key_list, vals)

            return self.update_db(sql,inst.__dict__.values())

    def getPasswordByUsername(self, username):
        return self.query_db('SELECT a.active, p.password FROM accounts a JOIN password p ON a.id = p.account_id WHERE a.username=?', [username], one=True)

    def getAccountByUsername(self, username):
        if (username != None):
            data = self.query_db("SELECT * FROM accounts WHERE accounts.username=?",
                [username], one=True)
            return Account(**data)

    def getTeamsByAccountId(self, account_id):
        return self.query_db('SELECT * from team t WHERE t.account_id = ?',[account_id],one=False)

    def getMatchesByTourneyId(self, tourney_id):
        return self.query_db('SELECT * from match m WHERE m.tourney_id = ?',[tourney_id],one=False)

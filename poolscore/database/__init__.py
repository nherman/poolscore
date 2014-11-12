###
# Database initialization and helpers
###
from datetime import datetime
import sqlite3 as lite
import os
from .entities import Account

LOCAL_DIR = os.path.abspath(os.path.dirname(__file__))  
DEFAULT_DB_PATH = "/tmp/poolscore.db"

class PermissionsError(Exception):
    pass

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

    def getInstanceById(self, cls, id, account_id):
        if (cls.get_table_name() != None and id != None):
            statement = "SELECT tbl.* FROM " + cls.get_table_name() + " tbl \
                         JOIN permissions p ON p.row_id = tbl.id \
                         WHERE p.entity = ? AND p.account_id = ? \
                         AND tbl.id = ?"

            data = self.query_db(statement, (cls.__name__, account_id, id), one=True)
            if (data == None):
                return None
            print("Getting {} for ID: {}".format(cls.__name__, id))

            return cls(**data)

    def storeInstance(self, inst, account_id):
        if ('id' in inst._data):
            #check permissions
            perms = self.query_db("SELECT * FROM permissions where entity = ? and row_id = ?",
                {'entity':inst.__class__.__name__, 'row_id':inst.id},
                one=True)
            if (perms == None or perms['account_id'] != account_id):
                raise permissionsError()

            #assume row already exists and do update
            vals = []
            sql = "UPDATE " + inst.get_table_name() + " SET "

            for key in inst._data.keys():
                if (not key in ["id","date_created"]):
                    sql += key + " = ?,"
                    if (key == "date_modified"):
                        vals.append(datetime.now())
                    else:
                        vals.append(inst._data[key])
            sql = sql[:-1] #remove trailing comma

            sql += " WHERE id = ?"
            vals.append(inst.id)

            print(sql)

            return self.update_db(sql, vals)

        else:
            print(inst)
            key_list = ",".join(inst._data.keys())
            print(key_list)
            vals = "?,"*len(inst._data.keys())
            vals = vals[:-1]
            SQL = "INSERT into {0} ({1}) VALUES ({2})".format(inst.get_table_name(), key_list, vals)
            id = self.update_db(SQL,inst._data.values())

            #record owner in permissions table
            permSQL = "INSERT into permissions (entity, row_id, account_id) VALUES (?,?,?)"
            permId = self.update_db(permSQL,
                    (inst.__class__.__name__, id, account_id))
            return id


    def getPasswordByUsername(self, username):
        return self.query_db('SELECT a.active, p.password FROM accounts a JOIN password p ON a.id = p.account_id WHERE a.username=?', [username], one=True)

    def getAccountByUsername(self, username):
        if (username != None):
            data = self.query_db("SELECT * FROM accounts WHERE accounts.username=?",
                [username], one=True)
            return Account(**data)

    def getTeamsByAccountId(self, account_id):
        return self.query_db('SELECT * from team t WHERE t.account_id = ?',[account_id],one=False)

    def getTourneyCountByAccountId(self, account_id):
        return self.query_db('SELECT count(*) as count from permissions p WHERE p.entity=? AND p.account_id=?',
            ("Tourney", account_id), one=True)

    def getTourneyListByAccountId(self, account_id):
        # get tourneys
        tourneys = self.query_db('SELECT t.id, t.date, t.home_team_id, t.away_team_id, t.in_progress, t.locked \
            from tourney t JOIN permissions p ON t.id = p.row_id WHERE p.entity=? AND p.account_id=?',
            ("Tourney", account_id))

        # get team names
        for tourney in tourneys:
            tourney['home_team'] = self.query_db('SELECT t.name, t.location from team t \
                JOIN permissions p ON t.id = p.row_id WHERE p.entity=? AND p.account_id=? AND t.id = ?',
            ("Team", account_id, tourney['home_team_id']), one=True)
            tourney['away_team'] = self.query_db('SELECT t.name, t.location from team t \
                JOIN permissions p ON t.id = p.row_id WHERE p.entity=? AND p.account_id=? AND t.id = ?',
            ("Team", account_id, tourney['away_team_id']), one=True)

        return tourneys

    def getMatchesByTourneyId(self, tourney_id):
        return self.query_db('SELECT * from match m WHERE m.tourney_id = ?',[tourney_id],one=False)

    def getGamesByMatchId(self, match_id):
        return self.query_db('SELECT * from game m WHERE m.match_id = ?',[match_id],one=False)

    def getPlayersByAccountIdForTeam(self, account_id, team_id):
        SQL = "SELECT * from player pl \
               JOIN team_player tp ON pl.id = tp.player_id \
               JOIN permissions p ON pl.id = p.row_id \
               WHERE p.entity=? AND p.account_id=? \
               AND tp.team_id = ?"
        return self.query_db(SQL, ("Player", account_id, team_id))

    def getPlayersByAccountIdNotOnTeams(self, account_id, teams):
        team_str = ""
        #there has to be a better way!
        for i,v in enumerate(teams):
            team_str += "\'" + str(v) + "\'"
            if i < len(teams)-1:
                team_str += ","

        SQL = "SELECT * FROM player pl \
               JOIN permissions p ON p.row_id = pl.id \
               JOIN team_player tp ON tp.player_id = pl.id \
               WHERE p.entity=? AND p.account_id=? \
               AND tp.team_id NOT IN (?)"

        return self.query_db(SQL, ("Player", account_id, team_str))

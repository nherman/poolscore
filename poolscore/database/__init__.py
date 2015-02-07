###
# Database initialization and helpers
###
from datetime import datetime
import sqlite3 as lite
import os
from .entities import Account, Match

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

    def update_db(self, query, args=()):
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
                (inst.__class__.__name__, inst.id),
                one=True)
            if (perms == None or perms['account_id'] != account_id):
                raise PermissionsError()

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

            return self.update_db(sql, vals)

        else:
            key_list = ",".join(inst._data.keys())
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
        MATCH_SQL = "SELECT * from match m WHERE m.tourney_id = ?"
        PLAYER_SQL = "SELECT p.* from player p \
               JOIN match_player mp ON p.id = mp.player_id \
               WHERE mp.match_id = ? AND mp.is_home_team = ?"

        matches = self.query_db(MATCH_SQL,[tourney_id])

        for match in matches:
            match["home_players"] = self.query_db(PLAYER_SQL,(match['id'],True))
            match["away_players"] = self.query_db(PLAYER_SQL,(match['id'],False))

        return matches


    def getGamesByMatchId(self, match_id):
        return self.query_db('SELECT * from game m WHERE m.match_id = ?',[match_id],one=False)

    def getGameEventsByMatchId(self, match_id, events_dict):
        game_ids = self.query_db('SELECT id from game m WHERE m.match_id = ?',[match_id],one=False)
        event_list = {}

        for game in game_ids:
            event_list[game['id']] = self.getGameEvents(game['id'],events_dict)
            print(event_list)


        return event_list

    def getPlayersByAccountIdForTeam(self, account_id, team_id):
        SQL = "SELECT pl.* from player pl \
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

        SQL = "SELECT pl.* FROM player pl \
               JOIN permissions p ON p.row_id = pl.id \
               JOIN team_player tp ON tp.player_id = pl.id \
               WHERE p.entity=? AND p.account_id=? \
               AND tp.team_id NOT IN (?)"

        return self.query_db(SQL, ("Player", account_id, team_str))

    def getNumMatchesForTourney(self, tourney_id):
        SQL = "SELECT count(*) AS count from match m WHERE m.tourney_id = ?"

        data = self.query_db(SQL,[tourney_id],one=True)
        return data['count']

    def setMatchPlayers(self, match_id, players, is_home_team):
        SQL = "INSERT INTO match_player (match_id, player_id, is_home_team) VALUES (?, ?, ?)"

        if isinstance(players,list):
            for player_id in players:
                self.update_db(SQL,(match_id, player_id, is_home_team))
        elif isinstance(players, int):
            self.update_db(SQL,(match_id, players, is_home_team))
        else:
            raise AttributeError("players must be an integer or a list of integers")


    def getMatchPlayers(self, match_id, is_home_team, account_id):
        SQL = "SELECT pl.* FROM player pl \
               JOIN match_player mp ON pl.id = mp.player_id \
               JOIN permissions p ON pl.id = p.row_id \
               WHERE p.entity = ? AND p.account_id = ? \
               AND mp.match_id = ? AND mp.is_home_team = ?"

        return self.query_db(SQL,("Player", account_id, match_id, is_home_team))
        
    def getNumGamesForMatch(self, match_id):
        SQL = "SELECT count(*) AS count from game g WHERE g.match_id = ?"

        data = self.query_db(SQL,[match_id],one=True)
        return data['count']

    def getLastGameWinner(self, match_id):
        SQL="SELECT winner from game g WHERE g.match_id = ? ORDER BY g.ordinal DESC LIMIT 1"

        data = self.query_db(SQL,[match_id],one=True)

        if data != None:
            return data['winner']
        else:
            return None

    def getGameEvents(self, game_id, events_dict):
        ret = {}
        SQL="SELECT * from game_events WHERE game_id = ?"

        #copy defaults
        for key in events_dict:
            ret[key] = events_dict[key]

        #get stored events
        events = self.query_db(SQL,[game_id])

        #update dict with stored values
        for event in events:
            ret[event["name"]] = event["value"]

        return ret

    def getGameEvent(self, game_id, event_name, event_tuple):
        SQL="SELECT value from game_events WHERE game_id = ? AND name = ?"

        data = self.query_db(SQL,[game_id,event_name],one=True)

        if (data == None):
            return event_tuple[1]
        else:
            return data


    def setGameEvent(self, game_id, event_name, event_tuple, value):
        SQL1="SELECT count(*) as count from game_events WHERE game_id = ? AND name = ?"
        data = self.query_db(SQL1,[game_id,event_name],one=True)

        print("id: {} name: {} count: {}".format(game_id,event_name, data["count"]))


        if (data["count"] > 0):
            SQL2 = "UPDATE game_events SET value = ? WHERE game_id = ? AND name = ?"
        else:
            SQL2 = "INSERT INTO game_events (value, game_id, name) VALUES (?, ?, ?)"


        if isinstance(value, event_tuple[0]) and (event_tuple[0] != int or value >= 0):
            self.update_db(SQL2,(value, game_id, event_name))
        else:
            raise AttributeError("Event {} requires a value of type {}".format(event_name,event_tuple[0]))


    def getMatchScore(self, match_id):
        SQL = "SELECT count(*) as games from game WHERE match_id = ? AND winner = ?"

        home = self.query_db(SQL,[match_id,"home"],one=True)
        away = self.query_db(SQL,[match_id,"away"],one=True)

        return {"HOME":home['games'],"AWAY":away['games']}

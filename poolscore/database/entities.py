#models
class Base(object):

    id            = None
    date_created  = None
    date_modified = None

    #abstract init method
    def __init__(self, kwargs):
        self.id             = kwargs['id']
        self.date_created   = kwargs['date_created']
        self.date_modified  = kwargs['date_modified']


class User(Base):

    __tablename__ = 'accounts'

    username    = ""
    email       = ""
    firstname   = ""
    lastname    = ""
    language    = ""
    active      = None

    def __init__(self, kwargs):
        super(User, self).__init__(kwargs)
        
        self.username   = kwargs['username']
        self.email      = kwargs['email']
        self.firstname  = kwargs['firstname']
        self.lastname   = kwargs['lastname']
        self.language   = kwargs['language']
        self.active     = kwargs['active']
        

class League(Base):

    __tablename__ = 'league'

    name        = ""
    shortname   = ""

    def __init__(self, kwargs):
        super(League, self).__init__(kwargs)
        
        self.name       = kwargs['name']
        self.shortname  = kwargs['shortname']


class Division(Base):

    __tablename__ = 'division'

    name        = ""
    leagueId   = ""

    def __init__(self, kwargs):
        super(Division, self).__init__(kwargs)
        
        self.name       = kwargs['name']
        self.leagueId   = kwargs['leagueId']


class Team(Base):

    __tablename__ = 'team'

    name        = ""
    accountId   = ""
    leageNum    = ""
    leagueId    = ""
    divisionId  = ""

    def __init__(self, kwargs):
        super(Team, self).__init__(kwargs)
        
        self.name       = kwargs['name']
        self.accountId  = kwargs['accountId']
        self.leagueNum  = kwargs['leagueNum']
        self.leagueId   = kwargs['leagueId']
        self.divisionId = kwargs['divisionId']


class Player(Base):

    __tablename__ = 'player'

    name        = ""
    leageNum    = ""
    handicap  = ""

    def __init__(self, kwargs):
        super(Player, self).__init__(kwargs)
        
        self.name       = kwargs['name']
        self.leagueNum  = kwargs['leagueNum']
        self.handicap   = kwargs['handicap']


class Tourney(Base):

    __tablename__ = 'tourney'

    date        = None
    homeTeamId  = ""
    awayTeamId  = ""
    homeGames   = 0
    awayGames   = 0
    winner      = None
    in_progress = True
    locked      = False
    data        = {}

    def __init__(self, kwargs):
        super(Tourney, self).__init__(kwargs)

        self.date           = kwargs['date']
        self.homeTeamId     = kwargs['homeTeamId']
        self.awayTeamId     = kwargs['awayTeamId']
        self.ruleset        = kwargs['ruleset']
        self.scoringMethod  = kwargs['scoringMethod']
        

class Match(Base):

    __tablename__ = 'match'

    touneyId        = None
    homePlayerIds   = ""
    awayPlayerIds   = ""
    homeGames       = 0
    awayGames       = 0
    winner          = None
    in_progress     = True
    locked          = False
    data            = {}


    def __init__(self, kwargs):
        super(Match, self).__init__(kwargs)

        self.touneyId       = kwargs['touneyId']
        self.homePlayerIds  = kwargs['homePlayerIds']
        self.awayPlayerIds  = kwargs['awayPlayerIds']
        self.homeGames      = kwargs['homeGames']
        self.awayGames      = kwargs['awayGames']
        self.winner         = kwargs['winner']
        self.in_progress    = kwargs['in_progress']
        self.data           = kwargs['data']


class Game(Base):

    __tablename__ = 'match'

    matchId     = None
    breaker     = ""
    innings     = ""
    win_type    = 0
    loss_type   = 0
    winner      = None
    in_progress = True
    locked      = False
    data        = {}


    def __init__(self, kwargs):
        super(Match, self).__init__(kwargs)

        self.matchId        = kwargs['matchId']
        self.breaker        = kwargs['breaker']
        self.innings        = kwargs['innings']
        self.win_type       = kwargs['win_type']
        self.loss_type      = kwargs['loss_type']
        self.winner         = kwargs['winner']
        self.in_progress    = kwargs['in_progress']
        self.data           = kwargs['data']


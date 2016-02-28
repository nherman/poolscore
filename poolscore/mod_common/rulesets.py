import handicaps

class Ruleset(object):

    def handicap(*args):
        if args.length >= 2:
            return self.handicaper(args)
        else:
            raise TypeError

    def __init__(self, name = None, handicaper = None, tourney_events = {}, match_events = {}, game_events = {}, **kwargs):
        self.name = name
        self.handicaper = handicaper
        self.tourney_events = tourney_events
        self.match_events = match_events
        self.game_events = game_events

        for key in kwargs:
            if key not in self.__dict__:
                self.__dict__[key] = kwargs[key]


    def __repr__(self):
        return '<Ruleset %r>' % (self.name)



apa8ball_tourney_events = {
    "coin_toss": None,
    "player_choice": None,
    "start_time": None,
    "end_time": None
}

apa8ball_match_events = {
    "lag": None,
    "sweep": False,
    "rubber": False
}

apa8ball_game_events = {
    "breaker":None,
    "innings": 0,
    "home_coaches": 0,
    "home_safes": 0,
    "away_coaches": 0,
    "away_safes": 0,
    "8 break": False,
    "break & run": False,
    "early 8": False,
    "scratch 8": False
}

Rulesets = {
    "APA8BALL": Ruleset(
                    name = "APA8BALL",
                    handicaper = handicaps.APA8BALL,
                    tourney_events = apa8ball_tourney_events,
                    match_events = apa8ball_match_events,
                    game_events = apa8ball_game_events
                )
}

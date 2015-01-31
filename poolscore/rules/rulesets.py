import handicaps

class Ruleset(object):

    def __init__(self,
                 name,
                 handicaper,
                 tourney_events = {},
                 match_events = {},
                 game_events = {},
                 **kwargs):
        self.name = name
        self.handicaper = handicaper
        self.tourney_events = tourney_events
        self.match_events = match_events
        self.game_events = game_events

        for key in kwargs:
            if key not in self.__dict__:
                self.__dict__[key] = kwargs[key]


    def handicap(*args):
        if args.length >= 2:
            return self.handicaper(args)
        else:
            raise TypeError

# "static"
# {"event_name": ( ["Valid","Values"], "Default Value" ) }
apa8ball_tourney_events = {
    "coin_toss": (int,None),
    "player_choice": (int,None)
}

apa8ball_match_events = {
    "lag": (int,None),
    "sweep": (bool,False),
    "rubber": (bool,False)
}

apa8ball_game_events = {
    "breaker":(int,None),
    "innings": (int,0),
    "home_coaches": (int,0),
    "home_safes": (int,0),
    "away_coaches": (int,0),
    "away_safes": (int,0),
    "8 break": (bool,False),
    "break & run": (bool,False),
    "early 8": (bool,False),
    "scratch 8": (bool,False)
}

RULESETS = {
    "APA8BALL": Ruleset(
                    name = "APA8BALL",
                    handicaper = handicaps.APA8BALL,
                    tourney_events = apa8ball_tourney_events,
                    match_events = apa8ball_match_events,
                    game_events = apa8ball_game_events
                )
}

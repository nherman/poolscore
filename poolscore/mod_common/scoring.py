from functools import wraps

def scoringDecorator(f):
    @wraps(f)
    def decorated(team1_games,
                  team1_needed,
                  team2_games,
                  team2_needed):

        if (
            (team1_games < team1_needed or team2_games < team2_needed)
            and
            (team1_games == team1_needed or team2_games == team2_needed)
           ):

            return f(team1_games=team1_games,
                     team1_needed=team1_needed,
                     team2_games=team2_games,
                     team2_needed=team2_needed)

        else:
            raise TypeError

    return decorated


@scoringDecorator
def STANDARD(**kwargs):
    '''One point for a win'''
    if (kwargs[team1_games] == kwargs[team1_needed]):
        return (1,0)
    else:
        return (0,1)

@scoringDecorator
def APA8BALL(**kwargs):
    '''1 point for the hill, 1 point for the win, bonus point for a sweep'''

    p1 = 0
    p2 = 0

    if (kwargs["team1_games"] == kwargs["team1_needed"]):
        p1 = 2
        if (kwargs["team2_games"] == 0):
            p1 = p1+1
        elif (kwargs["team2_needed"] - kwargs["team2_games"] == 1):
            p2 = 1

    else:
        p2 = 2
        if (kwargs["team1_games"] == 0):
            p2 = p2 + 1
        elif (kwargs["team1_needed"] - kwargs["team1_games"] == 1):
            p1 = 1

    return (p1,p2)

#public
Scoring = {
    "STANDARD":STANDARD,
    "APA8BALL":APA8BALL
}
from functools import wraps

def scoringDecorator(f):
    @wraps(f)
    def decorated(player1_games, player1_required, player2_games, player2_required):
        if ((player1_games < player1_required or player2_games < player2_required)
            and (player1_games == player1_required or player2_games == player2_required)):

            return f(player1_games=player1_games, player1_required=player1_required, player2_games=player2_games, player2_required=player2_required)

        else:
            raise TypeError

    return decorated


@scoringDecorator
def STANDARD(**kwargs):
    '''One point for a win'''
    if (args[player1_games] == args[player2_required]):
        return (1,0)
    else:
        return (0,1)

@scoringDecorator
def APA8BALL(**kwargs):
    '''1 point for the hill, 1 point for the win, bonus point for a sweep'''

    p1 = 0
    p2 = 0

    if (kwargs["player1_games"] == kwargs["player1_required"]):
        p1 = 2
        if (kwargs["player2_games"] == 0):
            p1 = p1+1
        elif (kwargs["player2_required"] - kwargs["player2_games"] == 1):
            p2 = 1

    else:
        p2 = 2
        if (kwargs["player1_games"] == 0):
            p2 = p2 + 1
        elif (kwargs["player1_required"] - kwargs["player1_games"] == 1):
            p1 = 1

    return (p1,p2)
#handicaping functions

def APA8BALL(players1, players2):
    '''
        player1 & player2 must be integers between 2 & 7.
        return numer of games player 1 must win
    '''

    matrix = [
        [2,2,2,2,2,2],
        [3,2,2,2,2,2],
        [4,3,3,3,3,2],
        [5,4,4,4,4,3],
        [6,5,5,5,5,4],
        [7,6,5,5,5,5],
    ]

    if (len(players1) > 0 and len(players2) > 0 and 2 <= players1[0].handicap <= 7 and 2 <= players2[0].handicap <= 7):
        return matrix[players1[0].handicap-2][players2[0].handicap-2]
    else:
        raise TypeError



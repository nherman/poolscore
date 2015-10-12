#handicaping functions

def APA8BALL(player1, player2):
    '''
        player1 & player2 must be integers between 2 & 7.
        return dict containing the number of games each player must win
    '''

    matrix = [
        [(2,2),(2,3),(2,4),(2,5),(2,6),(2,7)],
        [(3,2),(2,2),(2,3),(2,4),(2,5),(2,6)],
        [(4,2),(3,2),(3,3),(3,4),(3,5),(2,5)],
        [(5,2),(4,2),(4,3),(4,4),(4,5),(3,5)],
        [(6,2),(5,2),(5,3),(5,4),(5,5),(4,5)],
        [(7,2),(6,2),(5,2),(6,3),(5,4),(5,5)],
    ]

    if (2 <= player1 <= 7 and 2 <= player2 <= 7):
        return matrix[player1-2][player2-2]
    else:
        raise TypeError



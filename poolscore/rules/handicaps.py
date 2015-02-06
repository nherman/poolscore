#handicaping functions

def APA8BALL(player1, player2):
    '''return dict containing the number of games each player must win'''

    matrix = [
        [(2,2),(2,3),(2,4),(2,5),(2,6),(2,7)],
        [(3,2),(2,2),(2,3),(2,4),(2,5),(2,6)],
        [(4,2),(3,2),(3,3),(3,4),(3,5),(2,5)],
        [(5,2),(4,2),(4,3),(4,4),(4,5),(3,5)],
        [(6,2),(5,2),(5,3),(5,4),(5,5),(4,5)],
        [(7,2),(6,2),(5,2),(6,3),(5,4),(5,5)],
    ]

    if (player1 <= 7 and player1 >=2 and player2 <= 7 and player2 >= 2):
        return matrix[player1-2][player2-2]
    else:
        raise TypeError



__author__ = 'Shtav'
import tournamentdb


# def swissPairings():
#     """Returns a list of pairs of players for the next round of a match.
#
#     Assuming that there are an even number of players registered, each player
#     appears exactly once in the pairings.  Each player is paired with another
#     player with an equal or nearly-equal win record, that is, a player adjacent
#     to him or her in the standings.
#
#     Returns:
#       A list of tuples, each of which contains (id1, name1, id2, name2)
#         id1: the first player's unique id
#         name1: the first player's name
#         id2: the second player's unique id
#         name2: the second player's name
#     """
#     DB = tournamentdb.connect()
#     c = DB.cursor()
#     c.execute("SELECT id, name FROM players ORDER BY wins DESC")
#     #print tournamentdb.playerStandings()
#     pairs = []
#     pair = None
#     for i in c.fetchall():
#         print(i)
#         if pair:
#             pair = pair + (i[0],) + (i[1],)
#             pairs.append(pair)
#             pair = None
#         else:
#             pair = (i[0], i[1])
#     if pair:  # Is true if odd number of players
#         pair = pair + (9999,) + ('BYE',)
#         pairs.append(pair)
#     DB.commit()
#     DB.close()
#     return pairs

def remainingOpponents(p_id):
    """Returns a list opponents that player had not yet had a match with.

    The first entry in the list should be the opponent with the closest amount
    of match_points.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = tournamentdb.connect()
    c = DB.cursor()
    c.execute("DROP VIEW opponents")
    c.execute("CREATE OR REPLACE VIEW opponents "
              "AS SELECT p.id, "
              "ABS((SELECT SUM(match_outcome) FROM matches m "
              "WHERE p.id = m.player_id) - "
              "(SELECT SUM(match_outcome) FROM matches m "
              "WHERE %s = m.player_id)) AS diff "
              "FROM players p  "
              "WHERE p.id != %s AND "
              "p.id NOT IN "
              "(SELECT opponent_id FROM matches "
              "WHERE player_id = %s) "
              "GROUP BY p.id "
              "ORDER BY diff", (p_id, p_id, p_id))
    c.execute("SELECT * FROM opponents")
    #print(p_id)
    #print c.fetchall()
    # c.execute("SELECT p.id, "
    #           "(SELECT SUM(match_outcome) FROM matches m "
    #           "WHERE p.id = m.player_id) AS match_points "
    #           "FROM players p  "
    #           "WHERE p.id != %s AND "
    #           "p.id IN "
    #           "(SELECT opponent_id FROM matches "
    #           "WHERE player_id != %s) "
    #           "GROUP BY p.id "
    #           "ORDER BY diff", (p_id, p_id,))
    c.execute("SELECT (SELECT id FROM players WHERE id = %s), "
              "o.id, o.diff  FROM opponents o, players p "
              "WHERE p.id = o.id "
              "ORDER BY o.diff, p.seed_score", (p_id,))


    # c.execute("SELECT (SELECT id FROM players WHERE id = %s), p.id, "
    #           "ABS((SELECT SUM(match_outcome) FROM matches m "
    #           "WHERE p.id = m.player_id)-(SELECT SUM(match_outcome)"
    #           "FROM matches m WHERE %s = m.player_id))"
    #           "FROM players p, matches m "
    #           "WHERE p.id != %s AND "
    #           "p.id IN "
    #           "(SELECT opponent_id FROM matches "
    #           "WHERE player_id != %s) "
    #           "GROUP BY p.id ", (p_id, p_id, p_id, p_id,))
    # print c.fetchall()



    # c.execute("CREATE OR REPLACE VIEW opponents "
    #           "AS SELECT player_id, SUM(match_outcome) AS match_points "
    #           "FROM matches m "
    #           "WHERE opponent_id != %s AND player_id != %s "
    #           "GROUP BY player_id", (p_id, p_id,))
    # c.execute("SELECT * FROM opponents")
    # print(p_id)
    # print(c.fetchall())
    # c.execute("SELECT m.player_id, o.player_id, "
    #           "ABS(SUM(m.match_outcome) - o.match_points) AS diff "
    #           "FROM matches m, opponents o, players p "
    #           "WHERE m.player_id = %s AND o.player_id = p.id "
    #           "GROUP BY m.player_id, o.player_id, o.match_points, p.wins "
    #           "ORDER BY diff, p.wins", (p_id,))

    # c.execute("SELECT p.id, ABS(SUM(m.match_outcome)) "
    #           "FROM players p "
    #           "LEFT JOIN matches m  "
    #           "ON p.id = m.player_id "
    #           "GROUP BY p.id", (p_id,))
    # "WHERE m.player_id = %s "
    #           "GROUP BY m.player_id, o.player_id, o.match_points "
    #           "ORDER BY diff"

    remaining_opp = c.fetchall()
    DB.commit()
    DB.close()
    return remaining_opp


def recursivePairFinder(pairings_table, players, pairs=[]):
    copy = players
    for p_id in players:
        possible_pairs = pairings_table[p_id]  # list of possible pairs
        for x in possible_pairs:
            if len(pairs) >= len(players)/2:
                return pairs
            possible_opponent = x[1]
            if possible_opponent in players and p_id in players:
                copy.remove(possible_opponent)
                copy.remove(p_id)
                recursivePairFinder(pairings_table, copy, pairs)
                pairs.append(x)



def main():
    players = tournamentdb.playerStandings()
    pairings_table = {}
    players_by_points = [i[0] for i in players]
    for i in players_by_points:
        pairings_table[i] = remainingOpponents(i)
    pairs_list = recursivePairFinder(pairings_table, players_by_points, [])
    return pairs_list

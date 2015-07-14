__author__ = 'Shtav'
import tournamentdb


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
    c.execute("CREATE OR REPLACE VIEW opponents_%s "
              "AS SELECT player_id, SUM(match_outcome) AS match_points "
              "FROM matches m "
              "WHERE m.opponent_id != %s AND player_id != %s "
              "GROUP BY player_id", (p_id, p_id, p_id,))
    c.execute("SELECT * FROM opponents")
    print(p_id)
    print(c.fetchall())
    c.execute("SELECT m.player_id, o.player_id, "
              "ABS(SUM(m.match_outcome) - o.match_points) AS diff "
              "FROM matches m, opponents_%s o, players p "
              "WHERE m.player_id = %s AND o.player_id = p.id "
              "GROUP BY m.player_id, o.player_id, o.match_points, p.wins "
              "ORDER BY diff, p.wins", (p_id, p_id,))

    # c.execute("SELECT p.id, ABS(SUM(m.match_outcome)) "
    #           "FROM players p "
    #           "LEFT JOIN matches m  "
    #           "ON p.id = m.player_id "
    #           "GROUP BY p.id", (p_id,))
    # "WHERE m.player_id = %s "
    #           "GROUP BY m.player_id, o.player_id, o.match_points "
    #           "ORDER BY diff"

    remaining_opp = c.fetchall()
    print(remaining_opp)
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
                recursivePairFinder(pairings_table, copy)
                pairs.append(x)



def main():
    players = tournamentdb.playerStandings()
    pairings_table = {}
    players_by_points = [i[0] for i in players]
    for i in players_by_points:
        pairings_table[i] = remainingOpponents(i)
    line_up = recursivePairFinder(pairings_table, players_by_points)
    return line_up


__author__ = 'Shtav'
import tournamentdb
import copy



def remainingOpponents(t_id, p_id):
    """Returns a list opponents that player had not yet had a match with.

    The first entry in the list should be the opponent with the closest amount
    of match_points.

    Returns:
      A list of tuples, each of which contains (id, opponent_id,
      diff):
        id: the player's unique id (assigned by the database)
        opponent_id: the opponent's unique id (assigned by the database)
        diff: absolute difference in match_point totals
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
              "FROM players p, matches m "
              "WHERE p.id != %s AND p.id NOT IN "
              "(SELECT opponent_id FROM matches WHERE player_id = %s "
              "AND tourney_id = %s) "
              "GROUP BY p.id "
              "ORDER BY diff", (p_id, p_id, p_id, t_id))
    c.execute("SELECT (SELECT id FROM players WHERE id = %s), "
              "o.id, o.diff  FROM opponents o, players p "
              "WHERE p.id = o.id "
              "ORDER BY o.diff, p.seed_score", (p_id,))

    remaining_opp = c.fetchall()
    DB.commit()
    DB.close()
    return remaining_opp


def recursivePairFinder(pairings_table, players, size, pairs=[]):
    if len(pairs) < size:
        players_copy = copy.deepcopy(players)
        pairs_copy = copy.deepcopy(pairs)
        for p_id in players_copy:
            possible_pairs = pairings_table[p_id]  # list of possible pairs
            for x in possible_pairs:
                possible_opponent = x[1]
                if possible_opponent in players_copy and p_id in players_copy:
                    pairs_copy.append(x)
                    players_copy.remove(possible_opponent)
                    players_copy.remove(p_id)
                    pairs = recursivePairFinder(pairings_table,
                                        players_copy, size, pairs_copy)
                    if len(pairs) >= size:
                        break
            if len(pairs) >= size:
                break
    return pairs



def main(t_id):
    players = tournamentdb.playerStandings()
    pairings_table = {}
    players_by_points = [i[0] for i in players]
    num_of_players = len(players_by_points)/2
    for i in players_by_points:
        pairings_table[i] = remainingOpponents(t_id, i)
    pairs_list = recursivePairFinder(pairings_table,
                                     players_by_points, num_of_players, [])
    return pairs_list

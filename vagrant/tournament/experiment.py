__author__ = 'Shtav'
import tournamentdb

def create_player_pairings(player, player_remaining_opponents):
    # Create a list of possible matches for a player for the next round
    pairing_table = []
    player_opponents_constant = player_remaining_opponents[:]
    for i in player_remaining_opponents:
        player_opponents_constant.remove(i)
        pair_weight_diff = abs(i[1] - player[1])
        pair = (player, i, pair_weight_diff)
        pairing_table.append(pair)
    return sorted(pairing_table, key=lambda x: x[2])


def create_pairings_table():
    # Compile a table of all players' possible matches for the next round
    players = tournamentdb.playerStandings()
    pairings_table = {}
    players_constant = players[:]
    for i in players_constant:
        possible_opponents = remainingOpponents(i[0])
        pairings_table[i[0]] = create_player_pairings(i, possible_opponents)
    return pairings_table


def remainingOpponents(p_id):
    """Returns a list opponents that player had not yet had a match with.

    The first entry in the list should be the opp

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = tournamentdb.connect()
    c = DB.cursor()
    # c.execute("SELECT player_id, SUM(match_outcome) "
    #           "FROM matches "
    #           "WHERE player_id NOT IN "
    #           "(SELECT opponent_id FROM matches WHERE player_id = %s) "
    #           "AND player_id != %s"
    #           "GROUP BY player_id ",
    #           (p_id, p_id,))
    c.execute("SELECT player_id, opponent_id, "
              "ABS(SUM(match_outcome) - (SELECT SUM(match_outcome) FROM matches WHERE player_id = m.opponent_id GROUP BY player_id)) "
              "FROM matches m "
              "WHERE opponent_id NOT IN "
              "(SELECT opponent_id FROM matches WHERE player_id = %s) "
              "AND player_id = %s"
              "GROUP BY player_id, opponent_id ",
              (p_id, p_id))
    #c.execute("SELECT opponent_id FROM matches WHERE player_id = %s", (p_id,))
    # c.execute("SELECT player_id, "
    #           "(SELECT id FROM players WHERE id != m.player_id) AS o_id, SUM(match_outcome) "
    #           "FROM matches m "
    #           "WHERE player_id = %s "
    #           "GROUP BY player_id, o_id", (p_id,))
    c.execute("CREATE VIEW opponents "
              "AS SELECT player_id, SUM(match_outcome) AS match_points "
              "FROM matches m "
              "WHERE m.opponent_id != %s AND player_id != %s "
              "GROUP BY player_id", (p_id, p_id,))
    c.execute("SELECT m.player_id, o.player_id, "
              "ABS(SUM(m.match_outcome) - o.match_points) "
              "FROM matches m, opponents o "
              "WHERE m.player_id = %s "
              "GROUP BY m.player_id, o.player_id, o.match_points", (p_id,))
    #c.execute("SELECT id FROM players WHERE id != %s", (p_id,))
    return c.fetchall()


def recursive_pair_finder(pairings_table, players_by_point, pairs=[]):
    copy = players_by_point
    for p_id in players_by_point:
        possible_pairs = pairings_table[p_id]  # list of possible pairs
        for x in possible_pairs:
            if len(pairs) >= len(players_by_point)/2:
                return pairs
            possible_opponent = x[1][0]
            if possible_opponent in players_by_point and p_id in players_by_point:
                copy.remove(possible_opponent)
                copy.remove(p_id)
                recursive_pair_finder(pairings_table, copy)
                pairs.append(x)



def main():
    DB = tournamentdb.connect()
    c = DB.cursor()
    c.execute("SELECT p.id "
              "FROM players p "
              "ORDER BY "
              "(SELECT SUM(match_outcome) "
              "FROM matches "
              "WHERE player_id = p.id) DESC")
    pairings_table = create_pairings_table()
    players_by_points = [i[0] for i in c.fetchall()]
    line_up = recursive_pair_finder(pairings_table, players_by_points)
    print(line_up)
    DB.close()



def create_dummy_match_results():
    DB = tournamentdb.connect()
    c = DB.cursor()
    c.execute("SELECT id FROM players")
    players = c.fetchall()
    print(players)
    copy = players[:]
    pairs = []
    pair = None
    for i in players:
        if pair == None:
            pair = [i]
            copy.remove(i)
        else:
            pair.append(i)
            pairs.append(pair)
            pair = None
    print(pairs)
    for i in pairs:
        tournamentdb.reportMatch(3, i[0][0], i[1][0])

if __name__ == '__main__':
    print remainingOpponents(1)

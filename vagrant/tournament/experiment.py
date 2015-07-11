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
    DB = tournamentdb.connect()
    c = DB.cursor()
    c.execute("""
      SELECT p.id, (SELECT SUM(match_outcome) FROM matches WHERE player_id = p.id)
      FROM players p""")
    players = c.fetchall()
    pairings_table = {}
    players_constant = players[:]
    for i in players_constant:
        possible_opponents = get_remaining_opponents(i[0])
        pairings_table[i[0]] = create_player_pairings(i, possible_opponents)
    return pairings_table

# Gets opponents that the player has not yet had a match with
def get_remaining_opponents(player):
    DB = tournamentdb.connect()
    c = DB.cursor()
    c.execute("""
      SELECT p.id,
      (SELECT SUM(match_outcome) FROM matches WHERE player_id = p.id) AS points
      FROM players p
      LEFT JOIN (SELECT opponent_id FROM matches WHERE player_id = %s) m
      ON m.opponent_id = p.id
      WHERE m.opponent_id IS NULL
      AND id != %s
      ORDER BY points DESC
    """, (player, player,))
    return c.fetchall()


def recursive_pair_finder(pairings_table, players_by_point, pairs=[]):
    copy = players_by_point
    for p_id in players_by_point:
        possible_pairs = pairings_table[p_id]  # list of possible pairs
        for x in possible_pairs:
            if len(pairs) >= 7:
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
    c.execute("""SELECT p.id
      FROM players p
      ORDER BY (SELECT SUM(match_outcome)
        FROM matches
        WHERE player_id = p.id) DESC""")
    pairings_table = create_pairings_table()
    players_by_points = [i[0] for i in c.fetchall()]
    line_up = recursive_pair_finder(pairings_table, players_by_points)
    for i in line_up:
        print(i)
    print(line_up)



def create_dummy_match_results():
    DB = tournamentdb.connect()
    c = DB.cursor()
    c.execute("SELECT id FROM members")
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

create_dummy_match_results()

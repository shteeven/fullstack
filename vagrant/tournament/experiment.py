__author__ = 'Shtav'
import psycopg2
import tournamentdb


def create_card_table():
    delete_card_tables()
    DB = tournamentdb.connect()
    c = DB.cursor()
    c.execute("SELECT id FROM players")
    players = c.fetchall()
    print(players)
    for i in players:
        c.execute(
            """CREATE TABLE card_%s
            (id SERIAL PRIMARY KEY, opponent_id INTEGER)""", (i[0],))
    DB.commit()
    DB.close()


def delete_card_tables():
    DB = tournamentdb.connect()
    c = DB.cursor()
    c.execute("""
    SELECT table_schema,table_name
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name LIKE 'card_%'
    ORDER BY table_schema,table_name;
    """)
    for i in c.fetchall():
        c.execute("DROP TABLE " + (i[1]))
    print('all tables dropped')
    DB.commit()
    DB.close()


def check_tables():
    DB = tournamentdb.connect()
    c = DB.cursor()
    c.execute("""
    SELECT table_schema,table_name
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name LIKE 'card_%'
    ORDER BY table_schema,table_name;
    """)
    for i in c.fetchall():
        print(i)
    DB.close()


def sort_pairings_table_by_weight(pairings_table):
    return None


# Create a list of possible matches for a player for the next round
def create_player_pairings(player, player_remaining_opponents):
    pairing_table = []
    player_opponents_constant = player_remaining_opponents[:]
    for i in player_remaining_opponents:
        player_opponents_constant.remove(i)
        pair_weight_diff = abs(i[1] - player[1])
        pair = (player, i, pair_weight_diff)
        pairing_table.append(pair)
    return sorted(pairing_table, key=lambda x: x[2])


# Compile a table of all players' possible matches for the next round
def create_pairings_table():
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
      (SELECT SUM(match_outcome) FROM matches WHERE opponent_id = p.id) AS points
      FROM players p
      LEFT JOIN (SELECT opponent_id FROM matches WHERE player_id = %s) m
      ON m.opponent_id = p.id
      WHERE m.opponent_id IS NULL
      AND id != %s
      ORDER BY points DESC
    """, (player, player,))
    return c.fetchall()




def remove_player_pairs(pair, pairing_table):
    pairing_table_constant = pairing_table[:]
    for i in pairing_table_constant:
        if pair[0] in i or pair[1] in i:
            pairing_table.remove(i)
    return pairing_table


# function creates a match by picking pairs that are weighted most evenly and
# are not a rematch
def create_match_lineup(pairings_table, players_by_point):
    players_constant = players_by_point[:]
    num_of_player = len(players_by_point)
    count = 0
    match_lineup = []
    # because pairings are pre-sorted, and players already paired are
    # removed, the function only needs to retrieve first item everytime.
    recursive_pair_finder(pairings_table, players_by_point)

def recursive_pair_finder(pairings_table, players_by_point, pairs=[]):
    copy = players_by_point
    for p_id in players_by_point:
        possible_pairs = pairings_table[p_id]  # list of possible pairs
        for x in possible_pairs:
            possible_opponent = x[1][0]
            if possible_opponent in players_by_point and p_id in players_by_point:
                copy.remove(possible_opponent)
                copy.remove(p_id)
                recursive_pair_finder(pairings_table, copy)
                pairs.append(x)
                print(pairs)
                print(len(pairs))
            if len(pairs) >= 7:
                print(pairs)
                return pairs
        #pairs.append()
        #print(a[0])
        #pairs.append(a[0])
        #if len(pairs) == 8:
        #    break
        #recursive_pair_finder(pairings_table, copy, pairs)


def main():
    DB = tournamentdb.connect()
    c = DB.cursor()
    c.execute("""SELECT p.id
      FROM players p
      ORDER BY (SELECT SUM(match_outcome)
        FROM matches
        WHERE player_id = p.id) DESC""")
    pairings_table = create_pairings_table()
    print(pairings_table)
    players_by_points = [i[0] for i in c.fetchall()]

    print(players_by_points)
    line_up = create_match_lineup(pairings_table, players_by_points)


main()
# a = create_pairings_table()
# aList = []
# keys_list = a.keys()
# #print(keys_list)
# print(a)
'''
for i in a:
    print(a[i][0][0][0])
    for x in a[i]:
        print(x)
'''

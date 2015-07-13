__author__ = 'Shtav'



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


def remove_player_pairs(pair, pairing_table):
    pairing_table_constant = pairing_table[:]
    for i in pairing_table_constant:
        if pair[0] in i or pair[1] in i:
            pairing_table.remove(i)
    return pairing_table


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


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT * FROM players ORDER BY wins DESC")
    pairs = []
    pair = None
    a = c.fetchall()
    for i in a:
        if pair:
            pair = pair + (i[0],) + (i[1],)
            pairs.append(pair)
            pair = None
        else:
            pair = (i[0], i[1])
    if pair:  # Is true if odd number of players
        pair = pair + (9999,) + ('BYE',)
        pairs.append(pair)
    DB.close()
    return pairs
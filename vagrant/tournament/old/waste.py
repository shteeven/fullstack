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



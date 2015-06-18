#!/usr/bin/env python
#
# tournamentdb.py -- the DB implementation of a Swiss-system tournament
#

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    # For dev w/o vagrant & w/ pgAdmin III
    return psycopg2.connect(host="localhost",
                            dbname="tournament"
                            )
    # For dev w/ vagrant
    # return psycopg2.connect(dbname="tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("TRUNCATE matches")
    DB.commit()
    DB.close()



def deletePlayers():
    """Remove all the player records from the database."""
    DB = psycopg2.connect("dbname=tournament")
    c = DB.cursor()
    c.execute("TRUNCATE players")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT count(*) FROM players")
    result = c.fetchone()[0]
    DB.commit()
    DB.close()
    return result


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO players VALUES (DEFAULT, %s)", (name,))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT id, name, wins, matches FROM players ORDER BY wins DESC")
    results = []
    for i in c.fetchall():
        results.append(i)
    DB.commit()
    DB.close()
    return results

def reportMatch(winner, loser=None):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    if loser:  # Do not update record of loser if 'bye'
        c.execute("UPDATE players SET matches = matches + 1 WHERE id = %s;", (loser,))
    c.execute("UPDATE players SET wins = wins + 1, matches = matches + 1 WHERE id = %s;", (winner,))
    DB.commit()
    DB.close()


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
    for i in c.fetchall():
        if pair:
            pair = pair + (i[0],) + (i[1],)
            pairs.append(pair)
            pair = None
        else:
            pair = (i[0], i[1])
            print(pair)
    if pair:  # Is true if odd number of players
        pair = pair + (9999999999,) + ('BYE',)
        pairs.append(pair)
    DB.close()
    return pairs



def get_all_tables():
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT * FROM matches")
    for i in c.fetchall():
        print(i)
    DB.close()


def get_all_players():
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT * FROM players")
    players = ({'id': str(row[1]), 'name': str(row[0])} for row in c.fetchall())
    print("here")
    c.execute("SELECT * FROM players")
    print(c.fetchall())
    DB.close()
    return players


def get_top_5():
    DB = connect()
    c = DB.cursor()
    # Select every other player from table ordered by wins //EVENs
    c.execute("""SELECT id, name, wins FROM (
                SELECT id, name, wins, ROW_NUMBER() OVER(ORDER BY wins DESC) AS rownum FROM players
                ) t WHERE t.rownum % 2 = 0""")

    # Select every other player from table ordered by wins //ODDs
    c.execute("""SELECT id, name, wins FROM (
                SELECT id, name, wins, ROW_NUMBER() OVER(ORDER BY wins DESC) AS rownum FROM players
                ) t WHERE t.rownum % 2 = 1""")
    # players = ({'id': str(row[1]), 'name': str(row[0])} for row in c.fetchall())

    # c.execute("SELECT * FROM information_schema.columns WHERE table_name   = 'players_order'")
    players = []
    for i in c.fetchall():
        players.append(i)
    DB.close()
    return players


print(countPlayers())

# print(get_top_5())
print(swissPairings())

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
    print('truncated')
    DB.commit()
    print('truncated committed')
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


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """


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

def main():
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT * FROM matches ORDER BY match_id DESC")
    c.execute("SELECT * FROM matches ORDER BY match_id DESC")
    for i in c.fetchall():
        print('no loop')
        print i
    deleteMatches()
    print('delete matches success')
    c.execute("SELECT * FROM matches ORDER BY match_id DESC")
    print('should be nothing after this')
    for i in c.fetchall():
        print('no loop 2')
        print i
    DB.close()

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

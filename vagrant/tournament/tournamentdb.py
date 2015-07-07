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


def reportMatch(match_round, winner, loser=None, draw=None):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    if not draw:  # set records of match both in match table and player table
        c.execute("UPDATE players SET matches = (matches + 1) WHERE id = %s;", (loser,))  # update loser record
        c.execute("UPDATE players SET wins = (wins + 1), matches = (matches + 1) WHERE id = %s;", (winner,))  # update loser record
        c.execute("INSERT INTO matches (match_id, player_id, opponent_id, match_outcome) VALUES (%s, %s, %s, %s)", (match_round, winner, loser, 3))  # update winner tourney card
        c.execute("INSERT INTO matches (match_id, player_id, opponent_id, match_outcome) VALUES (%s, %s, %s, %s)", (match_round, loser, winner, 0))  # update loser tourney card
    else:  # set records with 'draw' points
        c.execute("UPDATE players SET wins = (wins + .5), matches = (matches + 1) WHERE id = %s;", (loser,))  # update player 1 record
        c.execute("UPDATE players SET wins = (wins + .5), matches = (matches + 1) WHERE id = %s;", (winner,))  # update player 2 record
        c.execute("INSERT INTO matches (match_id, player_id, opponent_id, match_outcome) VALUES (%s, %s, %s, %s)", (match_round, winner, loser, 1))  # update player 1 tourney card
        c.execute("INSERT INTO matches (match_id, player_id, opponent_id, match_outcome) VALUES (%s, %s, %s, %s)", (match_round, loser, winner, 1))  # update player 2 tourney card
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


def get_all_players():
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT id, name, wins, matches FROM players ORDER BY wins DESC")
    results = []
    for i in c.fetchall():
        results.append(i)
    DB.commit()
    DB.close()
    return results



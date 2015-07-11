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


def truncateMembers():
    """Remove all the member records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("TRUNCATE members")
    DB.commit()
    DB.close()


def truncatePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("TRUNCATE players")
    DB.commit()
    DB.close()


def truncateMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("TRUNCATE matches")
    DB.commit()
    DB.close()


def deleteMember(p_id):
    """Remove a member from the database.

    Args:
      p_id: the member's id.
    """
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM members WHERE id = %s", (p_id,))
    DB.commit()
    DB.close()


def deletePlayer(p_id):
    """Remove a player from the current tourney from the database.

    Args:
      p_id: the member's id.
    """
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM players WHERE id = %s", (p_id,))
    DB.commit()
    DB.close()


def deleteMatches(t_id, m_id):
    """Removes match records of a round from the database.

     Args:
      t_id: the tournament id.
      m_id: the match round id.
     """
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM matches "
              "WHERE tourney_id = %s AND match_id = %s", (t_id, m_id,))
    DB.commit()
    DB.close()


def countMembers():
    """Returns the number of members currently registered."""
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT count(*) FROM members")
    result = c.fetchone()[0]
    DB.commit()
    DB.close()
    return result


def countPlayers():
    """Returns the number of players currently in the tournament."""
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT count(*) FROM players")
    result = c.fetchone()[0]
    DB.commit()
    DB.close()
    return result


def registerMember(name):
    """Adds a member to the database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO members "
              "VALUES (DEFAULT, %s)", (name,))
    DB.commit()
    DB.close()


def addMemberToPlayers(p_id):
    """Adds a player, or list of players, to the current tournament database.

    Args:
      p_id: the player's member id or list of member ids.
    """
    DB = connect()
    c = DB.cursor()
    if type(p_id) == list:
        for i in p_id:
            c.execute("INSERT INTO players (id, seed_rank) "
                      "SELECT id, COALESCE(wins / NULLIF(matches,0), 0) "
                      "FROM members "
                      "WHERE id = %s", (i,))
    else:
        c.execute("INSERT INTO players (id, seed_rank) "
                  "SELECT id, COALESCE(wins / NULLIF(matches,0), 0) "
                  "FROM members "
                  "WHERE id = %s", (p_id,))
    DB.commit()
    DB.close()


def memberRankings():
    """Returns a list of the members and their win record, sorted
    by percentage of wins to matches.

    The first entry in the list should be the player in first place, or tied
    for first.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT id, name, wins, matches,"
              "COALESCE(wins / NULLIF(matches,0), 0) AS seed_score "
              "FROM members "
              "ORDER BY seed_score DESC")
    results = []
    for i in c.fetchall():
        results.append(i)
    DB.commit()
    DB.close()
    return results


def playerRankings():
    """Returns a list of the players and their and their seed score, sorted
    by percentage of wins to matches.

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
    c.execute("SELECT id, seed_score "
              "FROM players "
              "ORDER BY seed_score DESC")
    results = []
    for i in c.fetchall():
        results.append(i)
    DB.commit()
    DB.close()
    return results


def playerStandings():
    """Returns a list of the players and their and their seed score, sorted
    by percentage of wins to matches.

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
    c.execute("SELECT player_id, SUM(match_outcome) AS match_points "
              "FROM matches GROUP BY player_id "
              "ORDER BY match_points DESC")
    results = []
    for i in c.fetchall():
        results.append(i)
    DB.commit()
    DB.close()
    return results


def reportMatch(tourney_id, match_round, winner, loser, draw=None):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    if not draw:  # set records of match both in match table and player table
        # update loser record
        c.execute("UPDATE members "
                  "SET matches = (matches + 1) "
                  "WHERE id = %s;", (loser,))
        # update loser record
        c.execute("UPDATE members "
                  "SET wins = (wins + 1), matches = (matches + 1) "
                  "WHERE id = %s;", (winner,))
        # update winner tourney card
        c.execute("INSERT INTO matches (tourney_id, match_id, player_id, "
                  "opponent_id, match_outcome) "
                  "VALUES (%s ,%s, %s, %s, %s)",
                  (tourney_id, match_round, winner, loser, 3))
        # update loser tourney card
        c.execute("INSERT INTO matches (tourney_id, match_id, player_id, "
                  "opponent_id, match_outcome) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (tourney_id, match_round, loser, winner, 0))
    else:  # set records with 'draw' points
        # update player 1 record
        c.execute("UPDATE members "
                  "SET wins = (wins + .5), matches = (matches + 1) "
                  "WHERE id = %s;", (loser,))
        # update player 2 record
        c.execute("UPDATE members "
                  "SET wins = (wins + .5), matches = (matches + 1) "
                  "WHERE id = %s;", (winner,))
        # update player 1 tourney card
        c.execute("INSERT INTO matches (tourney_id, match_id, player_id, "
                  "opponent_id, match_outcome) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (tourney_id, match_round, winner, loser, 1))
        # update player 2 tourney card
        c.execute("INSERT INTO matches (tourney_id,match_id, player_id, "
                  "opponent_id, match_outcome) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (tourney_id, match_round, loser, winner, 1))
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


print(playerStandings())
#!/usr/bin/env python
#
# tournamentdb.py -- the db implementation of a Swiss-system tournament
#

import psycopg2
import copy

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
    db = connect()
    c = db.cursor()
    c.execute("TRUNCATE members")
    db.commit()
    db.close()


def truncatePlayers():
    """Remove all the player records from the players table."""
    db = connect()
    c = db.cursor()
    c.execute("TRUNCATE players")
    db.commit()
    db.close()


def truncateMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("TRUNCATE matches")
    db.commit()
    db.close()


def truncateAll():
    """Truncate all tables in database; matches, members, and players."""
    truncateMatches()
    truncatePlayers()
    truncateMembers()


def deleteMember(p_id):
    """Remove a member from the database.

    Args:
      p_id: the member's id.
    """
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM members WHERE id = %s", (p_id,))
    db.commit()
    db.close()


def deletePlayer(p_id):
    """Remove a player in the current tourney from the database.

    Args:
      p_id: the player's id.
    """
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM players WHERE id = %s", (p_id,))
    db.commit()
    db.close()


def deleteMatches(t_id, m_id):
    """Removes match records of a round from the database.

     Args:
      t_id: the tournament id.
      m_id: the match round id.
     """
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM matches "
              "WHERE tourney_id = %s AND match_id = %s", (t_id, m_id,))
    db.commit()
    db.close()


def deleteTourney(t_id):
    """Removes a tournament's records from the database.

     Args:
      t_id: the tournament id.
    """
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM matches "
              "WHERE tourney_id = %s", (t_id,))
    db.commit()
    db.close()


def countMembers():
    """Returns the number of members currently registered."""
    db = connect()
    c = db.cursor()
    c.execute("SELECT count(*) FROM members")
    result = c.fetchone()[0]
    db.commit()
    db.close()
    return result


def countPlayers():
    """Returns the number of players currently in the tournament."""
    db = connect()
    c = db.cursor()
    c.execute("SELECT count(*) FROM players")
    result = c.fetchone()[0]
    db.commit()
    db.close()
    return result


def registerMember(name):
    """Adds a member to the database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).

    Returns: new member's assigned id (important for testing)
    """
    db = connect()
    c = db.cursor()
    c.execute("INSERT INTO members "
              "VALUES (DEFAULT, %s)", (name,))
    c.execute("SELECT id FROM members WHERE name = %s", (name,))
    new_id = c.fetchall()
    db.commit()
    db.close()
    return new_id[0][0]


def registerPlayer(p_id):
    """Adds a player, or list of players, to the current tournament database.

    Args:
      p_id: the player's member id or list of member ids.
    """
    db = connect()
    c = db.cursor()
    c.execute("INSERT INTO players (id, name, seed_score) "
              "SELECT id, name, "
              "COALESCE(wins / NULLIF(matches,0), 0) "
              "FROM members "
              "WHERE id = %s", (p_id,))
    db.commit()
    db.close()


def membersBySeeding():
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
    db = connect()
    c = db.cursor()
    c.execute("SELECT id, name, wins, matches,"
              "COALESCE(wins / NULLIF(matches,0), 0) AS seed_score "
              "FROM members "
              "ORDER BY seed_score DESC")
    results = c.fetchall()
    db.commit()
    db.close()
    return results


def membersByWins():
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
    db = connect()
    c = db.cursor()
    c.execute("SELECT id, name, wins, matches "
              "FROM members "
              "ORDER BY wins DESC")
    results = c.fetchall()
    db.commit()
    db.close()
    return results


def playerSeedings():
    """Returns a list of the players and their and their seed score, sorted
    by percentage of wins to matches.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, seed_score):
        id: the player's unique id (assigned by the database)
        seed_score: the players' wins divided by total number of matches played
    """
    db = connect()
    c = db.cursor()
    c.execute("SELECT id, seed_score "
              "FROM players "
              "ORDER BY seed_score DESC")
    results = c.fetchall()
    db.commit()
    db.close()
    return results


def playersByWins():
    """Returns a list of the players and their record, sorted by wins.

    The first entry in the list should be the player in first place, or tied
    for first.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    c.execute("SELECT id, name, wins, matches "
              "FROM players "
              "ORDER BY wins DESC")
    results = c.fetchall()
    db.commit()
    db.close()
    return results


def playerStandings(t_id):
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
    db = connect()
    c = db.cursor()
    c.execute("SELECT p.id, "
              "COALESCE("
              "(SELECT SUM(match_outcome) "
              "FROM matches "
              "WHERE tourney_id = %s AND player_id = p.id), 0) AS match_points "
              "FROM players p "
              "GROUP BY p.id "
              "ORDER BY match_points, p.wins DESC", (t_id,))
    results = c.fetchall()
    db.commit()
    db.close()
    return results


def reportMatch(t_id, m_id, win_id, lose_id, draw=None):
    """Records the outcome of a single match between two players.

    Args:
      win_id:  the id number of the player who won
      lose_id:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()
    # set records with 'draw' points
    if draw is True:
        # update player 1 record
        c.execute("UPDATE players "
                  "SET wins = (wins + .5), matches = (matches + 1) "
                  "WHERE id = %s;", (lose_id,))
        # update player 2 record
        c.execute("UPDATE players "
                  "SET wins = (wins + .5), matches = (matches + 1) "
                  "WHERE id = %s;", (win_id,))
        # update player 1 tourney card
        c.execute("INSERT INTO matches (tourney_id, match_id, player_id, "
                  "opponent_id, match_outcome) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (t_id, m_id, win_id, lose_id, 1))
        # update player 2 tourney card
        c.execute("INSERT INTO matches (tourney_id,match_id, player_id, "
                  "opponent_id, match_outcome) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (t_id, m_id, lose_id, win_id, 1))
    # set records of match both in match table and player table
    elif draw is None or draw is False:
        # update lose_id record
        c.execute("UPDATE players "
                  "SET matches = (matches + 1) "
                  "WHERE id = %s;", (lose_id,))
        # update lose_id record
        c.execute("UPDATE players "
                  "SET wins = (wins + 1), matches = (matches + 1) "
                  "WHERE id = %s;", (win_id,))
        # update win_id tourney card
        c.execute("INSERT INTO matches (tourney_id, match_id, player_id, "
                  "opponent_id, match_outcome) "
                  "VALUES (%s ,%s, %s, %s, %s)",
                  (t_id, m_id, win_id, lose_id, 3))
        # update lose_id tourney card
        c.execute("INSERT INTO matches (tourney_id, match_id, player_id, "
                  "opponent_id, match_outcome) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (t_id, m_id, lose_id, win_id, 0))
    else:
        raise TypeError("Draw argument can only be True or None.")

    db.commit()
    db.close()


def playerRanks(t_id):
    db = connect()
    c = db.cursor()
    #c.execute("DROP VIEW omw")
    c.execute("CREATE OR REPLACE VIEW omw "
              "AS SELECT m.player_id, "
              "SUM(m.match_outcome) AS match_points "
              "FROM matches m, players p "
              "WHERE m.player_id = p.id AND tourney_id = %s "
              "GROUP BY m.player_id, p.name "
              "ORDER BY match_points DESC ", (t_id,))
    c.execute("SELECT o.player_id, p.name, o.match_points, "
              "(SELECT SUM(o.match_points) FROM omw o "
              "LEFT JOIN matches m "
              "ON o.player_id=m.player_id "
              "WHERE m.opponent_id = p.id AND m.tourney_id = %s) AS omw_score "
              "FROM players p "
              "LEFT JOIN omw o "
              "ON p.id=o.player_id "
              "ORDER BY o.match_points DESC, omw_score DESC, p.seed_score DESC",
              (t_id,))
    ranks = c.fetchall()
    db.commit()
    db.close()
    return ranks


def endTournament():
    db = connect()
    c = db.cursor()
    c.execute("UPDATE members m "
              "SET wins = p.wins + m.wins, matches = p.matches + m.matches "
              "FROM players p "
              "WHERE m.id = p.id"
              )
    db.commit()
    db.close()
    truncatePlayers()
    print("EoT. Members' records updated and players table cleared.")


def swissPairings(t_id):
    db = connect()
    c = db.cursor()
    c.execute("SELECT * FROM matches WHERE tourney_id = %s", (t_id,))
    in_progress = c.fetchone()
    db.commit()
    db.close()
    if in_progress == None:
        pairs_list = initialPairing(t_id)
    else:
        pairs_list = subsequentPairings(t_id)
    return pairs_list


def subsequentPairings(t_id):
    players = playerStandings(t_id)
    pairings_table = {}
    players_by_points = [i[0] for i in players]
    num_of_players = countPlayers()/2
    for i in players_by_points:
        pairings_table[i] = remainingOpponents(t_id, i)
    pairs_list = recursivePairFinder(pairings_table,
                                     players_by_points, num_of_players, [])
    return pairs_list


def initialPairing(t_id):
    pair_count = countPlayers() / 2
    players_list = [row[0] for row in playerStandings(t_id)]
    pairs = []
    for i in range(pair_count):
        pairs.append((players_list[i], players_list[i + pair_count], 0))
    return pairs


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
    db = connect()
    c = db.cursor()
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
    db.commit()
    db.close()
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


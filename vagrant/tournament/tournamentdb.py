#!/usr/bin/env python
#
# tournamentdb.py -- the db implementation of a Swiss-system tournament
#

import psycopg2
import copy

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect(host="localhost",
                            dbname="tournament", user="postgres")

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
      p_id: the player's member id.
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
    """Returns a list of the members and sorted by their win record.

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
    """Returns a list of the players and their match points.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Arg:
      t_id: tournament id.

    Returns:
      A list of tuples, each of which contains (id, match_points):
        id: the player's unique id
        matches: the total match points the player has won thus far
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
              "ORDER BY match_points, p.seed_score DESC", (t_id,))
    results = c.fetchall()
    db.commit()
    db.close()
    return results


def reportMatch(t_id, m_id, win_id, lose_id, draw=False):
    """Records the outcome of a single match between two players to the
    players' table only; not the members' table.

    Args:
      t_id: tournament id.
      m_id: match (round) id.
      win_id: the id number of the player who won.
      lose_id: the id number of the player who lost.
      draw: draw if True; can accept False (optional)
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
    elif draw is False:
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
        raise TypeError("Draw argument can only be True or False.")
    db.commit()
    db.close()


def playerRanks(t_id):
    """Returns the players' ranks in order of match points. In the case of ties,
      players are sub-sorted by opponent match wins, then seed_score.

    Args:
      t_id: tournament id.

    Returns:
      A list of tuples, each of which contains (id, name, match_points, omw):
        id: the player's unique id.
        name: the name of player.
        match_points: the player's match point total for tournament
        omw: the opponent match wins for tournament
    """
    db = connect()
    c = db.cursor()
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
    """To be ran at the end of each tournament. This function updates member
    data with data from players table, and then truncates the players table.
    """
    db = connect()
    c = db.cursor()
    c.execute("UPDATE members m "
              "SET wins = p.wins + m.wins, matches = p.matches + m.matches "
              "FROM players p "
              "WHERE m.id = p.id")
    db.commit()
    db.close()
    truncatePlayers()
    print("EoT. Members' records updated and players table cleared.")


def swissPairings(t_id):
    """Returns a list of pairs of players for the next round of a match.
    This function pools other functions to create pairs that provide the
    tournament with results that are more aligned with the players
    abilities and expected outcomes.
    It also ensures that no player plays another twice, can run with
    odd number of players, and no player gets more than one bye. This
    program works as long as the number of rounds is roughly log2 n;
    n being the number of players. Can work with more.

    Args:
      t_id: the tournament id.

    Returns:
      A list of tuples, each of which contains (id1, id2, diff)
        id1: the first player's unique id
        id2: the second player's unique id
        diff: the absolute difference in players' match points
    """
    db = connect()
    c = db.cursor()
    c.execute("SELECT * "
              "FROM matches "
              "WHERE tourney_id = %s", (t_id,))
    in_progress = c.fetchone()
    db.commit()
    db.close()
    num_of_players = countPlayers()
    if in_progress == None:
        if num_of_players % 2 != 0:
            db = connect()
            c = db.cursor()
            c.execute("INSERT INTO players (id, name, seed_score) "
                      "VALUES (2147483647, 'BYE', 0)")
            db.commit()
            db.close()
        num_of_players = countPlayers()
        pairs_list = initialPairing(num_of_players, t_id)
    else:
        pairs_list = subsequentPairings(num_of_players, t_id)
    if len(pairs_list) == (num_of_players / 2):
        return pairs_list
    else:
        raise ValueError("swissPairings is not returning the expected number "
                         "of pairs. This is most likely due to the number of"
                         "rounds for this style of tournament being exceeded.")


def initialPairing(num_of_players, t_id):
    """This is the initial pairing function. It pairs players based on seeding,
    allowing players to be better placed in the pool for situations where a tie
    may arise, as well as avoid high-performing, evenly-matched players from
    being matched in the first round.
    Returns a list of pairs of players for the initial round of a tourney.

    Args:
      t_id: the tournament id.

    Returns:
      A list of tuples, each of which contains (id1, id2, diff)
        id1: the first player's unique id
        id2: the second player's unique id
        diff: the absolute difference in players' match points
    """
    pair_count = num_of_players / 2
    players_list = [row[0] for row in playerStandings(t_id)]
    pairs = []
    for i in range(pair_count):
        pairs.append((players_list[i], players_list[i + pair_count], 0))
    return pairs


def subsequentPairings(num_of_players, t_id):
    """This is a function that follows the initial pairing function. If there
    are no records for this tourney in the matches table, it will fail to run.
    Returns a list of pairs of players for the next round of a tourney. Relies
    on recursivePairFinder() to find the best pairing combination.

    Args:
      t_id: the tournament id.

    Returns:
      A list of tuples, each of which contains (id1, id2, diff)
        id1: the first player's unique id
        id2: the second player's unique id
        diff: the absolute difference in players' match points
    """
    players = playerStandings(t_id)
    players_by_points = [i[0] for i in players]
    pairs_list = recursivePairFinder(
        t_id, players_by_points, num_of_players)
    return pairs_list


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


def recursivePairFinder(t_id, players, size):
    """Returns a list with the best combination of pairings. It tries to
    match the players with the same match points, if more than one option is
    available, it will try to pair the player with the lowest ranked player of
    that pool.

    Args:
      pairings_table: a dict with keys: players' ids and values: list of
                      remaining possible opponent for that player.
      players: list of players not yet paired, decreasing as recursion deepens.
      size: the size of the expected pairs list to be returned.
      pairs: pairs is passed down each recurrence and added to.

    Returns:
      A list of tuples, each of which contains (id1, id2, diff)
        id1: the first player's unique id
        id2: the second player's unique id
        diff: the absolute difference in players' match points
    """
    pairs = []
    try:
        players_copy
    except NameError:
        players_copy = copy.deepcopy(players)
    for i in players:
        opponents = remainingOpponents(t_id, i)
        for x in opponents:
            opponent = x[1]
            if opponent in players_copy and i in players_copy:
                players_copy_copy = copy.deepcopy(players_copy)
                players_copy.remove(i)
                players_copy.remove(opponent)
                if players_copy == []:
                    pairs.append(x)
                    break
                else:
                    pairs = recursivePairFinder(t_id,
                                                 players_copy, size)
                if pairs is not False and pairs != []:
                    pairs.append(x)
                    break
                elif pairs == False:
                    players_copy = players_copy_copy
        if pairs is not False and pairs != []:
            break
    if pairs == []:
        return False
    else:
        return pairs



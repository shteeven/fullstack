#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import copy

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    # For development with EDB/pgAdmin setup
    return psycopg2.connect(host="localhost", dbname="tournament",
                            user="postgres")
    #return psycopg2.connect(dbname="tournament")


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
    db = connect()
    c = db.cursor()
    c.execute("TRUNCATE matches, members, players")
    db.commit()
    db.close()


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
      A list of tuples, each of which contains (id, wins):
        id: the player's unique id
        wins: the total wins of player thus far in current tourney
    """
    db = connect()
    c = db.cursor()
    c.execute("SELECT p.id, p.wins "
              "FROM players p "
              "GROUP BY p.id "
              "ORDER BY p.wins DESC, p.seed_score DESC", (t_id,))
    results = c.fetchall()
    db.commit()
    db.close()
    return results


def playerRanks(t_id):
    """Returns the players' ranks in order of match points. In the case of ties,
      players are sub-sorted by opponent match wins, then seed_score.

    Args:
      t_id: tournament id.

    Returns:
      A list of tuples, each of which contains (id, name, wins, omw):
        id: the player's unique id.
        name: the name of player.
        wins: the player's win total for tournament
        omw: the opponent match wins for tournament
    """
    db = connect()
    c = db.cursor()
    c.execute("SELECT p.id, p.name, p.wins, "
              "(SELECT SUM(o.wins) FROM players o "
              "LEFT JOIN matches m "
              "ON o.id=m.player_id "
              "WHERE m.opponent_id = p.id AND m.tourney_id = %s) "
              "AS omw_score "
              "FROM players p "
              "ORDER BY p.wins DESC, omw_score DESC, p.seed_score DESC",
              (t_id,))
    ranks = c.fetchall()
    db.commit()
    db.close()
    return ranks


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
                  (t_id, m_id, win_id, lose_id, .5))
        # update player 2 tourney card
        c.execute("INSERT INTO matches (tourney_id,match_id, player_id, "
                  "opponent_id, match_outcome) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (t_id, m_id, lose_id, win_id, .5))
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
                  (t_id, m_id, win_id, lose_id, 1))
        # update lose_id tourney card
        c.execute("INSERT INTO matches (tourney_id, match_id, player_id, "
                  "opponent_id, match_outcome) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (t_id, m_id, lose_id, win_id, 0))
    else:
        raise TypeError("Draw argument can only be True or False.")
    db.commit()
    db.close()


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
        # initial pairings
        if num_of_players % 2 != 0:
            db = connect()
            c = db.cursor()
            c.execute("INSERT INTO players (id, name, seed_score) "
                      "VALUES (2147483647, 'BYE', 0)")
            db.commit()
            db.close()
        num_of_players = countPlayers()
        players = [row[0] for row in playerStandings(t_id)]
        pairs_list = []
        for i in range(num_of_players / 2):
            pairs_list.append((players[i], players[i + num_of_players / 2], 0))
    else:
        # subsequent pairing
        players = [row[0] for row in playerStandings(t_id)]
        pairs_list = recursivePairFinder(t_id, players, num_of_players)
    if len(pairs_list) == (num_of_players / 2):
        return pairs_list
    else:
        raise ValueError("swissPairings is not returning the expected number "
                         "of pairs. This is most likely due to the number of"
                         "rounds for this style of tournament being exceeded.")


def remainingOpponents(t_id, p_id):
    """Returns a list opponents that player had not yet had a match with.

    The first entry in the list should be the opponent with the closest amount
    of wins.

    Returns:
      A list of tuples, each of which contains (id, opponent_id,
      diff):
        id: the player's unique id (assigned by the database)
        opponent_id: the opponent's unique id (assigned by the database)
        diff: absolute difference in win totals
    """
    db = connect()
    c = db.cursor()
    c.execute("SELECT p.id, o.id, ABS(p.wins - o.wins) AS diff "
              "FROM players p, players o "
              "WHERE p.id = %s AND o.id != p.id AND o.id NOT IN "
              "(SELECT opponent_id "
              "FROM matches "
              "WHERE player_id=p.id AND tourney_id=%s) "
              "ORDER BY diff, o.seed_score", (p_id, t_id))
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
                # Keep a copy of players_copy in case of no pair found
                players_copy_copy = copy.deepcopy(players_copy)
                players_copy.remove(i)
                players_copy.remove(opponent)
                if players_copy == []:
                    # all players matched; begin build of pairs list
                    pairs.append(x)
                    break
                else:
                    pairs = recursivePairFinder(t_id,
                                                 players_copy, size)
                if pairs is not False and pairs != []:
                    pairs.append(x)
                    break
                elif pairs == False:
                    # return the original list of players before the removal
                    players_copy = players_copy_copy
        if pairs is not False and pairs != []:
            break
    if pairs == []:
        return False
    else:
        return pairs
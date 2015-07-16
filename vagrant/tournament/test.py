#!/usr/bin/env python
#
# Test cases for tournament.py

from tournamentdb import *
import sys
import math


def testRegisterMember():
    member_count = countMembers()
    new_id = registerMember('steven')
    print(new_id)
    if member_count == countMembers():
        raise ValueError("Member count should be plus one of previous count")
    elif countMembers() == member_count + 1:
        func_name = sys._getframe().f_code.co_name
        print(func_name + " passed!")
    return new_id


def testDeleteMembers():
    member_count = countMembers()
    new_id = testRegisterMember()
    deleteMember(new_id)
    if member_count != countMembers():
        raise ValueError(
            "Member count should be identical to previous member count")
    elif countMembers() == member_count:
        func_name = sys._getframe().f_code.co_name
        print(func_name + " passed!")


def testAddPlayers():
    player_count = countPlayers()
    new_id = testRegisterMember()
    registerPlayer(new_id)
    if countPlayers() == player_count:
        raise ValueError("Player count should be plus one of previous count")
    elif countPlayers() == player_count + 1:
        func_name = sys._getframe().f_code.co_name
        print(func_name + " passed!")


def testDeletePlayers():
    new_id = testAddPlayers()
    player_count = countPlayers()
    print(player_count)
    deletePlayer(new_id)
    print(countPlayers())
    if countPlayers() == player_count:
        raise ValueError("Player count should be minus one of previous count")
    elif countPlayers() == player_count - 1:
        func_name = sys._getframe().f_code.co_name
        print(func_name + " passed!")


def testMemberStandingsBeforeMatches():
    new_id1 = registerMember("Melpomene Murray")
    new_id2 = registerMember("Randy Schwartz")
    registerPlayer(new_id1)
    registerPlayer(new_id2)
    standings = membersByWins()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    func_name = sys._getframe().f_code.co_name
    print(func_name + " passed!")


def testReportMatch():
    """
    First half tests the match point reporting.
    Second half wins and match reporting.
    """
    new_id1 = registerMember('Abdul')
    new_id2 = registerMember('Doah')
    registerPlayer(new_id2)
    registerPlayer(new_id1)
    reportMatch(123, 1, new_id1, new_id2, draw=True)
    for i in playerStandings():
        if i[1] != 1:
            raise ValueError("Players with draws should have match points of 1")
    reportMatch(123, 2, new_id1, new_id2, draw=False)
    for i in playerStandings():
        if i[0] == new_id1:
            if i[1] != 4:
                raise ValueError("Winner should have 3 match points, plus 1 for"
                                 "draw: total 4")
        if i[0] == new_id2:
            if i[1] != 1:
                raise ValueError("Loser should have 1 match point, 1 for draw"
                                 "in round 1")

    truncateAll()
    players = [registerMember("Bruno Walton"), registerMember("Boots O'Neal"),
               registerMember("Cathy Burton"), registerMember("Diane Grant")]
    for i in players:
        registerPlayer(i)
    standings = playersByWins()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(123, 1, id1, id2)
    reportMatch(123, 1, id3, id4)
    standings = playersByWins()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    endTournament()
    func_name = sys._getframe().f_code.co_name
    print(func_name + " passed!")


def createTestCase():
    """
    Create mock records. Create mock tourney with rounds. Modify algorithm
    to have players face opponents within their own brackets of each round,
    but with opponents opposite ends of that bracket, thereby saving the
    most even matches for last.
    """
    truncateAll()
    players = [registerMember("A"), registerMember("B"),
               registerMember("C"), registerMember("D"),]
               # registerMember("E"), registerMember("F"),
               # registerMember("G"), registerMember("H"),
               # registerMember("I"), registerMember("J"),
               # registerMember("K"), registerMember("L"),
               # registerMember("M"), registerMember("N"),
               # registerMember("O"), registerMember("P"),
               # registerMember("Q"), registerMember("R")]
    db = connect()
    c = db.cursor()
    x = countMembers()
    y = countMembers()
    for i in players:
        x -= 1
        c.execute("UPDATE members "
                  "SET wins = %s, matches = %s "
                  "WHERE id = %s;", (x, y, i,))
    db.commit()
    db.close()


def runTestCase(is_new=False):
    """
    Create mock records. Create mock tourney with rounds. Modify algorithm
    to have players face opponents within their own brackets of each round,
    but with opponents opposite ends of that bracket, thereby saving the
    most even matches for last.
    """
    if is_new == True:
        createTestCase()
        tourney = 1
    else:
        truncatePlayers()
        db = connect()
        c = db.cursor()
        c.execute("SELECT tourney_id "
                  "FROM matches "
                  "GROUP BY tourney_id "
                  "ORDER BY tourney_id DESC")
        tourney = (c.fetchone())[0] + 1
        db.commit()
        db.close()
    #Start fake tourney here.

    seedings = membersBySeeding()
    players = [row[0] for row in seedings]
    for i in players:
        registerPlayer(i)
    standings = playerStandings(tourney)

    # TEMPLATE FOR FIRST ROUND PAIRINGS
    players_list = [row[0] for row in standings]
    numOfPlayers = len(players_list)
    count = 0

    for i in range(int(math.ceil(math.log(numOfPlayers, 2)))):
        count += 1
        print("round " + str(count))
        current_round = i + 2
        line_up = swissPairings(tourney)
        for x in line_up:
            if x[0] < x[1]:
                reportMatch(tourney, current_round, x[0], x[1])
            elif x[1] < x[0]:
                reportMatch(tourney, current_round, x[1], x[0])

    print("final scores")
    print(playerStandings(tourney))
    print("They rank :")
    rank = 1
    rankings = playerRanks(tourney)
    print(rankings)
    for i in rankings:
        print(str(rank) + ". " + i[1] + " --ID: " + str(i[0]))
        rank += 1
    endTournament()

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

if __name__ == '__main__':
    truncateAll()
    runTestCase(True)
    runTestCase()
    #endTournament()
    print "Success!  All tests pass!"
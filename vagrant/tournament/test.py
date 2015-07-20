#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *
import sys
import math


def testRegisterMember():
    member_count = countMembers()
    new_id = registerMember('steven')
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
    return new_id


def testDeletePlayers():
    new_id = testAddPlayers()
    player_count = countPlayers()
    deletePlayer(new_id)
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
    standings = playerStandings(1)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    [(id1, wins1), (id2, wins2)] = standings
    if wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
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
    for i in playerStandings(123):
        print(i)
        if i[1] != .5:
            raise ValueError("Player with draws should have match points of .5")
    reportMatch(123, 2, new_id1, new_id2, draw=False)
    for i in playerStandings(123):
        if i[0] == new_id1:
            if i[1] != 1.5:
                raise ValueError("Winner should have 3 match points, plus 1 for"
                                 "draw: total 4")
        if i[0] == new_id2:
            if i[1] != .5:
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
    standings = playerStandings(123)
    for (i, w) in standings:
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    endTournament()
    func_name = sys._getframe().f_code.co_name
    print(func_name + " passed!")


def createTestSet():
    """
    Create mock records. Create mock tourney with rounds. Modify algorithm
    to have players face opponents within their own brackets of each round,
    but with opponents opposite ends of that bracket, thereby saving the
    most even matches for last.
    """
    truncateAll()
    players = [registerMember("A"), registerMember("B"),
               registerMember("C"), registerMember("D"),
               registerMember("E"), registerMember("F"),
               registerMember("G"), registerMember("H"),
               registerMember("I"), registerMember("J"),
               registerMember("K"), registerMember("L"),
               registerMember("M"), registerMember("N"),
               registerMember("O"), registerMember("P"),
               registerMember("Q"), registerMember("R"),
               registerMember("A"), registerMember("B"),
               registerMember("C"), registerMember("D"),
               registerMember("E"), registerMember("F"),
               registerMember("G"), registerMember("H"),
               registerMember("I"), registerMember("J"),
               registerMember("K"), registerMember("L"),
               registerMember("M"), registerMember("N"),
               registerMember("O"), registerMember("P"),
               registerMember("Q"), registerMember("R"),]  # 36
               # registerMember("A"), registerMember("B"),
               # registerMember("C"), registerMember("D"),
               # registerMember("E"), registerMember("F"),
               # registerMember("G"), registerMember("H"),
               # registerMember("I"), registerMember("J"),
               # registerMember("K"), registerMember("L"),
               # registerMember("M"), registerMember("N"),
               # registerMember("O"), registerMember("P"),
               # registerMember("Q"), registerMember("R"),
               # registerMember("A"), registerMember("B"),
               # registerMember("C"), registerMember("D"),
               # registerMember("E"), registerMember("F"),
               # registerMember("G"), registerMember("H"),
               # registerMember("I"), registerMember("J"),
               # registerMember("K"), registerMember("L"),
               # registerMember("M"), registerMember("N"),
               # registerMember("O"), registerMember("P"),
               # registerMember("Q"), registerMember("R"),  # 72
               # registerMember("A"), registerMember("B"),
               # registerMember("C"), registerMember("D"),
               # registerMember("E"), registerMember("F"),
               # registerMember("G"), registerMember("H"),
               # registerMember("I"), registerMember("J"),
               # registerMember("K"), registerMember("L"),
               # registerMember("M"), registerMember("N"),
               # registerMember("O"), registerMember("P"),
               # registerMember("Q"), registerMember("R"),
               # registerMember("A"), registerMember("B"),
               # registerMember("C"), registerMember("D"),
               # registerMember("E"), registerMember("F"),
               # registerMember("G"), registerMember("H"),
               # registerMember("I"), registerMember("J"),
               # registerMember("K"), registerMember("L"),
               # registerMember("M"), registerMember("N"),
               # registerMember("O"), registerMember("P"),
               # registerMember("Q"), registerMember("R"),
               # registerMember("A"), registerMember("B"),
               # registerMember("C"), registerMember("D"),
               # registerMember("E"), registerMember("F"),
               # registerMember("G"), registerMember("H"),
               # registerMember("I"), registerMember("J"),
               # registerMember("K"), registerMember("L"),
               # registerMember("M"), registerMember("N"),
               # registerMember("O"), registerMember("P"),
               # registerMember("Q"), registerMember("R"),
               # registerMember("A"), registerMember("B"),
               # registerMember("C"), registerMember("D"),
               # registerMember("E"), registerMember("F"),
               # registerMember("G"), registerMember("H"),
               # registerMember("I"), registerMember("J"),
               # registerMember("K"), registerMember("L"),
               # registerMember("M"), registerMember("N"),
               # registerMember("O"), registerMember("P"),
               # registerMember("Q"), registerMember("R")]
    # players2 = [registerMember("A"), registerMember("B"),
    #            registerMember("C"), registerMember("D"),
    #            registerMember("E"), registerMember("F"),
    #            registerMember("G"), registerMember("H"),
    #            registerMember("I"), registerMember("J"),
    #            registerMember("K"), registerMember("L"),
    #            registerMember("M"), registerMember("N"),
    #            registerMember("O"), registerMember("P"),
    #            registerMember("Q"), registerMember("R"),
    #            registerMember("A"), registerMember("B"),
    #            registerMember("C"), registerMember("D"),
    #            registerMember("E"), registerMember("F"),
    #            registerMember("G"), registerMember("H"),
    #            registerMember("I"), registerMember("J"),
    #            registerMember("K"), registerMember("L"),
    #            registerMember("M"), registerMember("N"),
    #            registerMember("O"), registerMember("P"),
    #            registerMember("Q"), registerMember("R"),
    #            registerMember("A"), registerMember("B"),
    #            registerMember("C"), registerMember("D"),
    #            registerMember("E"), registerMember("F"),
    #            registerMember("G"), registerMember("H"),
    #            registerMember("I"), registerMember("J"),
    #            registerMember("K"), registerMember("L"),
    #            registerMember("M"), registerMember("N"),
    #            registerMember("O"), registerMember("P"),
    #            registerMember("Q"), registerMember("R"),
    #            registerMember("A"), registerMember("B"),
    #            registerMember("C"), registerMember("D"),
    #            registerMember("E"), registerMember("F"),
    #            registerMember("G"), registerMember("H"),
    #            registerMember("I"), registerMember("J"),
    #            registerMember("K"), registerMember("L"),
    #            registerMember("M"), registerMember("N"),
    #            registerMember("O"), registerMember("P"),
    #            registerMember("Q"), registerMember("R"),
    #            registerMember("A"), registerMember("B"),
    #            registerMember("C"), registerMember("D"),
    #            registerMember("E"), registerMember("F"),
    #            registerMember("G"), registerMember("H"),
    #            registerMember("I"), registerMember("J"),
    #            registerMember("K"), registerMember("L"),
    #            registerMember("M"), registerMember("N"),
    #            registerMember("O"), registerMember("P"),
    #            registerMember("Q"), registerMember("R"),
    #            registerMember("A"), registerMember("B"),
    #            registerMember("C"), registerMember("D"),
    #            registerMember("E"), registerMember("F"),
    #            registerMember("G"), registerMember("H"),
    #            registerMember("I"), registerMember("J"),
    #            registerMember("K"), registerMember("L"),
    #            registerMember("M"), registerMember("N"),
    #            registerMember("O"), registerMember("P"),
    #            registerMember("Q"), registerMember("R"),
    #            registerMember("A"), registerMember("B"),
    #            registerMember("C"), registerMember("D"),
    #            registerMember("E"), registerMember("F"),
    #            registerMember("G"), registerMember("H"),
    #            registerMember("I"), registerMember("J"),
    #            registerMember("K"), registerMember("L"),
    #            registerMember("M"), registerMember("N"),
    #            registerMember("O"), registerMember("P"),
    #            registerMember("Q"), registerMember("R"),
    #            registerMember("A"), registerMember("B"),
    #            registerMember("C"), registerMember("D"),
    #            registerMember("E"), registerMember("F"),
    #            registerMember("G"), registerMember("H"),
    #            registerMember("I"), registerMember("J"),
    #            registerMember("K"), registerMember("L"),
    #            registerMember("M"), registerMember("N"),
    #            registerMember("O"), registerMember("P"),
    #            registerMember("Q"), registerMember("R")]
    # 288
    #players.extend(players2)
    # 576
    #players.extend(players2)
    #players.extend(players2)

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
        createTestSet()
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

    num_of_players = countPlayers()
    rounds = int(math.ceil(math.log(num_of_players, 2)))
    for i in range(rounds):
        current_round = i + 1
        print("round " + str(current_round))
        line_up = swissPairings(tourney)
        print(line_up)
        for x in line_up:
            if x[0] < x[1]:
                reportMatch(tourney, current_round, x[0], x[1])
            elif x[1] < x[0]:
                reportMatch(tourney, current_round, x[1], x[0])
    print("final scores")
    print(playerStandings(tourney))
    print("They rank :")
    rankings = playerRanks(tourney)
    print(rankings)
    rank = 1
    for i in rankings:
        print(str(rank) + ". " + i[1] + " --ID: " + str(i[0]))
        rank += 1
    endTournament()


def querySpeedTest(t_id):
    db = connect()
    c = db.cursor()
    c.execute("select tourney_id "
              "from matches WHERE tourney_id = %s "
              "LIMIT 1", (t_id,))
    in_progress = c.fetchone()
    db.commit()
    db.close()
    return in_progress


if __name__ == '__main__':
    truncateAll()
    testRegisterMember()
    truncateAll()
    testDeleteMembers()
    truncateAll()
    testAddPlayers()
    truncateAll()
    testDeletePlayers()
    truncateAll()
    testMemberStandingsBeforeMatches()
    truncateAll()
    testReportMatch()
    truncateAll()
    runTestCase(True)
    print "Success!  All tests pass!"
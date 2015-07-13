#!/usr/bin/env python
#
# Test cases for tournament.py

from tournamentdb import *
import experiment
import sys


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


def testPairings():
    players = [registerMember("Twilight Sparkle"), registerMember("Fluttershy"),
               registerMember("Applejack"), registerMember("Pinkie Pie"),
               registerMember("Dubstep"), registerMember("B-boy"),
               registerMember("Folk"), registerMember("Electro"),]
    for i in players:
        registerPlayer(i)
    standings = playerStandings()
    print(standings)
    [id1, id2, id3, id4, id5, id6, id7, id8] = [row[0] for row in standings]
    reportMatch(123, 1, id1, id2)
    reportMatch(123, 1, id3, id4)
    reportMatch(123, 1, id5, id6)
    reportMatch(123, 1, id7, id8)
    endTournament()
    [registerPlayer(row[0]) for row in membersBySeeding()]
    print playerSeedings()
    pairings = experiment.main()
    print(pairings)
    if len(pairings) != 4:
        raise ValueError(
            "For eight players, swissPairings should return four pairs.")
    [(pid1, pid2, diff), (pid3, pid4, diff),
     (pid5, pid6, diff), (pid7, pid8, diff)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4]),
                         frozenset([id5, id7]), frozenset([id6, id8])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4]),
                        frozenset([pid5, pid6]), frozenset([pid7, pid8])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def createTestCase():
    """
    Create mock records. Create mock tourney with rounds. Modify algorithm
    to have players face opponents within their own brackets of each round,
    but with opponents opposite ends of that bracket, thereby saving the
    most even matches for last.
    """
    players = [registerMember("A"), registerMember("B"),
               registerMember("C"), registerMember("D"),
               registerMember("E"), registerMember("F"),
               registerMember("G"), registerMember("H")]
    db = connect()
    c = db.cursor()
    x = 8
    for i in players:
        x -= 1
        c.execute("UPDATE members "
                  "SET wins = %s, matches = 8 "
                  "WHERE id = %s;", (x, i,))
    db.commit()
    db.close()
    # Start fake tourney here.
    tourney = 1
    round = 1
    for i in players:
        registerPlayer(i)
    print experiment.main()
    print(membersBySeeding())

if __name__ == '__main__':
    truncateAll()
    createTestCase()

    print "Success!  All tests pass!"



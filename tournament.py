#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

# Extra credits attempted: allow ties; allow multiple tournaments.

import psycopg2
from bleach import clean

PLAYERS_PER_MATCH = 2


def checkCleanArgs(argDict):
    """Errors if any input was not clean to start. Requires output of locals()"""
    for arg in argDict.keys():
        cleanArg = clean(argDict[arg])
        assert cleanArg == str(argDict[arg]), "Bad {0}: {1}".format(
            arg, argDict[arg])


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def addTournament():
    """Creates a tournament, prints the ID for use in other functions."""
    db = connect()
    c = db.cursor()

    c.execute(
        "insert into tournaments (tournament_id) values (default)"
        " returning tournament_id;")

    db.commit()

    new_tournament_id = c.fetchone()[0]

    print "Created tournament with ID: {0}".format(new_tournament_id)

    c.close()
    db.close()

    return new_tournament_id


def checkTournament(tournament_id, cursor):
    """Checks that a tournament exists. Needs a db cursor."""

    # any function using this one must have checkCleanArgs first.

    cursor.execute("select count(*) from tournaments where tournament_id = (%s);",
                   (clean(tournament_id),))
    assert int(cursor.fetchone()[0]) == 1, "Invalid tournament ID"


def deleteTournaments():
    """Deletes all tournaments from tournaments table."""
    # figure out how "cascade" works - will this delete all
    # matches/match_players, etc.? it should.
    db = connect()
    c = db.cursor()

    c.execute("delete from tournaments;")
    db.commit()
    c.close()
    db.close()


def deleteThisTournament(tournament_id):
    """Deletes tournament with given id."""

    argDict = locals()
    checkCleanArgs(argDict)

    db = connect()
    c = db.cursor()

    checkTournament(tournament_id, c)

    sql_statement = "delete from tournaments where tournament_id=(%s);"

    c.execute(sql_statement, (tournament_id,))
    db.commit()
    c.close()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""

    db = connect()
    c = db.cursor()

    sql_statement = "delete from players;"

    c.execute(sql_statement)
    db.commit()
    c.close()
    db.close()


def deletePlayersInTournament(tournament_id):
    """Remove all the player records in a given tournament from the database."""

    argDict = locals()
    checkCleanArgs(argDict)

    db = connect()
    c = db.cursor()

    # check that tournament exists
    checkTournament(tournament_id, c)

    sql_statement = "delete from tournament_players where tournament_id=(%s);"

    c.execute(sql_statement, (tournament_id,))
    db.commit()
    c.close()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""

    db = connect()
    c = db.cursor()

    sql_statement = "select count(*) from players;"

    c.execute(sql_statement)
    nPlayers = int(c.fetchone()[0])  # should only be one row and one col in c
    return nPlayers


def countPlayersInTournament(tournament_id):
    """Returns the number of players currently registered in given tournament."""

    argDict = locals()
    checkCleanArgs(argDict)

    db = connect()
    c = db.cursor()

    # check that tournament exists
    checkTournament(tournament_id, c)

    sql_statement = "select count(*) from tournament_players where tournament_id=(%s);"

    c.execute(sql_statement, (tournament_id,))
    nPlayers = int(c.fetchone()[0])  # should only be one row and one col in c
    return nPlayers


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
        name: the player's full name (need not be unique).
    """

    argDict = locals()
    checkCleanArgs(argDict)

    db = connect()
    c = db.cursor()

    sql_statement = "insert into players (p_name) values (%s) returning player_id;"

    c.execute(sql_statement, (name,))
    db.commit()

    new_player_id = c.fetchone()[0]
    print "Created player {0} with ID: {1}".format(name, new_player_id)

    c.close()
    db.close()

    return new_player_id


def checkPlayer(player_id, cursor):
    """Checks if there is a player with the given ID. Needs a db cursor."""

    # any function using this one must have checkCleanArgs first.

    # argDict = locals()
    # argDict.pop('cursor', None)
    # checkCleanArgs(argDict)

    cursor.execute(
        "select count(*) from players where player_id = %s;", (player_id,))
    assert cursor.fetchone()[0] == 1, "No such player ID registered."


def checkPlayerInTournament(player_id, tournament_id, cursor):
    """Checks if a player is registered in a given tournament. Needs db cursor.
    Returns number of registered players with this info (should be 1 or 0).
    """

    argDict = locals()
    argDict.pop('cursor', None)
    checkCleanArgs(argDict)

    checkTournament(tournament_id, cursor)
    checkPlayer(player_id, cursor)

    cursor.execute("select count(*) from tournament_players"
                   " where tournament_id = %s and player_id = %s;",
                   (tournament_id, player_id,))

    return cursor.fetchone()[0]


def registerPlayerInTournament(player_id, tournament_id):
    """Adds a pre-registered player to a pre-existing tournament."""
    db = connect()
    c = db.cursor()

    # check that player and tournament exist and args are clean,
    # then check that player with this info doesn't already exist.
    assert checkPlayerInTournament(
        player_id, tournament_id, c) == 0, "Player already registered."

    sql_statement = ("insert into tournament_players (player_id, tournament_id)"
                     " values (%s, %s);")

    c.execute(sql_statement, (player_id, tournament_id,))
    db.commit()
    c.close()
    db.close()


def checkTournamentPlayerCount(tournament_id):
    """Makes sure a tournament has the correct number of players without byes."""
    # note that the provided tournament_id is checked to be clean and the
    # tournament_id is checked to be valid within countPlayersInTournament,
    # so any function using this one does not need to do those things redundantly.

    playerCount = countPlayersInTournament(tournament_id)
    morePlayersNeeded = PLAYERS_PER_MATCH - (playerCount % PLAYERS_PER_MATCH)
    assert morePlayersNeeded == PLAYERS_PER_MATCH, ("Register {0} additional "
                                                    "players in tournament {1} "
                                                    "to begin the tournament."
                                                    ).format(
        morePlayersNeeded, tournament_id)


def deleteMatches():
    """Remove all the match records from the database."""

    db = connect()
    c = db.cursor()

    sql_statement = "delete from matches;"
    c.execute(sql_statement)

    # Since p_t_score is not calculated, this is necessary.
    sql_statement_2 = "update tournament_players set p_t_score = 0;"
    c.execute(sql_statement_2)

    db.commit()

    c.close()
    db.close()


def deleteMatchesInTournament(tournament_id):
    """Remove all the match records in a given tournament from the database."""

    argDict = locals()
    checkCleanArgs(argDict)

    db = connect()
    c = db.cursor()

    # check that tournament exists
    checkTournament(tournament_id, c)

    sql_statement = "delete from matches where tournament_id=(%s);"
    c.execute(sql_statement, (tournament_id,))

    # Since p_t_score is not calculated, this is necessary.
    sql_statement_2 = ("update tournament_players set p_t_score = 0 "
                       "where tournament_id = (%s);")
    c.execute(sql_statement_2, (tournament_id,))

    db.commit()
    c.close()
    db.close()


def playerStandings(tournament_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, tournament score, matches):
          id: the player's unique id (assigned by the database)
          name: the player's full name (as registered)
          tournament_score: the player's score in the tournament by WotC rules: 
                            (win=3,tie=1,loss=0)
          matches: the number of matches the player has played
    """

    argDict = locals()
    checkCleanArgs(argDict)

    db = connect()
    c = db.cursor()

    # make sure the number of players in the tournament works without byes,
    # bonus tournament_id check.
    checkTournamentPlayerCount(tournament_id)

    # full_player_info is a view joining tournament_players, match_players, and
    # players to yield this summary info.

    sql_statement = """
    select player_id, p_name, p_t_score, 
        case when nmatches is null then 0 else nmatches end
        from full_player_info
        where tournament_id = (%s) order by p_t_score desc;"""

    c.execute(sql_statement, (tournament_id,))

    standings = c.fetchall()

    c.close()
    db.close()

    return standings


def reportMatch(tournament_id, winner_id, *args):
    """Records the outcome of a single match between two players.

    Args:
        tournament_id: which tournament this match was in
        winner_id:  the id of the player who won, or 0 if a tie
        args: additional arguments are a list of players in the match (allows >2 players)
            *Note this is ALL the match players, not just losers.*
    """

    # check there are the correct # players in the match before recording outcome.
    # using set() differently could allow for "byes" in future iterations.
    assert len(set(args)) == PLAYERS_PER_MATCH, "Bad number of players"

    # Make sure all data is clean

    argDict = locals()
    checkCleanArgs(argDict)

    # need to separately check player *args

    aKeys = range(len(args))
    pDict = dict(zip(aKeys, args))

    checkCleanArgs(pDict)

    # make sure the number of players in the tournament works without byes,
    # bonus tournament_id check.
    checkTournamentPlayerCount(tournament_id)

    db = connect()
    c = db.cursor()

    # check that all players in args are tournament players

    # check that winner is a valid player or 0 (tie); 'is' is pickier than '=='
    # assert clean(winner_id) in args or winner_id is 0, "Invalid winner ID"
    # easier to handle the above in match-creation conditional.

    # check that match should be played in this tournament round

    # create a match with the given data
    # we want to make sure all the provided data is correct, though.

    # case: there is a tie
    if winner_id is 0:
        checkTournament(tournament_id, c)
        c.execute("insert into matches (tournament_id) values (%s)"
                  " returning match_id;", (tournament_id,))
        match_id = int(c.fetchone()[0])
        for player in args:
            assert checkPlayerInTournament(
                player, tournament_id, c) == 1, "Player ID {0} not in tournament.".format(player)
            c.execute("insert into match_players (match_id,player_id)"
                      " values (%s, %s);", (match_id, player,))
            c.execute("update tournament_players set p_t_score = p_t_score + 1 "
                      "where tournament_id = %s and player_id = %s;",
                      (tournament_id, player_id,))
    # case: there is a winner
    elif winner_id in args:
        assert checkPlayerInTournament(
            winner_id, tournament_id, c) == 1, "Winner not a tournament player"
        c.execute("insert into matches (tournament_id, winner_id) values (%s, %s) "
                  "returning match_id;", (tournament_id, winner_id,))
        match_id = int(c.fetchone()[0])
        for player in args:
            assert checkPlayerInTournament(
                player, tournament_id, c) == 1, "Player ID {0} not in tournament.".format(player)
            c.execute("insert into match_players (match_id,player_id)"
                      " values (%s, %s);", (match_id, player,))
            if player is winner_id:
                c.execute("update tournament_players set p_t_score = p_t_score + 3 "
                          "where tournament_id = %s and player_id = %s;",
                          (tournament_id, player,))
            else:
                pass

    else:
        raise ValueError("Invalid winner ID.")

    db.commit()
    c.close()
    db.close()


def swissPairings(tournament_id):
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

    argDict = locals()
    checkCleanArgs(argDict)

    db = connect()
    c = db.cursor()

    standings = playerStandings(tournament_id) # also runs checkTournamentPlayerCount
    nMatchesOnly = [x[3] for x in standings]

    # check if all players have played the same number of matches as the top player.
    isNewRound = True if all(
        playerMatches == standings[0][3] for playerMatches in nMatchesOnly) else False

    if not isNewRound:
        print("Warning: using swissPairings before a round is complete can "
              "result in meaningless pairings.")

    # it is ok if players who have already played one another play each other
    # again, even consecutively, because that may be the fastest way to find a
    # winner.

    sql_statement = """
    select a.player_id, a.p_name, b.player_id, b.p_name 
    from (select row_number() over (order by p_t_score desc) as rn, * 
        from full_player_info) as a, 
    (select row_number() over (order by p_t_score desc) as rn, * 
        from full_player_info) as b
    where a.tournament_id = %s and b.tournament_id = %s and 
        mod(a.rn,2) = 1 and b.rn = a.rn + 1;
    """
    # note that using % as modulo operator doesn't work for psycopg2 connection

    c.execute(sql_statement, (tournament_id, tournament_id,))

    pairings = c.fetchall()

    print(pairings)

    return pairings
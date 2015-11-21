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
    """Connect to the PostgreSQL database.  Returns database connection and cursor."""
    try: 
        db = psycopg2.connect("dbname=tournament")
        cursor = db.cursor()
        return db, cursor
    except:
        print "Database connection failed. Does tournament database exist for this user?"


def addTournament(description):
    """Creates a tournament.

    Args:
        description: A description of the tournament to help identify it.
            100 character max length.

    Returns: 
        new_tournament_id: serial ID of newly created tournament
    """

    argDict = locals()
    checkCleanArgs(argDict)

    db, c = connect()

    # don't need to check input description type because SQL will convert it to
    # varchar upon insertion.
    sql_statement = ("INSERT INTO tournaments (tournament_id, t_description) "
                     "VALUES (DEFAULT, %s) "
                     "RETURNING tournament_id;")        
    c.execute(sql_statement, (description,))
    db.commit()

    new_tournament_id = c.fetchone()[0]
    print "Created tournament with ID: {0}".format(new_tournament_id)

    db.close()

    return new_tournament_id


def checkTournament(tournament_id, cursor):
    """Checks that a tournament exists. Needs a db cursor."""

    # any function using this one must have checkCleanArgs first.

    sql_statement = "SELECT COUNT(*) FROM tournaments WHERE tournament_id = (%s);"
    cursor.execute(sql_statement, clean(tournament_id),)
    assert int(cursor.fetchone()[0]) == 1, "Invalid tournament ID"


def deleteTournaments():
    """Deletes all tournaments from tournaments table."""
    # figure out how "cascade" works - will this delete all
    # matches/match_players, etc.? it should.
    db, c = connect()

    c.execute("DELETE FROM tournaments;")
    db.commit()
    db.close()


def deleteThisTournament(tournament_id):
    """Deletes tournament with given id."""

    argDict = locals()
    checkCleanArgs(argDict)

    db, c = connect()

    checkTournament(tournament_id, c)

    sql_statement = "DELETE FROM tournaments WHERE tournament_id=(%s);"

    c.execute(sql_statement, (tournament_id,))
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""

    db, c = connect()

    sql_statement = "DELETE FROM players;"

    c.execute(sql_statement)
    db.commit()
    db.close()


def deletePlayersInTournament(tournament_id):
    """Remove all the player records in a given tournament from the database."""

    argDict = locals()
    checkCleanArgs(argDict)

    db, c = connect()

    # check that tournament exists
    checkTournament(tournament_id, c)

    sql_statement = "DELETE FROM tournament_players WHERE tournament_id=(%s);"

    c.execute(sql_statement, (tournament_id,))
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered as nPlayers."""

    db, c = connect()

    sql_statement = "SELECT COUNT(*) FROM players;"

    c.execute(sql_statement)
    nPlayers = int(c.fetchone()[0])  # should only be one row and one col in c

    db.close()
    return nPlayers


def countPlayersInTournament(tournament_id):
    """Returns the number of players currently registered in given tournament.

    Args: 
        tournament_id: serial id of tournament whose players you are counting

    Returns: 
        nPlayers: number of players in this tournament
        """

    argDict = locals()
    checkCleanArgs(argDict)

    db, c = connect()

    checkTournament(tournament_id, c)

    sql_statement = "SELECT COUNT(*) FROM tournament_players WHERE tournament_id=(%s);"

    c.execute(sql_statement, (tournament_id,))
    nPlayers = int(c.fetchone()[0])  # should only be one row and one col in c

    db.close()
    return nPlayers


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
        name: the player's full name (need not be unique).

    Returns: 
        new_player_id: new player's serial ID
    """

    argDict = locals()
    checkCleanArgs(argDict)

    db, c = connect()

    sql_statement = "INSERT INTO players (p_name) VALUES (%s) RETURNING player_id;"

    c.execute(sql_statement, (name,))
    db.commit()

    new_player_id = c.fetchone()[0]
    print "Created player {0} with ID: {1}".format(name, new_player_id)

    db.close()

    return new_player_id


def checkPlayer(player_id, cursor):
    """Checks if there is a player with the given ID, AssertionError if not.

    Args:
        player_id: serial ID of player to check
        cursor: cursor from connection to tournament database
    """

    # any function using this one must have checkCleanArgs first.

    cursor.execute(
        "SELECT COUNT(*) FROM players WHERE player_id = %s;", (player_id,))
    assert cursor.fetchone()[0] == 1, "No such player ID registered."


def checkPlayerInTournament(player_id, tournament_id, cursor):
    """Checks if a player is registered in a given tournament.

    Args:
        player_id: serial ID of player to check
        tournament_id: serial ID of tournament the player should be registered in
        cursor: cursor from connection to tournament database

    Returns: 
        number of registered players with given player and tournament id (1 or 0)
    """

    argDict = locals()
    argDict.pop('cursor', None)
    checkCleanArgs(argDict)

    checkTournament(tournament_id, cursor)
    checkPlayer(player_id, cursor)

    sql_statement = ("SELECT COUNT(*) FROM tournament_players"
                     " WHERE tournament_id = %s AND player_id = %s;")

    cursor.execute(sql_statement, (tournament_id, player_id,))

    # return result of count aggregation
    return cursor.fetchone()[0]


def registerPlayerInTournament(player_id, tournament_id):
    """Adds a pre-registered player to a pre-existing tournament.

    Args: 
        player_id: serial ID of player to be added
        tournament_id: serial ID of tournament player is to be added to
    """
    db, c = connect()

    # check that player and tournament exist and args are clean (in checkPlayerInTournament),
    # then check that player with this info doesn't already exist.
    assert checkPlayerInTournament(
        player_id, tournament_id, c) == 0, "Player already registered."

    sql_statement = ("INSERT INTO tournament_players (player_id, tournament_id)"
                     " VALUES (%s, %s);")

    c.execute(sql_statement, (player_id, tournament_id,))
    db.commit()
    db.close()


def checkTournamentPlayerCount(tournament_id):
    """Makes sure a tournament has the correct number of players without byes.

    Args:
        tournament_id: serial ID of tournament whose player count you want
    """
    # note that the provided tournament_id is checked to be clean and the
    # tournament_id is checked to be valid within countPlayersInTournament,
    # so any function using this one does not need to do those things redundantly.

    playerCount = countPlayersInTournament(tournament_id)
    nMorePlayersNeeded = PLAYERS_PER_MATCH - (playerCount % PLAYERS_PER_MATCH)
    assert nMorePlayersNeeded == PLAYERS_PER_MATCH, ("Register {0} additional "
                                                    "players in tournament {1} "
                                                    "to begin the tournament."
                                                    ).format(
        nMorePlayersNeeded, tournament_id)


def deleteMatches():
    """Remove all the match records from the database."""

    db, c = connect()

    sql_statement = "DELETE FROM matches;"
    c.execute(sql_statement)

    # Since p_t_score is not calculated, this is necessary.
    sql_statement_2 = "UPDATE tournament_players SET p_t_score = 0;"
    c.execute(sql_statement_2)

    db.commit()

    db.close()


def deleteMatchesInTournament(tournament_id):
    """Remove all the match records in a given tournament from the database.
    Args:
        tournament_id: serial ID of tournament whose matches you want to delete
    """

    argDict = locals()
    checkCleanArgs(argDict)

    db, c = connect()

    checkTournament(tournament_id, c)

    sql_statement = "DELETE FROM matches WHERE tournament_id=(%s);"
    c.execute(sql_statement, (tournament_id,))

    # Since p_t_score is not calculated, this is necessary.
    sql_statement_2 = ("UPDATE tournament_players SET p_t_score = 0 "
                       "WHERE tournament_id = (%s);")
    c.execute(sql_statement_2, (tournament_id,))

    db.commit()
    db.close()


def playerStandings(tournament_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
        tournament_id: serial ID of tournament whose standings you want

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

    db, c = connect()

    # make sure the number of players in the tournament works without byes,
    # bonus tournament_id check.
    checkTournamentPlayerCount(tournament_id)

    # standings is a function selecting a parameterized subset of rows/columns
    # from full_player_info view. Allows all logic to remain in .sql file.

    sql_statement = """SELECT * from standings(%s);"""
    c.execute(sql_statement, (tournament_id,))

    standings = c.fetchall()

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

    # need to separately check player *args, as they come as a [list].

    aKeys = range(len(args))
    pDict = dict(zip(aKeys, args))

    checkCleanArgs(pDict)

    # make sure the number of players in the tournament works without byes,
    # bonus tournament_id check.
    checkTournamentPlayerCount(tournament_id)

    db, c = connect()

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
        c.execute("INSERT INTO matches (tournament_id) VALUES (%s)"
                  " RETURNING match_id;", (tournament_id,))
        match_id = int(c.fetchone()[0])
        for player in args:
            assert checkPlayerInTournament(
                player, tournament_id, c) == 1, "Player ID {0} not in tournament.".format(player)
            c.execute("INSERT INTO match_players (match_id,player_id)"
                      " VALUES (%s, %s);", (match_id, player,))
            c.execute("UPDATE tournament_players SET p_t_score = p_t_score + 1 "
                      "WHERE tournament_id = %s AND player_id = %s;",
                      (tournament_id, player_id,))
    # case: there is a winner
    elif winner_id in args:
        assert checkPlayerInTournament(
            winner_id, tournament_id, c) == 1, "Winner not a tournament player"
        c.execute("INSERT INTO matches (tournament_id, winner_id) VALUES (%s, %s) "
                  "RETURNING match_id;", (tournament_id, winner_id,))
        match_id = int(c.fetchone()[0])
        for player in args:
            assert checkPlayerInTournament(
                player, tournament_id, c) == 1, "Player ID {0} not in tournament.".format(player)
            c.execute("INSERT INTO match_players (match_id,player_id)"
                      " VALUES (%s, %s);", (match_id, player,))
            if player is winner_id:
                c.execute("UPDATE tournament_players SET p_t_score = p_t_score + 3 "
                          "WHERE tournament_id = %s AND player_id = %s;",
                          (tournament_id, player,))
            else:
                pass

    else:
        raise ValueError("Invalid winner ID.")

    db.commit()
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

    db, c = connect()

    standings = playerStandings(tournament_id)
    # playerStandings also internally asserts correct number of players.
    nMatchesOnly = [x[3] for x in standings]

    # check if all players have played the same number of matches as the top player.
    isNewRound = True if all(
        playerMatches == standings[0][3] for playerMatches in nMatchesOnly) else False

    if not isNewRound:
        print("Warning: using swissPairings before a round is complete can "
              "result in meaningless pairings.")

    sql_statement = """SELECT * FROM pairings(%s);"""
    c.execute(sql_statement, (tournament_id,))

    roundPairings = c.fetchall()

    db.close()

    print(roundPairings)

    return roundPairings
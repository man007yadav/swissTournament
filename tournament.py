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


def deleteMatches():
    """Remove all the match records from the database."""

    db = connect()
    c = db.cursor()

    sql_statement = "delete from matches;"

    c.execute(sql_statement)
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

    c.execute(sql_statement, (clean(tournament_id),))
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

    sql_statement = "delete from players where tournament_id=(%s);"

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

    sql_statement = "select count(*) from tournament players where tournament_id=(%s);"

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

    sql_statement = "insert into players (p_name) values (%s);"

    c.execute(sql_statement, (name,))
    db.commit()
    c.close()
    db.close()


def checkPlayer(player_id, cursor):
    """Checks if there is a player with the given ID. Needs a db cursor."""

    # any function using this one must have checkCleanArgs first. 

    # argDict = locals()
    # argDict.pop('cursor', None)
    # checkCleanArgs(argDict)

    cursor.execute("select count(*) from players where player_id = %s;",(player_id,))
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

    return c.fetchone()[0]



def registerPlayerInTournament(player_id, tournament_id):
    """Adds a pre-registered player to a pre-existing tournament."""
    db = connect()
    c = db.cursor()

    # check that player and tournament exist and args are clean, 
    # then check that player with this info doesn't already exist.
    assert checkPlayerInTournament(player_id, tournament_id, c) == 0, "Player already registered."

    sql_statement = ("insert into tournament_players (player_id, tournament_id)"
                     " values (%s, %s);")

    c.execute(sql_statement, (player_id, tournament_id,))
    db.commit()
    c.close()
    db.close()




def addTournament():
    """Creates a tournament, prints the ID for use in other functions."""
    db = connect()
    c = db.cursor()

    c.execute(
        "insert into tournaments (tournament_id) values (default)"
        " returning tournament_id;")
    print c.fetchone()[0]
    db.commit()
    c.close()
    db.close()



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

    # check that tournament exists
    checkTournament(tournament_id, c)

    # below SQL joins tournament_players to a count aggregation of
    # match_players so we know nmatches played and player score,
    # then to players table so we can get player names.

    # TODO: find a way to calculate score using SQL instead of updating a
    # score field - use a self-join?

    sql_statement = """
    select tp.player_id, p.p_name, tp.p_t_score, 
        case when mp.nmatches is null then 0 else mp.nmatches end  
    from (tournament_players as tp
        left outer join 
        (select player_id, count(*) as nmatches 
            from match_players group by player_id) as mp 
        on (tp.player_id = mp.player_id)) 
        inner join players as p 
        on (tp.player_id = p.player_id)
    where tp.tournament_id = (%s) order by tp.p_t_score desc;"""

    # note that the match count returns as a long int

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

    # make sure to assert that there are the correct # players in the match
    # before recording an outcome.

    assert len(args) == PLAYERS_PER_MATCH, "Bad number of players"

    # Make sure all data is clean

    argDict = locals()
    checkCleanArgs(argDict)

    # need to separately check player *args

    aKeys = range(len(args))
    pDict = dict(zip(aKeys, args))

    checkCleanArgs(pDict)

    db = connect()
    c = db.cursor()

    # check that all players in args are tournament players

    # check that winner is a valid player or 0 (tie); 'is' is pickier than '=='
    # assert clean(winner_id) in args or winner_id is 0, "Invalid winner ID"
    # easier to handle the above in match-creation conditional.

    # check that match should be played in this tournament round

    # create a match with the given data
    # we want to make sure all the provided data is correct, though. 
    if winner_id is 0:
        checkTournament(tournament_id, c)
        c.execute("insert into matches (tournament_id) values (%s)" 
            " returning match_id;", (tournament_id,))
        match_id = int(c.fetchone()[0])
        for player in args:
            checkPlayerInTournament(player, tournament_id, c)
            c.execute("insert into match_players (match_id,player_id)"
                " values (%s, %s);", (match_id, player,))
            c.execute("update tournament_players set p_t_score = p_t_score + 1 "
                "where tournament_id = %s and player_id = %s;",
                (tournament_id, player_id,))

    elif winner_id in args: 
        assert checkPlayerInTournament(winner_id, tournament_id, c) == 1, "Winner not a tournament player"
        c.execute("insert into matches (tournament_id, winner_id) values (%s, %s)"
            " returning match_id;", (tournament_id, winner_id,))
        match_id = int(c.fetchone()[0])
        for player in args:
            checkPlayerInTournament(player, tournament_id, c)
            c.execute("insert into match_players (match_id,player_id)"
                " values (%s, %s);", (match_id, player,))
            if player is winner_id:
                c.execute("update tournament_players set p_t_score = p_t_score + 3 "
                    "where tournament_id = %s and player_id = %s;",
                    (tournament_id, player_id,))
            else:
                pass

    else:
        raise ValueError("Invalid winner ID.")

    db.commit()
    c.close()
    db.close()


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

    # get player standings: if nmatches is same for all players, generate a full round
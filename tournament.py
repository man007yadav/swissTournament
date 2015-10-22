#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from bleach import clean

PLAYERS_PER_MATCH = 2


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

    db = connect()
    c = db.cursor()

    # check that tournament exists
    c.execute("select count(*) from tournaments where tournament_id = (%s);",
              (clean(tournament_id),))
    assert int(c.fetchone()[0]) == 1, "Invalid tournament ID"

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

    db = connect()
    c = db.cursor()

    # check that tournament exists
    c.execute("select count(*) from tournaments where tournament_id = (%s);",
              (clean(tournament_id),))
    assert int(c.fetchone()[0]) == 1, "Invalid tournament ID"

    sql_statement = "delete from players where tournament_id=(%s);"

    c.execute(sql_statement, (clean(tournament_id),))
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

    db = connect()
    c = db.cursor()

    # check that tournament exists
    c.execute("select count(*) from tournaments where tournament_id = (%s);",
              (clean(tournament_id),))
    assert int(c.fetchone()[0]) == 1, "Invalid tournament ID"

    sql_statement = "select count(*) from tournament players where tournament_id=(%s);"

    c.execute(sql_statement, (clean(tournament_id),))
    nPlayers = int(c.fetchone()[0])  # should only be one row and one col in c
    return nPlayers


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
        name: the player's full name (need not be unique).
    """

    db = connect()
    c = db.cursor()

    sql_statement = "insert into players (p_name) values (%s);"

    c.execute(sql_statement, (clean(name),))
    db.commit()
    c.close()
    db.close()


def registerPlayerInTournament(player_id, tournament_id):
    """Adds a pre-registered player to a pre-existing tournament."""
    db = connect()
    c = db.cursor()

    # check that player and tournament exist, redundant with final sql
    # statement
    c.execute("select count(*) from players where player_id = (%s);",
              (clean(player_id),))
    assert int(c.fetchone()[0]) == 1, "Invalid player ID"

    c.execute("select count(*) from tournaments where tournament_id = (%s);",
              (clean(tournament_id),))
    assert int(c.fetchone()[0]) == 1, "Invalid tournament ID"

    sql_statement = "insert into tournament_players (player_id, tournament_id) values (%s, %s);"

    c.execute(sql_statement, (clean(player_id), clean(tournament_id),))
    db.commit()
    c.close()
    db.close()


def addTournament():
    """Creates a tournament, prints the ID for use in other functions."""
    db = connect()
    c = db.cursor()

    c.execute(
        "insert into tournaments (tournament_id) values (default) returning tournament_id;")
    print c.fetchone()[0]
    db.commit()
    c.close()
    db.close()


def deleteTournaments():
    """Deletes all tournaments from tournaments table."""
    db = connect()
    c = db.cursor()

    c.execute("delete from tournaments;")
    db.commit()
    c.close()
    db.close()


def deleteThisTournament(tournament_id):
    """Deletes tournament with given id."""
    db = connect()
    c = db.cursor()

    # check that tournament exists
    c.execute("select count(*) from tournaments where tournament_id = (%s);",
              (clean(tournament_id),))
    assert int(c.fetchone()[0]) == 1, "Invalid tournament ID"

    sql_statement = "delete from tournaments where tournament_id=(%s);"

    c.execute(sql_statement, (clean(tournament_id),))
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
          tournament_score: the player's score in the tournament by WotC rules (win=3,tie=1,loss=0)
          matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()

    # check that tournament exists - fail early and notify with lowest-cost
    # query
    c.execute("select count(*) from tournaments where tournament_id = (%s);",
              (clean(tournament_id),))
    assert int(c.fetchone()[0]) == 1, "Invalid tournament ID"

    # below SQL joins tournament_players to a count aggregation of 
    # match_players so we know nmatches played and player score, 
    # then to players table so we can get player names.

    # TODO: find a way to calculate score using SQL instead of updating a score field

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

    c.execute(sql_statement, (clean(tournament_id),))

    standings = c.fetchall()

    return standings


def reportMatch(tournament_id, winner_id, *args):
    """Records the outcome of a single match between two players.

    Args:
        tournament_id: which tournament this match was in
        winner_id:  the id of the player who won, or 0 if a tie
        args: additional arguments are a list of players in the match (allows >2 players)
    """

    # make sure to assert that there are at least 2 players in the match
    # before recording an outcome.


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

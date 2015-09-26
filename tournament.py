#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from bleach import clean


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

# def deleteMatchesInTournament(tournament_id):


def deletePlayers():
    """Remove all the player records from the database."""
    
    db = connect()
    c = db.cursor()

    sql_statement = "delete from players;"
    
    c.execute(sql_statement)
    db.commit()
    c.close()
    db.close()

# def deletePlayersInTournament(tournament_id):

def countPlayers():
    """Returns the number of players currently registered."""
    
    db = connect()
    c = db.cursor()

    sql_statement = "select count(*) from players;"
    
    c.execute(sql_statement)
    nPlayers = int(c.fetchone()[0])
    return nPlayers

# def countPlayersInTournament(tournament_id):


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
    
    c.execute(sql_statement,(clean(name),))
    db.commit()
    c.close()
    db.close()

# def registerPlayerInTournament(player_id, tournament_id):


def playerStandings(tournament_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
 
 
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



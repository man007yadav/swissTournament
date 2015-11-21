-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
--
-- NOTES:
-- Began with statements: create database tournament; \c tournament; \i tournament.sql;
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament


DROP TABLE IF EXISTS tournaments;
CREATE TABLE tournaments(
    tournament_id   SERIAL PRIMARY KEY,
    t_description   VARCHAR(100)
);

DROP TABLE IF EXISTS players;
CREATE TABLE players(
    player_id   SERIAL PRIMARY KEY,
    p_name      VARCHAR(30) NOT NULL
);

DROP TABLE IF EXISTS tournament_players;
CREATE TABLE tournament_players(
    player_id       INTEGER REFERENCES players(player_id) 
                            ON UPDATE CASCADE ON DELETE CASCADE,
    tournament_id   INTEGER REFERENCES tournaments(tournament_id)
                            ON UPDATE CASCADE ON DELETE CASCADE,
    p_t_score       INTEGER DEFAULT 0,
    -- this score field will get updated frequently, to minimize #queries to get standings.
    primary key (player_id, tournament_id)
);

DROP TABLE IF EXISTS matches;
CREATE TABLE matches(
    match_id        SERIAL PRIMARY KEY,
    tournament_id   INTEGER REFERENCES tournaments(tournament_id)
                            ON UPDATE CASCADE ON DELETE CASCADE,
    -- winnerID is serial ID of player if there was a winner, and 0 if there was a tie.
    winner_id       INTEGER REFERENCES players(player_id)
                            ON UPDATE CASCADE ON DELETE CASCADE
                    -- deleting winner player deletes the match.
    -- constraint on winner_id values is managed in Python code.
);

DROP TABLE IF EXISTS match_players;
CREATE TABLE match_players(
    match_id    INTEGER REFERENCES matches(match_id)
                        ON UPDATE CASCADE ON DELETE CASCADE,
    player_id   INTEGER REFERENCES players(player_id)
                        ON UPDATE CASCADE ON DELETE CASCADE
);

-- helper view used to simplify standings and pairings functions
CREATE OR REPLACE VIEW full_player_info AS
    SELECT tp.player_id, tp.tournament_id, tp.p_t_score, mp.nmatches, p.p_name
    FROM tournament_players AS tp
        LEFT OUTER JOIN
        --CAST is used because otherwise returns an ugly long int type.
        (SELECT player_id, CAST(COUNT(*) AS INT) AS nmatches 
            FROM match_players GROUP BY player_id) AS mp 
        ON (tp.player_id = mp.player_id) 
        INNER JOIN players AS p ON (tp.player_id = p.player_id)
    ORDER BY tp.p_t_score DESC;

-- functions used to accept tournament_id parameter in Python code.
--used in tournament.playerStandings
CREATE OR REPLACE FUNCTION standings(tourn_id INT)
    RETURNS TABLE(player_id INT, p_name VARCHAR(30), p_t_score INT, nmatches INT)
    AS $func$
    SELECT player_id, p_name, p_t_score, 
        CASE WHEN nmatches IS NULL THEN 0 ELSE nmatches END
    FROM full_player_info
    WHERE tournament_id = tourn_id
    $func$ LANGUAGE SQL;

--used in tournament.swissPairings
CREATE OR REPLACE FUNCTION pairings(tourn_id INT)
    RETURNS TABLE(a_player_id INT, a_p_name VARCHAR(30), b_player_id INT, b_p_name VARCHAR(30))
    AS $func$
    SELECT a.player_id, a.p_name, b.player_id, b.p_name
    FROM (SELECT row_number() OVER () AS rn, * 
        FROM full_player_info) AS a, 
    (SELECT row_number() OVER () AS rn, * 
        FROM full_player_info) AS b
    WHERE a.tournament_id = tourn_id AND b.tournament_id = tourn_id AND
    -- Change second argument to MOD in addition to overall structure if PLAYERS_PER_MATCH changes 
        MOD(a.rn,2) = 1 AND b.rn = a.rn + 1
    $func$ LANGUAGE SQL;
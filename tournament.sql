-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- began with statements: create database tournaments; \c tournaments; \i tournament.sql

drop table if exists matches;
create table matches(
    tournamentID    integer,
    playerIDs       integer ARRAY[2],
    -- winnerID is serial ID of player if there was a winner, and 0 if there was a tie
    winnerID        integer
);

drop table if exists players;
create table players(
    name varchar(30),
);

-- view for all matches a player has participated in (maybe grouped by tournament) will help determine their record.

drop table if exists tournaments;
create table tournaments();

-- view of all matches in a given tournament


-- nRounds is log base nPlayersPerMatch (2) of nPlayersInTournament

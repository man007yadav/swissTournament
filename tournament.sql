-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
--
-- NOTES:
-- Began with statements: create database tournaments; \c tournaments; \i tournament.sql;


drop table if exists tournaments;
create table tournaments(tournament_id serial primary key);

drop table if exists matches;
create table matches(
    match_id        serial primary key,
    tournament_id   integer references tournaments(tournament_id),
    -- winnerID is serial ID of player if there was a winner, 
    -- and 0 if there was a tie; see if there's a constraint to enforce this - can we use null?
    winner_id       integer
);

drop table if exists players;
create table players(
    player_id   serial primary key,
    p_name      varchar(30)
);

-- view for all matches a player has participated in (maybe grouped by 
-- tournament) will help determine their record.

drop table if exists tournament_players;
create table tournament_players(
    player_id       integer references players(player_id) 
                            on update cascade on delete cascade,
    tournament_id   integer references tournaments(tournament_id)
                            on update cascade on delete cascade,
    p_t_score       smallint default 0,
    -- this score field will get updated frequently, to minimize #queries to get standings.
    primary key (player_id, tournament_id)
);

drop table if exists match_players;
create table match_players(
    match_id    integer references matches(match_id),
    player_id   integer references players(player_id)
);

-- select matchID,winnerID from matches where tournament_id = thisTourn; 
    -- for each player find out which matches they participated in and what their score was (cases for playerid=winnerid,
    -- playerid != winnerid, winnerid=0, return an ordered list of players by score. 
-- view of all matches in a given tournament


-- nRounds is log base nPlayersPerMatch (2) of nPlayersInTournament

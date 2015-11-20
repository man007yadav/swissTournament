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


drop table if exists tournaments;
create table tournaments(tournament_id serial primary key);

drop table if exists players;
create table players(
    player_id   serial primary key,
    p_name      varchar(30)
);

drop table if exists tournament_players;
create table tournament_players(
    player_id       integer references players(player_id) 
                            on update cascade on delete cascade,
    tournament_id   integer references tournaments(tournament_id)
                            on update cascade on delete cascade,
    p_t_score       integer default 0,
    -- this score field will get updated frequently, to minimize #queries to get standings.
    primary key (player_id, tournament_id)
);

drop table if exists matches;
create table matches(
    match_id        serial primary key,
    tournament_id   integer references tournaments(tournament_id)
                            on update cascade on delete cascade,
    -- winnerID is serial ID of player if there was a winner, and 0 if there was a tie.
    winner_id       integer references players(player_id)
                            on update cascade on delete cascade
                    -- deleting winner player deletes the match.
    -- constraint on winner_id values is managed in Python code.
);

drop table if exists match_players;
create table match_players(
    match_id    integer references matches(match_id)
                        on update cascade on delete cascade,
    player_id   integer references players(player_id)
                        on update cascade on delete cascade
);

create or replace view full_player_info as
    select tp.player_id, tp.tournament_id, tp.p_t_score, mp.nmatches, p.p_name
    from tournament_players as tp
        left outer join
        (select player_id, cast(count(*) as int) as nmatches 
            from match_players group by player_id) as mp 
        on (tp.player_id = mp.player_id) 
        inner join players as p on (tp.player_id = p.player_id);

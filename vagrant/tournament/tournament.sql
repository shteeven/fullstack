-- Database: tournament

-- DROP DATABASE tournament;

CREATE DATABASE tournament;
\c tournament;

-- Table: matches

DROP TABLE matches;

CREATE TABLE matches
(
  match_id integer NOT NULL,
  match_outcome real DEFAULT 0,
  player_id integer NOT NULL,
  opponent_id integer NOT NULL,
  tourney_id integer NOT NULL,
  CONSTRAINT matches_pkey PRIMARY KEY (match_id, player_id, tourney_id)
)
WITH (
  OIDS=FALSE
);

-- Table: members

DROP TABLE members;

CREATE TABLE members
(
  id serial NOT NULL,
  name text NOT NULL,
  wins real DEFAULT 0,
  matches integer DEFAULT 0,
  CONSTRAINT id PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

-- Table: players

DROP TABLE players;

CREATE TABLE players
(
  id serial NOT NULL,
  seed_score real DEFAULT 0,
  name text,
  matches integer DEFAULT 0,
  wins real DEFAULT 0,
  CONSTRAINT players_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);




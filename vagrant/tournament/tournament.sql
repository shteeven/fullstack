-- Database: tournament

-- DROP DATABASE tournament;

CREATE DATABASE tournament
  WITH OWNER = "Shtav"
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1;

-- DROP SCHEMA public;

CREATE SCHEMA public
  AUTHORIZATION "Shtav";

GRANT ALL ON SCHEMA public TO "Shtav";
GRANT ALL ON SCHEMA public TO public;
COMMENT ON SCHEMA public
  IS 'standard public schema';

-- Table: matches

-- DROP TABLE matches;

CREATE TABLE matches
(
  match_id integer NOT NULL,
  match_outcome integer NOT NULL DEFAULT 0,
  player_id integer NOT NULL,
  opponent_id integer NOT NULL,
  tourney_id integer NOT NULL,
  CONSTRAINT matches_pkey PRIMARY KEY (match_id, player_id, tourney_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE matches
  OWNER TO "Shtav";

-- Table: members

-- DROP TABLE members;

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
ALTER TABLE members
  OWNER TO "Shtav";

-- Table: players

-- DROP TABLE players;

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
ALTER TABLE players
  OWNER TO "Shtav";


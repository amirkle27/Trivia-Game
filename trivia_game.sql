select count (*) from questions;
 select * from questions;


drop function new_player;

CREATE OR REPLACE FUNCTION new_player(
        new_username VARCHAR(50),
        new_password TEXT,
        new_email VARCHAR(100),
        new_age INTEGER,
        OUT player_id INTEGER
        )
    language plpgsql AS
    $$
    begin
        IF EXISTS(SELECT 1 FROM players WHERE players.username = new_username ) THEN
            RAISE EXCEPTION 'This username already exists. Try something else';
        END IF;
        IF EXISTS(SELECT 1 FROM players WHERE players.password = new_password) THEN
            RAISE EXCEPTION 'This password already exists. Try something else';
        END IF;
        IF EXISTS(SELECT 1 FROM players WHERE players.email = new_email) THEN
            RAISE EXCEPTION 'This email already exists. Try something else';
        ELSE
            INSERT INTO players (username, password, email, age) VALUES (
                new_username,
                new_password,
                new_email,
                new_age)
            RETURNING player_id into player_id;
        END IF;

    end;
$$;




drop function log_new_player;

CREATE OR REPLACE FUNCTION log_new_player()
    RETURNS TRIGGER AS $$
        begin
            INSERT INTO new_player_log (player_id) VALUES (NEW.player_id);
            RETURN NEW;
        end;
    $$ LANGUAGE plpgsql;

drop TRIGGER IF EXISTS new_user_registration ON players;
CREATE TRIGGER new_user_registration
AFTER INSERT ON players
FOR EACH ROW
EXECUTE FUNCTION log_new_player();

ALTER TABLE players DISABLE TRIGGER new_user_registration;
SELECT setval('players_player_id_seq', (SELECT MAX(player_id) FROM players));
DELETE FROM players;
select * from players;
select * from player_answers;
select * from new_player_log;
ALTER SEQUENCE players_player_id_seq RESTART WITH 1;

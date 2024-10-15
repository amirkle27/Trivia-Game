select count (*) from questions;
 select * from questions;


drop procedure new_player;

CREATE OR REPLACE PROCEDURE new_player(
        new_username VARCHAR(50),
        new_password VARCHAR(100),
        new_email VARCHAR(100),
        new_age INTEGER
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
                new_age);
        END IF;

    end;
$$;

CALL new_player('amirkle27', 'ItsAniceTrivia100', 'amirkle@gmail.com', 41);
CALL new_player('guy', 'WhyDoINeedAPasswordForASimpleTriviaGame', 'guy@gmail.com', 39);

SELECT * FROM players;

-- CALL new_player('amirkle27', 'AMIR', 'amirklei@gmail.com', 41);
-- CALL new_player('amirkle', 'ItsAniceTrivia100', 'amirklee@gmail.com', 41);
-- CALL new_player('amir', 'TRY', 'amirkle@gmail.com', 41);

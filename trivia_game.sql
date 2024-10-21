select count (*) from questions;
 select * from questions;


DROP FUNCTION IF EXISTS new_player;

CREATE OR REPLACE FUNCTION new_player(
    new_username VARCHAR(50),
    new_password TEXT,
    new_email VARCHAR(100),
    new_age INTEGER,
    OUT out_player_id INTEGER
)
LANGUAGE plpgsql AS
$$
BEGIN
    -- Check for existing username
    IF EXISTS(SELECT 1 FROM players WHERE players.username = new_username) THEN
        RAISE EXCEPTION 'This username already exists. Try something else';
    END IF;

    -- Check for existing password
    IF EXISTS(SELECT 1 FROM players WHERE players.password = new_password) THEN
        RAISE EXCEPTION 'This password already exists. Try something else';
    END IF;

    -- Check for existing email
    IF EXISTS(SELECT 1 FROM players WHERE players.email = new_email) THEN
        RAISE EXCEPTION 'This email already exists. Try something else';
    ELSE
        -- Insert into players and return player_id
        INSERT INTO players (username, password, email, age)
        VALUES (new_username, new_password, new_email, new_age)
        RETURNING player_id INTO out_player_id;
    END IF;
END;
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


drop procedure update_player_answers;

CREATE OR REPLACE PROCEDURE update_player_answers(
    IN p_player_id INTEGER,
    IN p_question_id INTEGER,
    IN p_selected_answer CHAR(1))
language plpgsql AS
    $$
    begin
        DECLARE
            v_is_correct BOOLEAN;
        BEGIN
            SELECT CASE
                WHEN q.correct_answer = p_selected_answer THEN TRUE
                ELSE FALSE
            END
            INTO v_is_correct
            FROM questions q
            WHERE q.question_id = p_question_id;

            INSERT INTO player_answers(player_id, question_id, selected_answer, is_correct)
            VALUES (p_player_id,p_question_id,p_selected_answer,v_is_correct)
            ON CONFLICT (player_id,question_id)
            DO UPDATE
            SET selected_answer = EXCLUDED.is_correct;

            UPDATE players
            SET questions_solved=questions_solved+1
            WHERE player_id=p_player_id;
        END;
    end;

$$;

drop procedure update_high_score_table;

CREATE OR REPLACE procedure update_high_score_table(
    IN p_player_id INTEGER)
language plpgsql AS
    $$
    DECLARE v_correct_answer INTEGER;
        begin
            SELECT COUNT (*)
            INTO v_correct_answer
            FROM player_answers
            WHERE player_id = p_player_id AND is_correct = TRUE;

            IF v_correct_answer > 5 THEN
                INSERT INTO high_scores (player_id, score_id, finished_at)
                VALUES (p_player_id, v_correct_answer, CURRENT_TIMESTAMP);
            END IF;
        end;
    $$;




SELECT setval('players_player_id_seq', (SELECT MAX(player_id) FROM players));
DELETE FROM players;
select * from players;
select * from player_answers;
select * from new_player_log;
ALTER SEQUENCE players_player_id_seq RESTART WITH 1;

-- drop procedure add_answer_to_player_answers
--
-- CREATE OR REPLACE PROCEDURE add_answer_to_player_answers()

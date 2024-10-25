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

drop function get_random_questions;

CREATE OR REPLACE FUNCTION get_random_questions ()
    RETURNS TABLE (
        question_id INTEGER,
        question_text TEXT,
        answer_a TEXT,
        answer_b TEXT,
        answer_c TEXT,
        answer_d TEXT,
        correct_answer CHAR(1))
language plpgsql AS
    $$
    begin
        RETURN QUERY
        SELECT q.question_id, q.question_text, q.answer_a, q.answer_b, q.answer_c, q.answer_d, q.correct_answer
        FROM questions q
        ORDER BY RANDOM()
        LIMIT 20;
        END
    $$;



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
            VALUES (p_player_id,p_question_id,p_selected_answer,v_is_correct);

            UPDATE players
            SET questions_solved=questions_solved+1
            WHERE player_id=p_player_id;
        END;
    end;

$$;

drop procedure update_high_score_table_start_time;

CREATE OR REPLACE procedure update_high_score_table_start_time(
    IN p_player_id INTEGER)
language plpgsql AS
    $$
        begin
            INSERT INTO high_scores (player_id, started_at)
            VALUES (p_player_id, CURRENT_TIMESTAMP);
        end;
    $$;


drop procedure update_high_score_table_finish_time;

CREATE OR REPLACE procedure update_high_score_table_finish_time(
    IN p_player_id INTEGER)
language plpgsql AS
    $$
    DECLARE v_correct_answer INTEGER;
            v_latest_score_id INTEGER;
        begin
            SELECT COUNT (*)
            INTO v_correct_answer
            FROM player_answers
            WHERE player_id = p_player_id AND is_correct = TRUE;

            IF v_correct_answer >= 5 THEN
                SELECT score_id
                INTO v_latest_score_id
                FROM high_scores
                WHERE player_id = p_player_id
                ORDER BY started_at DESC
                LIMIT 1;

                UPDATE high_scores
                SET finished_at = CURRENT_TIMESTAMP,
                    total_game_time = (CURRENT_TIMESTAMP - started_at),
                    score = v_correct_answer
                WHERE  score_id = v_latest_score_id;
            END IF;
        end;
    $$;

drop function maintain_top_20_scores;

CREATE OR REPLACE FUNCTION maintain_top_20_scores()
RETURNS TRIGGER
language plpgsql AS
    $$
    begin
        DELETE FROM high_scores
        WHERE score_id NOT IN
              (SELECT score_id
                FROM high_scores
                ORDER BY score DESC
                LIMIT 20);
        RETURN NEW;
    end;
    $$;

drop TRIGGER limit_high_scores ON high_scores;

CREATE TRIGGER limit_high_scores
AFTER INSERT ON high_scores
FOR EACH ROW
EXECUTE FUNCTION maintain_top_20_scores();

SELECT setval('players_player_id_seq', (SELECT MAX(player_id) FROM players));
DELETE FROM players;
select * from players;
select * from player_answers;
select * from new_player_log;
select * from high_scores;
select * from questions;
ALTER SEQUENCE players_player_id_seq RESTART WITH 1;

-- drop procedure add_answer_to_player_answers
--f
-- CREATE OR REPLACE PROCEDURE add_answer_to_player_answers()


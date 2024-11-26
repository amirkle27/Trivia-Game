import matplotlib.pyplot as plt
import time
import itertools
from time import sleep
import psycopg2
import psycopg2.extras
from pymongo import MongoClient
import bcrypt
from random import sample

connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="admin",
        port="5432"
    )
pg_cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
client = MongoClient("mongodb://localhost:27017/")
mongo_db = client["Trivia_MongoDB"]
questions_collection = mongo_db["questions"]
player_questions_collection = mongo_db['player_questions']

colors = [
        "\033[91m",  # Red
        "\033[92m",  # Green
        "\033[33m",  # Yellow
        "\033[94m",  # Blue
        "\033[95m",  # Magenta
        "\033[96m",  # Cyan
    ]
reset = "\033[0m"  # Reset color to default

def print_table(data, headers, column_widths,row_colors=None):
    """Dynamically prints a table with specified headers, data, and column widths."""
    header_row = "| " + " | ".join(f"{header:^{column_widths[i]}}" for i, header in enumerate(headers)) + " |"
    separator_row = "|" + "|".join("-" * (width + 2) for width in column_widths) + "|"
    print("\033[97m" + header_row + "\033[0m")
    print(separator_row)
    left_align_columns = {i for i, header in enumerate(headers) if "Question Text" in header or "Topic" in header}
    for idx, row in enumerate(data):
        color = row_colors[idx] if row_colors and idx < len(row_colors) else "\033[0m"
        row_text = "| " + " | ".join(
            f"{str(row[i]):<{column_widths[i]}}" if i in left_align_columns else f"{str(row[i]):^{column_widths[i]}}"
            for i in range(len(headers))
        ) + " |"
        print(color + row_text + "\033[0m")
    print("\n")

def format_results(results, keys, default="N/A"):
    """
    Formats a list of dictionaries (results) into a list of lists based on the provided keys.
    - results: List of dictionaries containing the data.
    - keys: List of keys to extract from each dictionary.
    - default: Default value to use if a key is missing.
    """
    return [
        [row.get(key, default) for key in keys]
        for row in results
    ]

def get_age_group(age):
    """Determine the age group range for a given age"""
    try:
        age = int(age)
    except ValueError:
        print("Invalid input! Age must be a number.")
        return None
    age_groups = {
        "1-5": range(1, 6),
        "5-10": range(6, 11),
        "10-15": range(11, 16),
        "15-20": range(16, 21),
        "20-30": range(21, 31),
        "30-40": range(31, 41),
        "40-100": range(41, 101)
    }
    for group, age_range in age_groups.items():
        if age in age_range:
            return group
    print("No matching age groups for this age. Please try again!")
    return None

def fetch_remaining_questions(player_id):
    """Fetch the remaining questions for a returning player from player_questions_collection."""
    return list(player_questions_collection.find({"player_id": player_id, "is_answered": False}))


def create_player_questions_set(player_id, age_group, selected_topics):
    """Creates a unique set of 20 random questions for a player's quiz according to their age and selected topics."""
    player_questions_collection.delete_many({"player_id": player_id})
    questions = list(questions_collection.find({"Age_Group": age_group, "Topic": {"$in": selected_topics}}))
    if len(questions) < 20:
        print("Not enough questions available for the selected topics. Adding all available questions.")
        player_questions = questions
    else:
        player_questions = sample(questions, 20)
    questions_for_session = [
        {
            "player_id": player_id,
            "Question_No": question["Question_No"],
            "Question_Text": question["Question_Text"],
            "Answer_a": question["Answer_a"],
            "Answer_b": question["Answer_b"],
            "Answer_c": question["Answer_c"],
            "Answer_d": question["Answer_d"],
            "Correct_Answer": question["Correct_Answer"],
            "Topic": question["Topic"],
            "Age_Group": question["Age_Group"],
            "is_answered": False
        }
        for question in player_questions
    ]
    player_questions_collection.insert_many(questions_for_session)



def update_player_answer(player_id, question_id, selected_answer):
    """Updates player answer and scores based on correctness."""
    question = player_questions_collection.find_one({"Question_No": question_id, "player_id": player_id})
    if not question:
        print(f"No question found with Question_No {question_id} for player {player_id}")
        return
    correct_answer = question['Correct_Answer']
    is_correct = (selected_answer == correct_answer)
    try:
        query = "CALL update_player_answers (%s, %s, %s, %s);"
        pg_cursor.execute(query, (player_id, question_id, selected_answer, is_correct))
        connection.commit()
        player_questions_collection.update_one(
            {"Question_No": question_id, "player_id": player_id},
            {"$set": {"is_answered": True}}
        )
    except Exception as e:
        print(f"An error occurred while updating player answers: {e}")
        connection.rollback()

def verify_player(username, password):
    """Verify if a returning player exists in PostgreSQL with an unfinished game."""
    try:
        pg_cursor.execute("SELECT player_id, password, age FROM players WHERE username = %s", (username,))
        result = pg_cursor.fetchone()
        if result and bcrypt.checkpw(password.encode(), result['password'].encode()):
            player_id = result['player_id']
            age = result['age']
            remaining_questions = player_questions_collection.count_documents(
                {"player_id": player_id, "is_answered": False})
            unfinished_game = remaining_questions > 0
            return player_id, unfinished_game, age
        else:
            return None, None, None
    except Exception as e:
        print("Error verifying player:", e)
        return None, None, None

def main_menu():
    print("Hello, and welcome to:".center(130, " "))  # Manually set the center width to 120
    time.sleep(2)
    for i, color in zip(range(5), itertools.cycle(colors)):
        text = f"{color}The Trivia Game!{reset}"
        print(f"\r{' '}\r{text.center(140)}", end="", flush=True)
        time.sleep(2)
    print("\n")  # Ensure the last line doesn't get overwritten
    while True:
        action = input("Please choose one of the options below:\n\n\
        1. New Player Sign-in [Press N]\n\
        2. Existing Player Log-in [Press E]\n\
        3. Show Statistics [Press S]\n\
        4. Quit the Game [Press Q]\n\n").lower()
        match action:
            case 'n' | '1':
                while True:
                    username = check_to_quit(input("Please enter a username: \n"))
                    if username.isdigit():
                        print("Username must contain characters!")
                        continue
                    while True:
                        password = check_to_quit(input("Please enter a password: \n"))
                        reenter_password = check_to_quit(input("Please re-enter your Password: \n"))
                        if password != reenter_password:
                            print("Passwords mismatched. Please try again.")
                        else:
                            break
                    email = check_to_quit(input("Please enter your E-mail address: \n"))
                    try:
                        while True:
                            age = check_to_quit(int(input("Please enter your age: \n")))
                            if 0 < age <= 100:
                                break
                            else:
                                print("Age must be between 1 and 100. Please try again.")
                    except Exception as e:
                        print(f"An error occurred with: {e}. Age must be a number...")
                        sleep(2)
                        return main_menu()
                    player_id = insert_new_player(username, password, email, age)
                    if player_id:
                        print(f"Player {username} created successfully with ID:\n{player_id} ")
                        selected_topics = choose_topics(age)
                        create_player_questions_set(player_id,get_age_group(age),selected_topics)
                        player_age = age
                        start_quiz(player_id, player_age)
                    else:
                        print("Failed to create player. Please try again.")
                        sleep(2)
                        return main_menu()
            case 'e' | '2':
                username = check_to_quit(input("Please enter a username: \n"))
                password = check_to_quit(input("Please enter a password: \n"))
                player_id, unfinished_game, player_age = verify_player(username, password)
                if player_id is None:
                    print("No such player exists or invalid credentials. Returning to the main menu.")
                    sleep(2)
                    return main_menu()
                print(f"Welcome back, {username}!")
                new_or_continue = input(f"Would you like to:\n"
                                        f"\033[92m1. Start a New Game [Press 1 or N]\n"
                                        f"\033[94m2. Continue an Existing Game [Press 2 or C]\n"
                                        f"\033[95m3. Choose a Different Age Group [Press D or 3]\033[0m\n").strip().lower()
                if new_or_continue in ('1','n'):
                    topics = choose_topics(player_age)
                    create_player_questions_set(player_id, get_age_group(player_age), topics)
                    start_quiz(player_id,player_age)
                elif new_or_continue in ('2', 'c'):
                    if unfinished_game:
                        start_quiz(player_id,player_age)
                    else:
                        print("No unfinished quiz found for this player. Starting a new game:")
                        topics = choose_topics(player_age)
                        create_player_questions_set(player_id, get_age_group(player_age), topics)
                        sleep(2)
                        start_quiz(player_id,player_age)
                elif new_or_continue in ('3', 'd'):
                    try:
                        new_age = check_to_quit(int(input("Enter a new age (1-100):\n")))
                    except Exception as e:
                        print(f"An error occurred as {e}. Returning to Main Menu.")
                        return main_menu()
                    new_age_group = get_age_group(new_age)
                    topics = choose_topics(new_age)
                    create_player_questions_set(player_id, new_age_group, topics)
                    start_quiz(player_id, new_age)
                else:
                    print("Invalid choice. Returning to main menu.")
                    main_menu()
            case 's' | '3':
                present_statistics_menu()
            case 'q' | '4':
                print("Sorry to see you leave. Goodbye.")
                exit()

def start_quiz(player_id, player_age):
    """Starts the quiz using questions from the player's questions set."""
    questions = fetch_remaining_questions(player_id)
    if not questions:
        print("No remaining questions found for this player. Starting a new game.")
        topics = choose_topics(player_age)
        create_player_questions_set(player_id, get_age_group(player_age), topics)
        questions = fetch_remaining_questions(player_id)
        question_counter = 1
    else:
        question_counter = player_questions_collection.count_documents(
            {"player_id": player_id, "is_answered": True}) + 1
    for i, color in zip(range(5), itertools.cycle(colors)):
        text = f"{color}GET READY, STARTING THE QUIZ!{reset}"
        print(f"\r{' '}\r{text.center(140)}", end="", flush=True)
        time.sleep(2)
    update_starting_time(player_id)
    question_limit = 20
    while questions and question_counter <= question_limit:
        question = questions.pop(0)
        question_id = question.get('Question_No')
        print(f"\nCurrent question ID: {question_id}")
        question_structure(question_counter, question)
        valid_answers = ['a', 'b', 'c', 'd', 's', 'q']
        while True:
            selected_answer = check_to_quit(input(
                f"Please enter your answer:\nIs it \033[95m(a)\033[0m, \033[92m(b)\033[0m, \033[93m(c)\033[0m, or \033[94m(d)\033[0m? "
                f"\n\033[96mRemember you can hit [S] for statistics or [Q] to quit at any time!\033[0m\n").strip().lower(), player_id)
            if selected_answer == 's':
                choice = input("Would you like to:\n1. See current game's statistics [Press 1 or C]\n2. See other statistics [Press 2 or O]").strip().lower()
                if choice in ('1', 'c'):
                    get_mid_game_statistics(player_id)
                    question_structure(question_counter, question)
                    continue
                elif choice in ('2', 'o'):
                    present_statistics_menu()
                continue
            if selected_answer in valid_answers:
                if selected_answer == 'q':
                    quit_game(player_id)
                    return main_menu()
                elif selected_answer == question['Correct_Answer']:
                    print(f"\033[92mCorrect Answer!\033[0m")
                    update_player_answer(player_id, question_id, selected_answer)
                else:
                    print(f"\033[91mWrong Answer... Too Bad...\033[0m\n\033[94mThe Correct Answer was:\033[0m {question['Correct_Answer']}.")
                    update_player_answer(player_id, question_id, selected_answer)
                question_counter += 1
                break
        if question_counter > question_limit:
            print("You've answered all 20 questions! Well done!")
            complete_game(player_id, player_age)
            return main_menu()
    print("You've answered all the questions! Well done!")
    complete_game(player_id, player_age)
    return main_menu()

def question_structure(question_counter,question):
    """prints a question and 4 possible answers in a structured form"""
    print(f"{' ':<35}{question_counter}. {question['Question_Text']}\033[0m\n")
    sleep(2)
    print(f"\033[95m{' ':<40}{'a.'}{question['Answer_a']:<40}\033[0m", end='')  # Answer a starts after 40 spaces
    sleep(1)
    print(f"\033[92m{' b.' + question['Answer_b']}\033[0m\n")
    sleep(1)
    print(f"\033[93m{' ':<40}{'c.'} {question['Answer_c']:<40}\033[0m", end='')
    sleep(1)
    print(f"\033[94m{'d.' + question['Answer_d']}\033[0m\n")
    sleep(1)

def complete_game(player_id,player_age):
    """Completes the current game and asks the player if they want to start a new game or quit."""
    pg_cursor.execute("CALL update_high_score_table_when_quiz_finished(%s);", (player_id,))
    connection.commit()
    print("Congratulations! Game completed!")
    while True:
        new_or_quit = input(f"would you like to:\n"
                            f"\033[92m1. Play another game [Press N or 1]\033[0m\n"
                            f"\033[93m2. Maybe step up a level or get some simpler questions with another age group? [Press A or 2]\033[0m\n"
                            f"\033[94m3. Quit [Press Q or 2]\033[0m").strip().lower()
        if new_or_quit.lower() in ('n','1'):
            topics = choose_topics(player_age)
            create_player_questions_set(player_id, get_age_group(player_age), topics)
            start_quiz(player_id, player_age)
            break
        elif new_or_quit in ('a, 2'):
            new_age = check_to_quit(int(input("Enter a new age (1-100):\n")))
            new_age_group = get_age_group(new_age)
            topics = choose_topics(new_age)
            create_player_questions_set(player_id, new_age_group, topics)
            start_quiz(player_id, new_age)
        elif new_or_quit in ('q','3'):
            print(f"Returning to main menu")
            (sleep(2))
            main_menu()
            break
        else:
            print("Invalid choice. Please enter N, 1, Q, or 2.")

def quit_game (player_id):
    """Quits the game"""
    pg_cursor.execute("CALL update_session_time(%s);", (player_id,))
    connection.commit()
    print("Game session saved. You can resume later at any time")

def present_statistics_menu():
    """Presents the statistics menu"""
    user_input = input(f"Would you like to:\n1. See Your overall Statistics\n2. See Your best performance yet\
                \n3. See a player's last game's statistics\n4. Get a full list of questions a player has been asked\n5. See a list of correct answers given by a user\
                \n6. Check for all time correct answers\n7. See all time best scores\n8. See number of players so far\n9. See details for most and least answered questions\n10. See some graphs\n11. Quit ")
    if user_input == '1':
        username = check_to_quit(input("Please enter a username: \n"))
        password = check_to_quit(input("Please enter a password: \n"))
        player_id = verify_player(username, password)
        get_user_statistics(player_id[0])
    elif user_input == '2':
        username = check_to_quit(input("Please enter a username: \n"))
        password = check_to_quit(input("Please enter a password: \n"))
        player_id = verify_player(username, password)
        get_user_best_score(player_id[0])
    elif user_input == '3':
        username = check_to_quit(input("Please enter a username: \n"))
        password = check_to_quit(input("Please enter a password: \n"))
        player_id = verify_player(username, password)
        if player_id:
            get_mid_game_statistics(player_id[0])
            sleep(5)
            main_menu()
    elif user_input == '4':
        username = check_to_quit(input("Please enter a username: \n"))
        password = check_to_quit(input("Please enter a password: \n"))
        player_id = verify_player(username, password)
        if player_id:
            user_answers(player_id[0])
        else:
            print("No player found with the provided ID")
            main_menu()
    elif user_input == '5':
        username = check_to_quit(input("Please enter a username: \n"))
        password = check_to_quit(input("Please enter a password: \n"))
        player_id = verify_player(username, password)
        if player_id:
            user_correct_answers(player_id[0])
        else:
            print("No player found with the provided ID")
            main_menu()
    elif user_input == '6':
        answered_correctly_count_list()
    elif user_input == '7':
        show_high_score_table()
    elif user_input == '8':
        past_players()
    elif user_input == '9':
        most_least_answered_questions_table()
    elif user_input == '10':
        show_graphs_menu()
    elif user_input == '11' or user_input == 'q':
        user_input = 'q'
        check_to_quit(user_input)

#statistics option 1:
def get_user_statistics(player_id):
    """Retrieves and shows the user's personal statistics from all games."""
    pg_cursor.execute("SELECT * FROM show_user_statistics(%s);", (player_id,))
    connection.commit()
    results = pg_cursor.fetchall()
    headers = ["Player ID", "Username", "Questions Solved", "Started At", "Finished At", "Total Game Time", "Score"]
    column_widths = [10, 20, 20, 30, 30, 30, 10]
    formatted_results = [
        [
            row["player_id"],
            row["username"],
            row.get("questions_solved", "N/A"),
            row.get("started_at", "N/A"),
            row.get("finished_at", "N/A"),
            row.get("total_game_time", "N/A"),
            row.get("score", "N/A"),
        ]
        for row in results
    ]
    print_table(formatted_results, headers, column_widths)
    sleep(5)
    return main_menu()

#statistics option 2:
def get_user_best_score(player_id):
    """Retrieves and shows the user's personal best from all games"""
    pg_cursor.execute("SELECT * FROM show_user_best_score(%s);", (player_id,))
    result = pg_cursor.fetchone()
    if result:
        headers = ["Player ID", "Username", "Questions Solved", "Started At", "Finished At", "Total Game Time", "Score"]
        column_widths = [10, 20, 20, 30, 30, 30, 10]
        keys = ["player_id", "username", "questions_solved", "started_at", "finished_at", "total_game_time", "score"]
        formatted_result = format_results([result], keys, default="N/A")
        print_table(formatted_result, headers, column_widths)
    else:
        print("No best score found for this player.")
    sleep(5)
    return main_menu()

#statistics option 3:
def get_mid_game_statistics(player_id):
    """Retrieves and prints mid-game statistics"""
    pg_cursor.execute("SELECT  * from mid_game_statistics(%s);", (player_id,))
    results = pg_cursor.fetchall()
    headers = ["Player ID", "Username", "Answered", "Correct", "Question ID", "Question Text", "Answer", "Is Correct",
               "Elapsed Time", "Score"]
    column_widths = [10, 20, 10, 10, 12, 120, 10, 12, 15, 8]
    formatted_results = []
    for row in results:
        question_id = row[4]
        question_doc = questions_collection.find_one({"Question_No": question_id})  # Confirm MongoDB field name
        question_text = question_doc.get("Question_Text", "Unknown") if question_doc else "Unknown"
        formatted_row = [
            row[0],  # Player ID
            row[1],  # Username
            row[2],  # Answered Questions
            row[3],  # Correct Answers
            question_id,  # Question ID
            question_text,  # Question Text
            row[5],  # Selected Answer
            row[6],  # Is Correct
            row[7] or "N/A",  # Elapsed Time
            row[8] or "N/A",  # Score
        ]
        formatted_results.append(formatted_row)
    print_table(formatted_results, headers, column_widths)

#statistics option 4:
def user_answers(player_id):
    """Retrieves data from Postgres and MongoDB and presents a full list of questions answered by the player"""
    pg_cursor.execute("SELECT * FROM show_questions_for_player(%s);", (player_id,))
    connection.commit()
    results = pg_cursor.fetchall()
    headers = ["Player ID", "Player Name", "Question ID", "Question Text", "Answered Correctly"]
    column_widths = [10, 20, 11, 120, 20]
    formatted_results = []
    for row in results:
        question_id = row["question_id"]
        question_doc = questions_collection.find_one({"Question_No": question_id})
        question_text = question_doc.get("Question_Text", "N/A") if question_doc else "N/A"
        formatted_results.append([
            row["player_id"],
            row["player_name"],
            question_id,
            question_text,
            "Correct" if row["is_correct"] else "Incorrect"
        ])
    print(f"\n\033[92mQuestions Answered By Player {player_id}:\033[0m\n")
    print_table(formatted_results, headers, column_widths)
    sleep(5)
    main_menu()

#statistics option 5:
def user_correct_answers(player_id):
    """Retrieves data from Postgres and MongoDB and presents a table of correct answers given by the player"""
    pg_cursor.execute("SELECT * from correct_answers_by_player(%s);",(player_id,))
    connection.commit()
    results = pg_cursor.fetchall()
    headers = ["Player ID", "Player Name", "Question ID", "Question Text", "Total Correct Answers"]
    column_widths = [10, 30, 11, 120, 21]
    formatted_results = []
    for row in results:
        question_id = row["question_id"]
        question_doc = questions_collection.find_one({"Question_No": question_id})
        question_text = question_doc.get("Question_Text", "N/A") if question_doc else "N/A"
        formatted_results.append([
            row["player_id"],
            row["player_name"],
            question_id,
            question_text,
            row["total_correct_answers"]
        ])
    print(f"\n\033[92mCorrect Answers By Player {player_id}:\033[0m\n")
    print_table(formatted_results, headers, column_widths)
    sleep(5)
    main_menu()

#statistics option 6:
def answered_correctly_count_list():
    """Retrieves data from Postgres and MongoDB and presents a table of correct answers answered by all users, from most to least"""
    pg_cursor.execute("SELECT * FROM players_list_by_correct_answers();")
    connection.commit()
    results = pg_cursor.fetchall()
    headers = ["Player ID", "Player Name", "Total Correct Answers"]
    column_widths = [20, 30, 25]
    keys = ["player_id", "player_name", "total_correct_answers"]
    formatted_results = format_results(results, keys)
    print("\n\033[92mCorrectly Answered Questions By Players:\033[0m\n")
    print_table(formatted_results, headers, column_widths)
    sleep(5)
    main_menu()

# statistics option 7:
def show_high_score_table():
    """Shows the 'high_score' table"""
    pg_cursor.execute("SELECT * FROM show_high_score_table();")
    connection.commit()
    results = pg_cursor.fetchall()
    headers = ["Player ID", "Username", "Questions Solved", "Started At", "Finished At", "Total Game Time", "Score"]
    column_widths = [10, 20, 20, 30, 30, 30, 10]
    keys = ["player_id", "username", "questions_solved", "started_at", "finished_at", "total_game_time", "score"]
    formatted_results = format_results(results, keys)
    print_table(formatted_results, headers, column_widths)
    sleep(5)
    main_menu()

#statistics option 8:
def past_players():
    """Retrieves data from postgres and sends it to be printed as a table of past players"""
    pg_cursor.execute("SELECT * FROM past_players_list();")
    connection.commit()
    results = pg_cursor.fetchall()
    headers = ["Player ID", "Username", "Age", "Email", "Registration Date", "Total Players"]
    column_widths = [10, 20, 10, 30, 26, 15]
    keys = ["player_id", "username", "age", "email", "registration_date", "total_players"]
    formatted_results = format_results(results, keys)
    print_table(formatted_results, headers, column_widths)
    sleep(5)
    main_menu()
    sleep(5)
    return main_menu()

#statistics option 9:
def most_least_answered_questions_table():
    """Retrieves data from PostgreSQL and MongoDB, printing tables for most and least answered questions with colors by age group."""
    headers = ["Age Group", "Topic", "Question ID", "Question Text", "Correct", "Incorrect", "Total"]
    column_widths = [10, 30, 11, 120, 10, 10, 10]
    pg_cursor.execute("SELECT * FROM most_least_answered_questions()")
    results = pg_cursor.fetchall()
    formatted_results = []
    row_colors = []
    for row in results:
        question_id, total_answered, total_correct, total_incorrect = row[:4]
        question_doc = questions_collection.find_one({"Question_No": question_id})
        age_group = question_doc.get("Age_Group", "N/A")
        topic = question_doc.get("Topic", "N/A")
        question_text = question_doc.get("Question_Text", "N/A")
        colors = {
            "1-5": "\033[92m",  # Green
            "5-10": "\033[94m",  # Blue
            "10-15": "\033[95m",  # Magenta
            "15-20": "\033[93m",  # Yellow
            "20-30": "\033[96m",  # Cyan
            "30-40": "\033[91m",  # Red
            "40-100": "\033[90m",  # Gray
        }
        row_colors.append(colors.get(age_group, "\033[0m"))
        formatted_results.append([
            age_group,
            topic,
            question_id,
            question_text,
            total_correct,
            total_incorrect,
            total_answered,
        ])
    print_table(formatted_results, headers, column_widths, row_colors)
    sleep(5)
    main_menu()

def check_to_quit(user_input, player_id = None):
    if user_input == 'q':
        if player_id:
            quit_game(player_id)
        return main_menu()
    return user_input

def show_graphs_menu():
    print(f"\n\033[4mStatistics graphs menu:\033[0m\n")
    user_input = input("Please choose one of the following:\n1. See a single player's pie chart for correct and incorrect answers\
    \n2. See a dispersion of players ages across all games played\n3. See a dispersion of topics chosen by players for a certain age group\
    \n4. Return to the main menu\n").strip()
    match user_input:
        case '1':
            while True:
                username = check_to_quit(input("Please enter a username: \n"))
                if username.isdigit():
                    print("Username must contain characters!")
                    show_graphs_menu()
                password = check_to_quit(input("Please enter a password: \n"))
                player_id,_,_ = verify_player(username, password)
                player_success_pie(player_id)
                sleep(2)
                main_menu()
        case '2':
            generate_ages_column_chart()
            main_menu()
        case '3':
            try:
                selected_age_group = get_age_group(input("Please Enter Age: "))
                if not selected_age_group:
                    print("Invalid age group. Returning to menu.")
                    return main_menu()
                get_answered_topic_dispersion_for_age_group(selected_age_group)
            except Exception as e:
                print(f"An error occurred: {e}.")
                sleep(2)
                return main_menu()

        case '4' | 'q':
            sleep(2)
            main_menu()
        case _:
            print("Invalid Choice")

#statistics graphs:
def player_success_pie(player_id):
    """Counts the number of 20-question sets prepared for a player and plots a pie chart with actual numbers and percentages."""
    total_questions = player_questions_collection.count_documents({"player_id": player_id})
    if total_questions == 0:
        print("No questions found for this player. Cannot generate pie chart.")
        return
    pg_cursor.execute("select * from player_answers_graph(%s)", (player_id,))
    result = pg_cursor.fetchone()
    if not result:
        print(f"No answer data found for player ID {player_id}. Cannot generate pie chart.")
        return
    correct = result[0]
    incorrect = result[1]
    unanswered = total_questions - (correct + incorrect)
    if correct + incorrect + unanswered == 0:
        print("No data available for correct, incorrect, or unanswered questions. Pie chart cannot be displayed.")
        return
    if unanswered > 0:
        labels = ['Correct', 'Wrong', 'Not Answered']
        colors = ['yellowgreen', 'red', 'gold']
        sizes = [correct, incorrect, unanswered]
        explode = (0.06, 0.06, 0.06)
    else:
        labels = ['Correct', 'Wrong']
        colors = ['yellowgreen', 'red']
        sizes = [correct, incorrect]
        explode = (0.1, 0.1)
    def autopct_format(pct, sizes):
        total = sum(sizes)
        absolute = int(round(pct * total / 100.0))
        return f"{pct:.1f}% \n({absolute})"
    fig, ax = plt.subplots()
    ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct=lambda pct: autopct_format(pct, sizes),
        shadow=True,
        startangle=90,
    )
    ax.axis('equal')
    ax.set_title(f"Distribution of Answers for Player ID {player_id}")
    plt.show()

def generate_ages_column_chart():
    """Generates a column chart showing the dispersion of questions asked across different ages."""
    pg_cursor.execute("select * from ages_dispersion()")
    results = pg_cursor.fetchone()
    ages = {"1-5" : results[0],
            "5-10" : results[1],
            "10-15" : results[2],
            "15-20" :results[3],
            "20-30" : results[4],
            "30-40" : results[5],
            "40-100" :results[6]}
    fig, ax = plt.subplots()
    bars = ax.bar(ages.keys(), ages.values(), color='skyblue')
    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            yval + 0.5,
            f"{yval}",
            ha='center',
            va='bottom',
            fontsize=10,
            color='black'
        )
    ax.set_xlabel("Age groups")
    ax.set_ylabel("Number of questions")
    ax.set_title("Number of Questions Asked for Each Age Group")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def get_answered_topic_dispersion_for_age_group(age_group):
    """Fetches the dispersion of answered questions for a specific age group and displays it in a column graph."""
    try:
        query = "SELECT * FROM topic_dispersion_for_age_group(%s);"
        pg_cursor.execute(query, (age_group,))
        results = pg_cursor.fetchall()
        if not results:
            print(f"No answered questions found for the age group: {age_group}")
            return
        topics = [row["topic"] for row in results]
        counts = [row["answered_question_count"] for row in results]
        plt.figure(figsize=(10, 6))
        bars = plt.bar(topics, counts, color='skyblue')
        for bar in bars:
            yval = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                yval + 0.5,
                f"{yval}",
                ha='center',
                va='bottom',
                fontsize=10,
                color='black'
            )
        plt.xlabel("Topics", fontsize=12)
        plt.ylabel("Answered Question Count", fontsize=12)
        plt.title(f"Answered Questions Dispersion for Age Group {age_group}", fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"An error occurred while fetching answered topic dispersion: {e}")
    main_menu()

def insert_new_player(username, password, email, age):
    """Inserting a record for a new player in the PostgreSQL database upon registering"""
    while True:
        try:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
            new_player_query = """
            SELECT * FROM new_player(%s, %s, %s, %s);
            """
            pg_cursor.execute(new_player_query, (username, hashed_password, email, age))
            result = pg_cursor.fetchone()
            if result:
                player_id = result[0]
                connection.commit()
                return player_id
        except psycopg2.Error as e:
            connection.rollback()
            error_message = str(e)
            print(f"An error occurred: {error_message}")
            while True:
                if 'username' in error_message:
                    new_username = input("This username already exists. Please enter a new one:")
                    if new_username != username:
                        return new_username
                elif 'password' in error_message:
                    password = input("This password already exists. Please enter a new one:")
                elif 'email' in error_message:
                    email = input("This email already exists. Please enter a new one:")
                else:
                    print("An unexpected error occurred", e)
                    return None

def choose_topics(age):
    """Lets the user choose 3 topics to be asked about, according to his age"""
    age_topics = {
        (1,6): ["Animals", "Colours", "Food and Drinks", "Games", "Weather"],
        (6,11): ["Animals", "Math and Numbers", "Games", "Science", "Food and Drinks", "Anatomy", "Music", "Geography", "History", "Movies and TV Shows", "Nature", "Weather"],
        (11,16): ["Science", "Geography", "History", "Music", "Movies and TV Shows", "Literature and Books", "Health and Fitness", "Technology", "Arts and Crafts"],
        (16,21): ["Pop Culture", "Politics", "Travel", "Science", "History", "Health and Fitness", "Sports", "Technology", "Social Issues"],
        (21,31): ["Politics", "Technology", "Current Events", "Finance and Economics", "Health", "Arts and Culture", "Music", "Movies and TV Shows", "Travel and Landmarks"],
        (31,41): ["Family and Relationships", "Career and Work-Life Balance", "Home and Lifestyle", "Health and Fitness", "Travel", "Finance and Economics"],
        (41,101): ["History", "Health and Wellness", "Culture and Arts", "Travel", "Current Events"]
    }
    topics = next(value for key, value in age_topics.items() if key[0] <= age <key[1])
    print("Please Choose 3 of the following topics:")
    for idx, topic in enumerate(topics, start=1):
        print(f"\033[95m{idx}. {topic}{' ':<50}\033[96m")
    selected_topics = []
    while len(selected_topics) < 3:
        choice = input(f"\033[94mEnter Your Topics (You can either choose by topic or by number):").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(topics):
            topic = topics[int(choice)-1]
        else:
            topic = next((t for t in topics if t.lower() == choice.lower()),None)
        if topic and topic not in selected_topics:
            selected_topics.append(topic)
        else:
            print("Invalid Choice... Please try again")
        if choice in topics and choice not in selected_topics:
            selected_topics.append(choice)
    print(f"OK, You've selected the following topics:\n{selected_topics}")
    return selected_topics

def update_starting_time(player_id):
    """Updates the quiz's starting time in the high_scores table."""
    query = "CALL update_high_score_table_start_time(%s);"
    try:
        pg_cursor.execute(query, (player_id,))
        connection.commit()
    except Exception as e:
        print(f"Error updating starting time: {e}")
        connection.rollback()

if __name__ == "__main__":
    main_menu()

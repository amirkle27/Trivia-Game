

# pip install matplotlib !!!

import matplotlib.pyplot as plt
import numpy as np

# Data
labels = ['Correct', 'Wrong', 'Not Answered']
sizes = [25, 35, 20]
colors = ['yellowgreen', 'red', 'gold']
explode = (0.1, 0, 0)  # To "explode" the first slice

# Create a pie chart
fig, ax = plt.subplots()
ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
       shadow=True, startangle=90)

# Equal aspect ratio ensures that the pie chart is drawn as a circle.
ax.axis('equal')

# Add a headline
ax.set_title("Distribution of Answers")

# Show the plot
plt.show()
##############################################
import time
import itertools
from time import sleep

import psycopg2
import psycopg2.extras
from dns.e164 import query
from pymongo import MongoClient
import bcrypt
connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="admin",
        port="5432"
    )
pg_cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client["trivia_game"]
player_questions_collection = mongo_db['player_questions']

colors = [
        "\033[91m",  # Red
        "\033[92m",  # Green
        "\033[93m",  # Yellow
        "\033[94m",  # Blue
        "\033[95m",  # Magenta
        "\033[96m",  # Cyan
    ]
reset = "\033[0m"  # Reset color to default

# Procedure to insert a new player

def insert_new_player(username, password, email, age):
    """Inserting a record for a new player in the PostgreSQL database upon registering"""
    while True:
        try:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

            # Use SELECT to call the function and retrieve the OUT parameter
            new_player_query = """
            SELECT * FROM new_player(%s, %s, %s, %s);
            """

            pg_cursor.execute(new_player_query, (username, hashed_password, email, age))

            result = pg_cursor.fetchone()
            print(f"Fetch result: {result}")  # Debugging line to see the fetch result

            if result:
                player_id = result[0]  # This assumes the first element is the player_id (OUT parameter)
                connection.commit()
                return player_id
                # else:
                # print("No player ID was returned.")
                # return None
        except psycopg2.Error as e:
            connection.rollback()
            error_message = str(e)

            print(f"An error occurred: {error_message}")
            if 'username' in error_message:
                username = input("This username already exists. Please enter a new one:")
            elif 'password' in error_message:
                password = input("This password already exists. Please enter a new one:")
            elif 'email' in error_message:
                email = input("This email already exists. Please enter a new one:")
            else:
                print("An unexpected error occurred", e)
                return None



# Fetch and store 20 questions for a player in MongoDB
def fetch_and_store_questions(player_id, pg_cursor, mongo_collection):
    """Fetching 20 random questions generated in postgreSQL and storing them at the MongoDB question bank
     for later use."""
    try:
        # Clear any existing questions for the player
        mongo_collection.delete_many({"player_id": player_id})
        # Call the new PostgreSQL function to fetch 20 random questions
        pg_cursor.execute("SELECT * FROM get_random_questions();")
        questions = pg_cursor.fetchall()

        # Store questions in MongoDB
        questions_to_store = [
            {
                "player_id": player_id,
                "question_id": question['question_id'],
                "question_text": question['question_text'],
                "answer_a": question['answer_a'],
                "answer_b": question['answer_b'],
                "answer_c": question['answer_c'],
                "answer_d": question['answer_d'],
                "correct_answer": question['correct_answer'],
            }
            for question in questions
        ]
        mongo_collection.insert_many(questions_to_store)
        print(f"Questions stored in MongoDB for player_id: {player_id}")
    except Exception as e:
        print("An error occurred while fetching and storing questions:", e)


def verify_player (username,password):
    """Verify if a returning player exists in PostgreSQL with an unfinished game."""
    try:
        pg_cursor.execute("SELECT player_id, password FROM players WHERE username = %s", (username,))
        result = pg_cursor.fetchone()
        if result and bcrypt.checkpw(password.encode(), result['password'].encode()):
            print(f"Welcome back, {username}!")
            player_id = result['player_id']
            # Check if the game is unfinished by counting answers
            pg_cursor.execute("SELECT COUNT(*) FROM player_answers WHERE player_id = %s", (player_id,))
            questions_answered = pg_cursor.fetchone()[0]

            unfinished_game = questions_answered < 20
            return player_id, unfinished_game
        else:
            print("Invalid login or finished game.")
            return None, False
    except Exception as e:
        print("Error verifying player:", e)
        return None, False

def fetch_remaining_questions (player_id, mongo_collection):
    """Fetch the remaining questions for a returning player from MongoDB."""
    remaining_questions = mongo_collection.find ({"player_id":player_id})
    return list(remaining_questions)

def update_player_answer (player_id,question_id,selected_answer):
    """Sends the player and question/answer info back to PostgreSQL to store in the player_answers table for later statistics use"""
    try:
        query = "CALL update_player_answers (%s,%s,%s)"
        pg_cursor.execute(query,(player_id,question_id,selected_answer))
        connection.commit()
    except Exception as e:
        print(f"An Error occurred while updating player answers: {e}")
        connection.rollback()



def start_quiz(player_id):
    """Loops through the questions stored in MongoDB,
     ask each one and delete it from the questions bank after receiving an answer """
    query = "CALL update_high_score_table_start_time(%s);"
    pg_cursor.execute(query,(player_id,))
    connection.commit()
    for i, color in zip(range(5), itertools.cycle(colors)):
        text = f"{color}GET READY, STARTING THE QUIZ!{reset}"
        print(f"\r{' '}\r{text.center(140)}", end="", flush=True)
        time.sleep(2)
    while True:
        question = player_questions_collection.find_one({"player_id":player_id})

        if not question:
            print("You've answered all the questions! Well done!")
            query = "CALL update_high_score_table_finish_time(%s);"
            pg_cursor.execute(query, (player_id,))
            connection.commit()
            return main_menu()
        else:
            question_id = question['question_id']
            print("\n")
            print(f"{' ':<50}{question['question_text']}\033[0m\n")  # Reset color to white for the question text
            sleep(2)
            print(f"\033[95m{' ':<40}{'a.'}{question['answer_a']:<40}\033[0m", end='')  # Answer a starts after 40 spaces
            sleep(1)
            print(f"\033[92m{' b.' + question['answer_b']}\033[0m\n")  # Answer b starts after 60 spaces
            sleep(1)
            print(f"\033[93m{' ':<40}{'c.'} {question['answer_c']:<40}\033[0m", end='')  # Answer c starts after 40 spaces
            sleep(1)
            print(f"\033[94m{'d.' + question['answer_d']}\033[0m\n")
            (sleep(1))
            selected_answer = check_to_quit(input(
                f"Please enter your answer:\nIs it \033[95m(a)\033[0m, \033[92m(b)\033[0m, \033[93m(c)\033[0m, or \033[94m(d)\033[0m? \n\033[96mRemember you can hit [Q] at any time to quit!\033[0m\n").lower(), player_id)
            if not selected_answer == 'q':
                update_player_answer(player_id, question_id, selected_answer)
                delete = player_questions_collection.delete_one({"_id": question['_id']})
                # Call this function after each answer is processed and the question is deleted
                print_remaining_questions(player_id)

            if delete.deleted_count == 1:
                print(f"Question {question['_id']} deleted successfully.")
            else:
                print(f"Failed to delete question {question['_id']}.")

            if selected_answer == question['correct_answer']:
                print("Correct Answer!")
            else:
                print(f"Wrong Answer... Too Bad...\nThe Correct Answer was: {question['correct_answer']}.")

def update_highscore (player_id):
    query = "CALL update_high_score_table(%s)"
    pg_cursor.execute(query,(player_id,))
    connection.commit()



    # Check and process new entries from new_player_log
    # while True:
    #     pg_cursor.execute("SELECT * FROM new_player_log;")
    #     new_entries = pg_cursor.fetchall()
    #
    #     for entry in new_entries:
    #         player_id = entry['player_id']
    #         fetch_and_store_questions(player_id, pg_cursor, player_questions_collection)
    #         pg_cursor.execute("DELETE FROM new_player_log WHERE player_id = %s;", (player_id,))
    #         connection.commit()


# finally:
#     # Close PostgreSQL connection
#     if pg_cursor:
#         pg_cursor.close()
#     if connection:
#         connection.close()
#     print("t")
#     # Fetch and print all documents in MongoDB collection
#     questions = player_questions_collection.find()
#     for question in questions:
#         print(question)
#
#     # Close MongoDB connection
#     if mongo_client:
#         mongo_client.close()



# Function to check a password
# def check_password(username, password,email,age):
#     # Retrieve the hashed password from the database
#     pg_cursor.execute("SELECT hashed_password FROM users WHERE username = %s", (username,))
#     result = pg_cursor.fetchone()
#
#     if result:
#         hashed_password_from_db = result[0]
#         # Compare the provided password with the stored hash
#         if bcrypt.checkpw(password.encode(), hashed_password_from_db.encode()):
#             print("Password is correct!")
#         else:
#             print("Incorrect password!")
#     else:
#         print("Username not found.")
#
#
# # Example usage
#   # Creating a new user
# check_password('user1', 'my_password1')  # Verifying the password
#
# # Close connection
# pg_cursor.close()
# connection.close()

def check_to_quit(user_input, player_id = None):
    if user_input == 'q':
        if player_id:
            quit_game(player_id)

        return main_menu()
    return user_input

def quit_game (player_id):
    pg_cursor.execute("CALL update_session_time(%s);", (player_id,))
    connection.commit()
    print("Game session saved. You can resume later at any time")

def complete_game(player_id):
    pg_cursor.execute("CALL update_high_score_table_finish_time(%s);", (player_id,))
    connection.commit()
    print("Congratulations! Game completed!")
def main_menu():
    print("Hello, and welcome to:".center(130, " "))  # Manually set the center width to 120
    time.sleep(2)

    # Limit to 10 cycles, for example
    for i, color in zip(range(5), itertools.cycle(colors)):
        text = f"{color}The Trivia Game!{reset}"
        print(f"\r{' '}\r{text.center(140)}", end="", flush=True)
        time.sleep(2)
    print("\n")  # Ensure the last line doesn't get overwritten


    action = input("Please choose one of the options below:\n\n\
    1. New Player Sign-in [Press N]\n\
    2. Existing Player Log-in [Press E]\n\
    3. Show Statistics [Press S]\n\
    4. Quit the Game [Press Q]\n\n").lower()
    match action:
        case 'n':
            while True:
                username = check_to_quit(input("Please enter a username: \n"))
                password = check_to_quit(input("Please enter a password: \n"))
                reenter_password = check_to_quit(input("Please re-enter your Password: \n"))
                email = check_to_quit(input("Please enter your E-mail address: \n"))
                age= check_to_quit(int(input("Please enter your age: \n")))
                if password != reenter_password:
                    again_or_quit = input("Passwords mismatch. Please try again or press [q] to go back to main menu")
                    if again_or_quit == 'q':
                        return main_menu()
                    else:
                        continue
                if password == reenter_password:
                    player_id = insert_new_player(username, password, email, age)
                    if player_id:
                        print(f"Player {username} created successfully with ID:\n{player_id} ")
                        fetch_and_store_questions(player_id, pg_cursor, player_questions_collection)
                        start_quiz(player_id)
                    else:
                        print("Failed to create player. Please try again.")
                        return main_menu()
                # else:
                #     print("Passwords do not match. Please try again.")
                #     main_menu()
        case 'e':
            username = check_to_quit(input("Please enter a username: \n"))
            password = check_to_quit(input("Please enter a password: \n"))
            player_id, unfinished_game = verify_player(username,password)
            if player_id:
                if unfinished_game:
                    questions = fetch_remaining_questions(player_id, player_questions_collection)
                    start_quiz(player_id)
                else:
                    complete_game(player_id)
                    print("It looks like you've completed the quiz. Let's start a new game!")
                    fetch_remaining_questions(player_id,pg_cursor,player_questions_collection)
                    start_quiz(player_id)
            else:
                print("Invalid login or finished game. Please try again")




        case 's':
            print("HAVENT WRITTEN THIS BIT FOR STATISTICS!")
        case 'q':
            print("Sorry to see you leave. Goodbye.")
            exit()


def print_remaining_questions(player_id):
    remaining_questions = player_questions_collection.find({"player_id": player_id})
    print("\nRemaining questions:")
    for question in remaining_questions:
        print(f"Question: {question['question_text']}, Correct Answer: {question['correct_answer']}")







main_menu()

import time
import itertools
from time import sleep

import psycopg2
import psycopg2.extras
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
        else:
            print("No player ID was returned.")
            return None

    except Exception as e:
        connection.rollback()
        print("An error occurred:", e)
        return None



# Fetch and store 20 questions for a player in MongoDB
def fetch_and_store_questions(player_id, pg_cursor, mongo_collection):
    """Fetching 20 random questions generated in postgreSQL and storing them at the mongoDB question bank
     for later use"""
    try:
        questions_query = """
            SELECT question_id, question_text, answer_a, answer_b, answer_c, answer_d, correct_answer
            FROM questions
            ORDER BY RANDOM()
            LIMIT 20;
            """
        pg_cursor.execute(questions_query)
        questions = pg_cursor.fetchall()

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

def start_quiz(player_id):
    """Loops through the questions stored in MongoDB,
     ask each one and delete it from the questions bank after receiving an answer """


    while True:
        question = player_questions_collection.find_one({"player_id":player_id})

        if not question:
            print("You've answered all the questions! Well done!")
            break;
        else:
            for i, color in zip(range(5), itertools.cycle(colors)):
                text = f"{color}GET READY, STARTING THE QUIZ!{reset}"
                print(f"\r{' '}\r{text.center(130)}", end="", flush=True)
                time.sleep(2)


                print("\n")
                print(f"\n{question['question_text']}\033[0m\n")  # Reset color to white for the question text
                sleep(2)
                print(f"\033[95ma. {question['answer_a']}\033[0m", end='')  # Apply color for option a and reset after
                sleep(1)
                print(f"\033[92mb. {question['answer_b']:>30}\033[0m\n")  # Apply color for option b and reset after
                sleep(1)
                print(f"\033[93mc. {question['answer_c']}\033[0m", end='')  # Apply color for option c and reset after
                sleep(1)
                print(f"\033[94md. {question['answer_d']:>30}\033[0m\n")  # Apply color for option d and reset after
                (sleep(1))
                answer = input(f"Please enter your answer:\nIs it \033[95m(a)\033[0m, \033[92m(b)\033[0m, \033[93m(c)\033[0m, or \033[94m(d)\033[0m? \n").lower()

                if answer == question['correct_answer']:
                    print("Correct Answer!")
                else:
                    print(f"Wrong Answer... Too Bad...\nThe Correct Answer was: {question['correct_answer']}.")
                player_questions_collection.delete_one({"_id": question['_id']})



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




def main_menu():
    print("Hello, and welcome to:".center(120, " "))  # Manually set the center width to 120
    time.sleep(2)

    # Limit to 10 cycles, for example
    for i, color in zip(range(5), itertools.cycle(colors)):
        text = f"{color}The Trivia Game!{reset}"
        print(f"\r{' '}\r{text.center(130)}", end="", flush=True)
        time.sleep(2)
    print("\n")  # Ensure the last line doesn't get overwritten


    action = input("Please choose one of the options below:\n\n\
    1. New Player Sign-in [Press N]\n\
    2. Existing Player Log-in [Press E]\n\
    3. Show Statistics [Press S]\n\
    4. Quit the Game [Press Q]\n\n").lower()
    match action:
        case 'n':
            username = input("Please enter a username: \n")
            password = input("Please enter a password: \n")
            reenter_password = input("Please re-enter your Password: \n")
            email = input("Please enter your E-mail address: \n")
            age= int(input("Please enter your age: \n"))

            if password == reenter_password:
                player_id = insert_new_player(username, password, email, age)
                if player_id:
                    print(f"Player {username} created successfully with ID:\n{player_id} ")
                    fetch_and_store_questions(player_id, pg_cursor, player_questions_collection)
                    start_quiz(player_id)
                else:
                    print("Failed to create player. Please try again.")
            else:
                print("Passwords do not match. Please try again.")
        case 'e':
            print("HAVENT WRITTEN THIS BIT FOR EXISTING PLAYER!")
        case 's':
            print("HAVENT WRITTEN THIS BIT FOR STATISTICS!")
        case 'q':
            print("Sorry to see you leave. Goodbye.")
            exit()



main_menu()

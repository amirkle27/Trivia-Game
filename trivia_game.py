import time
import psycopg2
import psycopg2.extras
from pymongo import MongoClient

# Connect to PostgreSQL
try:
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

    # Procedure to insert a new player
    def insert_new_player(username, password, email, age):
        new_player_query = f"""
        CALL new_player('{username}', '{password}', '{email}', {age});
        """
        pg_cursor.execute(new_player_query)
        connection.commit()

    # Insert sample players
    insert_new_player('shimon', 'MeNashE', 'shimonmenashe@gmail.com', 47)
    insert_new_player('amirkle27', 'ItsAniceTrivia100', 'amirkle@gmail.com', 41)
    insert_new_player('guy', 'WhyDoINeedAPasswordForASimpleTriviaGame', 'guy@gmail.com', 39)

    # Fetch and store 20 questions for a player in MongoDB
    def fetch_and_store_questions(player_id, pg_cursor, mongo_collection):
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
                "correct_answer": question['correct_answer']
            }
            for question in questions
        ]

        mongo_collection.insert_many(questions_to_store)
        print(f"Questions stored in MongoDB for player_id: {player_id}")

    # Check and process new entries from new_player_log
    while True:
        pg_cursor.execute("SELECT * FROM new_player_log;")
        new_entries = pg_cursor.fetchall()

        for entry in new_entries:
            player_id = entry['player_id']
            fetch_and_store_questions(player_id, pg_cursor, player_questions_collection)
            pg_cursor.execute("DELETE FROM new_player_log WHERE player_id = %s;", (player_id,))
            connection.commit()



except Exception as e:
    print("An error occurred:", e)

finally:
    # Close PostgreSQL connection
    if pg_cursor:
        pg_cursor.close()
    if connection:
        connection.close()
    print("t")
    # Fetch and print all documents in MongoDB collection
    questions = player_questions_collection.find()
    for question in questions:
        print(question)

    # Close MongoDB connection
    if mongo_client:
        mongo_client.close()

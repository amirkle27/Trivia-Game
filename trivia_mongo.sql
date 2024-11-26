db.createCollection("pleayer_qestions")
db.player_questions.deleteMany({})
db.questions.find()

db.questions.updateMany(

    { $rename: { "1-5": "Age_Group" }},
    { $rename: { "5-10": "Age_Group" }},
    { $rename: { "10-15": "Age_Group" }},
    { $rename: { "15-20": "Age_Group" }},
    { $rename: { "20-30": "Age_Group" }},
    { $rename: { "30-40": "Age_Group" }},
    { $rename: { "40-100": "Age_Group" }}
)

//most_answered_questions =
//for most answered questions:
db.questions.aggregate([
    {"$group": {
        "_id": {"age_group": "$age_group", "topic": "$topic"},
        "question": {"$first": "$question_text"},
        "question_id": {"$first": "$Question_No"},
        "total_answered_times": {"$max": "$answered_count"}
    }},
    {"$sort": {"total_answered_times": -1}}
])

//for least answered questions:

db.questions.aggregate([
    {"$group": {
        "_id": {"age_group": "$age_group", "topic": "$topic"},
        "question": {"$first": "$question_text"},
        "question_id": {"$first": "$Question_No"},
        "total_answered_times": {"$min": "$answered_count"}
    }},
    {"$sort": {"total_answered_times": 1}}
])


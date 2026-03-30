from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = "mongodb://localhost:27017/taskdb"
mongo = PyMongo(app)

# ➕ Add Task (with duplicate check)
@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    print("DATA RECEIVED:", data)

    # 🔥 Prevent duplicate
    existing = mongo.db.tasks.find_one({"title": data["title"]})
    if existing:
        return jsonify({"msg": "Task already exists"})

    mongo.db.tasks.insert_one({
        "title": data["title"],
        "status": data.get("status", "Pending")
    })

    return jsonify({"msg": "Task Added"})


# 📥 Get Tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = list(mongo.db.tasks.find({}, {"_id": 0}))
    return jsonify({"tasks": tasks})


# ❌ Delete Task
@app.route("/tasks/<title>", methods=["DELETE"])
def delete_task(title):
    mongo.db.tasks.delete_one({"title": title})
    return jsonify({"msg": "Deleted"})


# 🔄 Toggle Task Status (IMPORTANT FIX)
@app.route("/tasks/<title>", methods=["PUT"])
def update_task(title):
    task = mongo.db.tasks.find_one({"title": title})

    if not task:
        return jsonify({"msg": "Task not found"})

    # 🔥 Toggle logic
    new_status = "Completed" if task["status"] == "Pending" else "Pending"

    mongo.db.tasks.update_one(
        {"title": title},
        {"$set": {"status": new_status}}
    )

    return jsonify({"msg": "Updated", "status": new_status})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
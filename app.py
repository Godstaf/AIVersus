from flask import Flask, render_template, request, jsonify, session
from google import genai
import mysql.connector as my
import hashlib
import os
import pymongo
from bson import ObjectId

uri = 'mongodb://localhost:27017'
client = pymongo.MongoClient(uri)
db = client["AIVersus"]
collection = db["ChatHistory"]

# checking if mongodb connection is established
try:
    client.admin.command('ping')
    print("MongoDB connection established.")
except Exception as e:
    print("MongoDB connection failed:", e)
    exit(0)


app = Flask(__name__)
app.secret_key = str(os.urandom(24))  # Generate a random secret key for session management


# Connect to MySQL database
pwrd = "krish113838G"


try:
    mycon = my.connect(host='localhost',
                       user='root',
                       password=pwrd)

except:
    print("Wrong password!")
    exit(0)

if not mycon.is_connected():
    print("Not able to connect to the server at this movement")
    exit(0)
    
else:
    print("Connected")

cr = mycon.cursor()
cr.execute("CREATE DATABASE IF NOT EXISTS AIVersus")
cr.execute("USE AIVersus")

@app.route("/")
def index():
    return render_template("index.html")



@app.route("/new_chat", methods=["POST"])
def new_chat():
    email = session.get("userEmail")
    if not email:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    collection.insert_one({
        "email": email,
        "queries": [],
        "responses": []
    })
    chat_doc = collection.find_one({"email": email}, sort=[("_id", -1)])
    if chat_doc is not None:
        session["chat_id"] = str(chat_doc["_id"])
        return jsonify({"status": "success", "message": "New chat created", "chat_id": str(chat_doc["_id"])}), 200
    else:
        session["chat_id"] = None
        return jsonify({"status": "error", "message": "Failed to create chat"}), 500



@app.route("/get_all_chats", methods=["GET"])
def get_all_chats():
    email = session.get("userEmail")
    if not email:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    # Fetch all chat history for the user from MongoDB
    user_docs = list(collection.find({"email": email}))  # Convert cursor to list
    if user_docs:
        return jsonify({
            "status": "success",
            "chats": [{
                "chat_id": str(doc["_id"]),
                "queries": doc.get("queries", []),
                "responses": doc.get("responses", [])
            } for doc in user_docs]
        }), 200
    else:
        return jsonify({"status": "error", "message": "No chat history found"}), 404



@app.route("/get_chat_history", methods=["GET"])
def get_chat_history():
    email = session.get("userEmail")
    chat_id = request.args.get("chat_id")  # Get chat_id from query params
    if not email:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    if chat_id:
        session["chat_id"] = chat_id  # Set the current chat_id in session

    user_doc = list(collection.find({"email": email}))
    chatIdIndx = None

    if user_doc:
        for i in range(len(user_doc)-1, -1, -1):
            if str(user_doc[i].get("_id")) == session.get("chat_id"):
                chatIdIndx = i
                break

        if chatIdIndx is not None:
            return jsonify({
                "status": "success",
                "queries": user_doc[chatIdIndx].get("queries", []),
                "responses": user_doc[chatIdIndx].get("responses", [])
            }), 200
        else:
            return jsonify({"status": "error", "message": "No chat history found for this chat ID"}), 404
    else:
        return jsonify({"status": "error", "message": "No chat history found"}), 404
    
    

@app.route("/delete_empty_chats", methods=["POST"])
def delete_empty_chats():
    email = session.get("userEmail")
    if not email:
        return jsonify({"status": "error", "message": "User not logged in"}), 401  
    # Delete all chats for the user that have no queries or responses
    result = collection.delete_many({
        "email": email,
        "$or": [
            {"queries": {"$size": 0}},
            {"responses": {"$size": 0}}
        ]
    })
    return jsonify({"status": "success", "message": f"{result.deleted_count} empty chats deleted."}), 200



@app.route("/register", methods=["POST", "GET"])
def register_page():
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login_page():
    return render_template("login.html")


@app.route("/query", methods=["POST"])
def query_page():
    qry = request.form.get("Query")
    email = session.get("userEmail")
    chat_id = session.get("chat_id")  # Get current chat_id from session

    client = genai.Client(api_key="AIzaSyDLtRhhQTS05XcusmCaYX0m-NHEJK_Wq88")
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=[qry]
    )
    
    if email is not None and chat_id is not None:
        # Update the correct chat document by _id
        collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {
                "queries": qry,
                "responses": response.text
            }}
        )
    elif email is not None:
        # Fallback: create new document if chat_id/session is missing
        collection.insert_one({
            "email": email,
            "queries": [qry],
            "responses": [response.text]
        })

    return {"response": response.text}   
    
    # return {"response": response.results[0].content}
    # return {"response": qry} 



@app.route("/registerit", methods=["POST"])
def registerit():
    # Get form data
    password = request.form.get("password")
    emailId = request.form.get("email")
    name = request.form.get("name")

    # Validate inputs
    if not password or password.isspace():
        return jsonify({"status": "error", "message": "Password cannot be empty or whitespace"}), 400
    elif len(password) < 8:
        return jsonify({"status": "error", "message": "Password must be at least 8 characters long"}), 400
    elif not password.isalnum():
        return jsonify({"status": "error", "message": "Password must be alphanumeric"}), 400

    # Hash the password using SHA-256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    print("Hashed password: ", hashed_password)

    # Validate email and name
    if not emailId or not name:
        return jsonify({"status": "error", "message": "Email and Name cannot be empty"}), 400

    try:
        # Create the table if it doesn't exist
        cr.execute(
            """
            CREATE TABLE IF NOT EXISTS user (
                name VARCHAR(200), 
                email VARCHAR(500), 
                password VARCHAR(10240),
                PRIMARY KEY (email)
            )
            """
        )

        # Use parameterized query to insert data
        query = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
        values = (name, emailId, hashed_password)
        cr.execute(query, values)

        # Commit the transaction to save changes
        mycon.commit()

        print("User registered successfully!")
        return jsonify({"status": "success", "message": "User registered successfully!"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": "An error occurred while registering the user"}), 500
    

    
    
@app.route("/loginit", methods=["POST"])
def loginit():
    # Get form data
    emailId = request.form.get("email")
    password = request.form.get("password")
    if password is None:
        # Handle the error, e.g., return an error message
        return jsonify({"status": "error", "message": "Password cannot be empty"}), 401
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    query = "SELECT * FROM user WHERE email = %s AND password = %s"
    values = (emailId, hashed_password)
    cr.execute(query, values)
    result = cr.fetchone()
    # fetch name from database
    if result is None:
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401
    usrName = result[0] 
    print(result)
    if result:
        session["userEmail"] = emailId  # Store email in session
        session["userName"] = str(usrName).split()[0] if usrName else ""  # Ensure usrName is a string and handle None
        return jsonify({"status": "success", "message": "Login successful!"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401




@app.route("/get_user", methods=["GET"])
def get_user():
    email = session.get("userEmail")
    name = session.get("userName")
    if email:
        return jsonify({"status": "success", "email": email, "name": name}), 200
    else:
        return jsonify({"status": "error", "message": "No user logged in"}), 401



@app.route("/logout", methods=["POST"])
def logout():
    session.pop("userEmail", None)  # Remove email from session
    session.pop("userName", None)   # Remove name from session
    return jsonify({"status": "success", "message": "Logged out successfully!"}), 200


if __name__ == "__main__":
    app.run(debug=True)
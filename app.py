from flask import Flask, render_template, request, jsonify, session
from google import genai
from openai import OpenAI
import psycopg2 as ps
import hashlib
import os
import time
from bson import ObjectId
import postgresExtraFuncs as eFuncs
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()





app = Flask(__name__)
app.secret_key = str(os.urandom(24))  # Generate a random secret key for session management
print("secret key", app.secret_key)


# Connect to PostgreSQL database
pwrd = os.getenv("DB_PASSWORD")


try:
    mycon = ps.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "postgres"),
        password=pwrd,
        dbname=os.getenv("DB_NAME", "aiversus")
    )
    print("Connected")
except ps.Error as e:
    print(f"Database connection failed: {e}")
    exit(1)

cr = mycon.cursor()

@app.route("/")
def index():
    session["chatgpt_tgl"] = "True"
    session["deepseek_tgl"] = "True"
    session["gemini_tgl"] = "True"
    return render_template("index.html")



@app.route("/new_chat", methods=["POST"])
def new_chat():
    email = session.get("userEmail")
    if not email:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    chat_id = eFuncs.insert_one({
        "email"    : email,
        "queries"  : [],
        "response" : [],
        "response2": [],
        "response3": []
    })
    if chat_id is not None:
        session["chat_id"] = str(chat_id)
        return jsonify({"status": "success", "message": "New chat created", "chat_id": chat_id}), 200
    else:
        session["chat_id"] = None
        return jsonify({"status": "error", "message": "Failed to create chat"}), 500



@app.route("/get_all_chats", methods=["GET"])
def get_all_chats():
    email = session.get("userEmail")
    if not email:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    # Fetch all chat history for the user from MongoDB
    user_docs = list(eFuncs.findAll(email) or [])  # Convert cursor to list
    if user_docs:
        return jsonify({
            "status": "success",
            "chats": [{
                "chat_id"   : str(doc["id"]), # type: ignore
                "queries"   : doc.get("queries", []),
                "response"  : doc.get("response", []),
                "response2" : doc.get("response2", []),
                "response3" : doc.get("response3", [])
            } for doc in user_docs if isinstance(doc, dict)]
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

    current_chat_id = session.get("chat_id")
    if not current_chat_id:
        return jsonify({"status": "error", "message": "No chat selected"}), 400

    try:
        # Fetch the specific chat document directly using its _id and email for security
        chat_doc = eFuncs.find_one(id = current_chat_id, email = email)
    except Exception:
        return jsonify({"status": "error", "message": "Invalid chat ID format"}), 400

    if chat_doc:
        return jsonify({
            "status": "success",
            "queries": chat_doc.get("queries", []),
            "response": chat_doc.get("response", []),
            "response2": chat_doc.get("response2", []),
            "response3": chat_doc.get("response3", [])
        }), 200
    else:
        return jsonify({"status": "error", "message": "No chat history found"}), 404



@app.route("/delete_empty_chats", methods=["POST"])
def delete_empty_chats():
    email = session.get("userEmail")
    if not email:
        return jsonify({"status": "error", "message": "User not logged in"}), 401  
    # Delete all chats for the user that have no queries or response
    
    
    result = eFuncs.delete_many(email)
    return jsonify({"status": "success", "message": f"{result} empty chats deleted."}), 200


@app.route("/delete_chat", methods=["POST"])
def delete_chat():
    email = session.get("userEmail")
    if not email:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    
    data = request.get_json()
    chat_id = data.get("chat_id")
    
    if not chat_id:
        return jsonify({"status": "error", "message": "Chat ID is required"}), 400
    
    result = eFuncs.delete_one(chat_id, email)
    if result:
        return jsonify({"status": "success", "message": "Chat deleted successfully"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to delete chat"}), 500


@app.route("/register", methods=["POST", "GET"])
def register_page():
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login_page():
    return render_template("login.html")



@app.route("/chatgpt-btn", methods=["POST"])
def chatgpt_btn():
    data= request.get_json()
    chatgpt_btn = str(data.get('chatgptBtn', True))
    try:
        # Ensure chatgpt_btn is a boolean
        print("Received chatgpt_btn:", type(chatgpt_btn))
        if chatgpt_btn not in ["True", "False"]:
            return jsonify({"status": "error", "message": "Invalid button state"}), 400
        
        # Store the button state in the session
        session["chatgpt_tgl"] = chatgpt_btn
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "success", "message": "ChatGPT button state updated"}), 200



@app.route("/deepseek-btn", methods=["POST"])
def deepseek_btn():
    data= request.get_json()
    deepseek_btn = str(data.get('deepseekBtn', True))
    try:
        # Ensure deepseek_btn is a boolean
        print("Received deepseek_btn:", type(deepseek_btn))
        if deepseek_btn not in ["True", "False"]:
            return jsonify({"status": "error", "message": "Invalid button state"}), 400
        
        # Store the button state in the session
        session["deepseek_tgl"] = deepseek_btn
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "success", "message": "DeepSeek button state updated"}), 200



@app.route("/gemini-btn", methods=["POST"])
def gemini_btn():
    data= request.get_json()
    gemini_btn = str(data.get('geminiBtn', True))
    try:
        # Ensure gemini_btn is a boolean
        print("Received gemini_btn:", type(gemini_btn))
        if gemini_btn not in ["True", "False"]:
            return jsonify({"status": "error", "message": "Invalid button state"}), 400
        
        # Store the button state in the session
        session["gemini_tgl"] = gemini_btn
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "success", "message": "Gemini button state updated"}), 200





def get_chat_history_for_prompt():
    """Helper function to get chat history as a string for AI prompts"""
    email = session.get("userEmail")
    chat_id = session.get("chat_id")
    
    if not email or not chat_id:
        return "{}"
    
    try:
        import json
        chat_doc = eFuncs.find_one(id=chat_id, email=email)
        if chat_doc:
            return json.dumps({
                "queries": chat_doc.get("queries", []),
                "response": chat_doc.get("response", []),
                "response2": chat_doc.get("response2", []),
                "response3": chat_doc.get("response3", [])
            })
    except Exception:
        pass
    return "{}"


# ==================== AI DEBATE SYSTEM ====================

# Set to True to bypass API and use mock responses (for testing when rate limited)
USE_MOCK_MODE = False

def call_ai(prompt: str, max_retries: int = 3) -> str:
    """Helper function to call Gemini API with mock fallback"""
    
    # Mock mode for testing when rate limited
    if USE_MOCK_MODE:
        if "FOR" in prompt or "FAVOR" in prompt:
            return "This is a compelling argument IN FAVOR of the topic. The benefits clearly outweigh the drawbacks when we consider long-term implications. Research shows positive outcomes in similar cases."
        elif "AGAINST" in prompt or "OPPOSE" in prompt:
            return "This is a strong argument AGAINST the topic. We must consider the risks and unintended consequences. Historical precedent suggests caution is warranted."
        elif "BALANCED" in prompt:
            return "Looking at both perspectives, there are valid points on each side. The FOR position raises important benefits, while the AGAINST position highlights legitimate concerns. A nuanced approach is needed."
        elif "JUDGE" in prompt:
            return '{"winner": "FOR", "scores": {"for": {"total": 25}, "against": {"total": 22}, "balanced": {"total": 24}}, "reasoning": "FOR presented stronger evidence.", "remarks": {"for": "Good arguments", "against": "Solid points", "balanced": "Fair analysis"}}'
        return "Mock response for testing purposes."
    
    # Real API call with retry
    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            response = client.models.generate_content(
                model="gemini-2.5-flash",  # Using 2.5 which has quota available
                contents=[prompt]
            )
            return response.text or ""
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = (attempt + 1) * 5  # 5s, 10s, 15s - faster retries
                print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            else:
                print(f"AI Call Error: {e}")
                return f"⚠️ Error: {str(e)}"
    
    # If all retries failed, return mock response instead of error
    print("All retries failed. Returning mock response.")
    if "FOR" in prompt:
        return "[MOCK - API Rate Limited] Strong argument in favor of this topic with compelling evidence and logical reasoning."
    elif "AGAINST" in prompt:
        return "[MOCK - API Rate Limited] Strong argument against this topic highlighting risks and concerns."
    elif "BALANCED" in prompt:
        return "[MOCK - API Rate Limited] Balanced perspective acknowledging valid points from both sides."
    return '{"winner": "TIE", "scores": {}, "reasoning": "Mock verdict due to API limits", "remarks": {}}'


def validate_debate_topic(query: str) -> dict:
    """Check if query is suitable for debate"""
    import json
    
    if not query or len(query.strip()) < 3:
        return {"is_debatable": False, "reason": "Query is too short", "suggested_topic": None}
    
    validation_prompt = f"""
    Analyze if this topic is suitable for a debate: "{query}"
    
    A topic is DEBATABLE if:
    - It has multiple valid perspectives (opinions can differ)
    - It's not just a greeting or simple question like "Hi" or "How are you?"
    - It's not asking for pure factual information (like "what is 2+2" or "who is the president")
    - It's substantive enough for discussion
    
    Respond ONLY with valid JSON (no markdown, no extra text):
    {{"is_debatable": true, "reason": "explanation"}}
    OR
    {{"is_debatable": false, "reason": "why not debatable", "suggested_topic": "a related debatable topic"}}
    """
    
    try:
        response = call_ai(validation_prompt)
        # Clean response - remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        response = response.strip()
        
        result = json.loads(response)
        return result
    except Exception as e:
        print(f"Validation Error: {e}")
        # Default to allowing debate if validation fails
        return {"is_debatable": True, "reason": "Validation check passed"}


def get_for_argument(topic: str, round_num: int, history: list) -> str:
    """Generate argument IN FAVOR of the topic"""
    history_str = "\n".join([f"Round {h['round']}: FOR said: {h.get('for', '')[:200]}... | AGAINST said: {h.get('against', '')[:200]}..." for h in history]) if history else "No previous rounds."
    
    round_context = {
        1: "Opening Statement - Present your strongest arguments in favor. Be compelling and clear.",
        2: "Rebuttal - Counter the AGAINST position and reinforce your stance with evidence.",
        3: "Closing Argument - Summarize why your position wins. Make it memorable."
    }
    
    prompt = f"""You are the FOR agent in a formal debate. You SUPPORT the topic.
    
Topic: "{topic}"
Round: {round_num}/3 - {round_context.get(round_num, '')}

Previous Debate History:
{history_str}

Your task: Make a compelling, well-structured argument IN FAVOR of this topic.
- Be persuasive and use logical reasoning
- Keep response focused (2-3 paragraphs max)
- If round 2+, directly address opponent's points
"""
    return call_ai(prompt)


def get_against_argument(topic: str, round_num: int, history: list) -> str:
    """Generate argument AGAINST the topic"""
    history_str = "\n".join([f"Round {h['round']}: FOR said: {h.get('for', '')[:200]}... | AGAINST said: {h.get('against', '')[:200]}..." for h in history]) if history else "No previous rounds."
    
    round_context = {
        1: "Opening Statement - Present your strongest arguments against. Be compelling and clear.",
        2: "Rebuttal - Counter the FOR position and reinforce your stance with evidence.",
        3: "Closing Argument - Summarize why your position wins. Make it memorable."
    }
    
    prompt = f"""You are the AGAINST agent in a formal debate. You OPPOSE the topic.
    
Topic: "{topic}"
Round: {round_num}/3 - {round_context.get(round_num, '')}

Previous Debate History:
{history_str}

Your task: Make a compelling, well-structured argument AGAINST this topic.
- Be persuasive and use logical reasoning
- Keep response focused (2-3 paragraphs max)
- If round 2+, directly address opponent's points
"""
    return call_ai(prompt)


def get_balanced_argument(topic: str, round_num: int, history: list) -> str:
    """Generate a balanced, nuanced perspective"""
    history_str = "\n".join([f"Round {h['round']}: FOR: {h.get('for', '')[:150]}... | AGAINST: {h.get('against', '')[:150]}..." for h in history]) if history else "No previous rounds."
    
    round_context = {
        1: "Opening Statement - Present a nuanced view acknowledging both sides.",
        2: "Analysis - Identify the strongest points from both FOR and AGAINST.",
        3: "Synthesis - Offer a balanced conclusion that acknowledges complexity."
    }
    
    prompt = f"""You are the BALANCED agent in a formal debate. You provide nuanced analysis.
    
Topic: "{topic}"
Round: {round_num}/3 - {round_context.get(round_num, '')}

Previous Debate History:
{history_str}

Your task: Provide a balanced, nuanced perspective that:
- Acknowledges valid points on BOTH sides
- Identifies where each side is strong or weak
- Offers thoughtful analysis without fully committing to one side
- Keep response focused (2-3 paragraphs max)
"""
    return call_ai(prompt)


def run_debate_round(topic: str, round_num: int, history: list) -> dict:
    """Run a single debate round with all 3 agents"""
    print("Starting FOR argument...")
    for_arg = get_for_argument(topic, round_num, history)
    print("FOR done. Waiting 3s...")
    time.sleep(3)  # 3 second delay between calls
    
    print("Starting AGAINST argument...")
    against_arg = get_against_argument(topic, round_num, history)
    print("AGAINST done. Waiting 3s...")
    time.sleep(3)
    
    print("Starting BALANCED argument...")
    balanced_arg = get_balanced_argument(topic, round_num, history)
    print("BALANCED done.")
    
    return {
        "round": round_num,
        "for": for_arg,
        "against": against_arg,
        "balanced": balanced_arg
    }


def get_judge_verdict(topic: str, debate_history: list) -> dict:
    """Judge evaluates the debate and declares a winner"""
    import json
    
    rounds_summary = ""
    for r in debate_history:
        rounds_summary += f"""
=== ROUND {r['round']} ===
FOR: {r['for']}

AGAINST: {r['against']}

BALANCED: {r['balanced']}
"""
    
    prompt = f"""You are the JUDGE of this debate. Evaluate fairly and declare a winner.

TOPIC: "{topic}"

FULL DEBATE:
{rounds_summary}

Provide your verdict as JSON (no markdown formatting):
{{
    "winner": "FOR" or "AGAINST" or "BALANCED" or "TIE",
    "scores": {{
        "for": {{"argument_strength": 1-10, "evidence": 1-10, "persuasiveness": 1-10, "total": 1-30}},
        "against": {{"argument_strength": 1-10, "evidence": 1-10, "persuasiveness": 1-10, "total": 1-30}},
        "balanced": {{"argument_strength": 1-10, "evidence": 1-10, "persuasiveness": 1-10, "total": 1-30}}
    }},
    "reasoning": "2-3 sentences explaining why the winner won",
    "remarks": {{
        "for": "Brief feedback for FOR agent",
        "against": "Brief feedback for AGAINST agent",
        "balanced": "Brief feedback for BALANCED agent"
    }}
}}
"""
    
    try:
        response = call_ai(prompt)
        # Clean response
        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        response = response.strip()
        
        return json.loads(response)
    except Exception as e:
        print(f"Judge Error: {e}")
        return {
            "winner": "TIE",
            "reasoning": "Could not determine a clear winner.",
            "scores": {},
            "remarks": {}
        }


@app.route("/debate", methods=["POST"])
def debate():
    """Main debate endpoint - Optimized for rate limits"""
    query = request.form.get("Query", "").strip()
    
    # Simple validation (no API call) to save rate limit quota
    if not query or len(query) < 5:
        return jsonify({
            "status": "not_debatable",
            "reason": "Topic is too short. Please enter a proper debate topic.",
            "suggested_topic": "Should AI be used in education?"
        }), 200
    
    # Check for greetings/simple queries
    simple_queries = ["hi", "hello", "hey", "how are you", "what's up", "test"]
    if query.lower() in simple_queries:
        return jsonify({
            "status": "not_debatable",
            "reason": "This looks like a greeting, not a debate topic.",
            "suggested_topic": "Should social media be banned for teenagers?"
        }), 200
    
    # Run SINGLE debate round (3 API calls instead of 9)
    debate_history = []
    round_result = run_debate_round(query, 1, debate_history)
    debate_history.append(round_result)
    
    # Wait before judge call
    time.sleep(20)
    
    # Get Judge verdict (1 more API call)
    verdict = get_judge_verdict(query, debate_history)
    
    # === SAVE DEBATE TO DATABASE ===
    email = session.get("userEmail")
    chat_id = session.get("chat_id")
    
    if email:
        # Format responses for storage
        import json
        for_response = debate_history[0].get("for", "") if debate_history else ""
        against_response = debate_history[0].get("against", "") if debate_history else ""
        balanced_response = debate_history[0].get("balanced", "") if debate_history else ""
        
        # Add verdict info to balanced response as structured JSON
        import json as json_lib
        verdict_json = json_lib.dumps(verdict)
        balanced_response += "|||VERDICT|||" + verdict_json
        
        if chat_id:
            # Update existing chat
            eFuncs.update_one(chat_id, email, 
                qry=f"[DEBATE] {query}", 
                rep=for_response, 
                rep2=against_response, 
                rep3=balanced_response)
        else:
            # Create new chat for debate
            new_chat_id = eFuncs.insert_one({
                "email": email,
                "queries": [f"[DEBATE] {query}"],
                "response": [for_response],
                "response2": [against_response],
                "response3": [balanced_response]
            })
            if new_chat_id:
                session["chat_id"] = new_chat_id
    
    return jsonify({
        "status": "success",
        "topic": query,
        "rounds": debate_history,
        "verdict": verdict
    }), 200


# END DEBATE SYSTEM 


@app.route("/query", methods=["POST"])
def query_page():
    qry = request.form.get("Query")
    email = session.get("userEmail")
    chat_id = session.get("chat_id")  # Get current chat_id from session
    chatgpt_btn = session.get("chatgpt_tgl")
    deepseek_btn = session.get("deepseek_tgl")
    gemini_btn = session.get("gemini_tgl")
    chatgpt_btn, deepseek_btn, gemini_btn = chatgpt_btn or "True", deepseek_btn or "True", gemini_btn or "True"
    responseTxt, response2Txt, response3Txt = None, None, None

    if (chatgpt_btn == "True"):
        # Using Gemini API for ChatGPT responses (OpenAI key has no model access)
        try:
            qrygpt = "You are response1 (or just response). Past chat in form of json: " + get_chat_history_for_prompt() + "\n\n Current Query: " + qry
            

            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                contents=[qrygpt]
            )
            responseTxt = response.text
        except Exception as e:
            print(f"Gemini Error (ChatGPT): {e}")
            responseTxt = "⚠️ Rate limit exceeded. Please wait a minute and try again."
    
    if (deepseek_btn == "True"):
        time.sleep(2)  # Delay to avoid rate limiting with same API key
        try:
            qryDp = "You are response2 (or just response). Past chat in form of json: " + get_chat_history_for_prompt() + "\n\n Current Query: " + qry
            client2 = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            response2 = client2.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[qryDp]
            )
            response2Txt = response2.text
        except Exception as e:
            print(f"Gemini Error (DeepSeek): {e}")
            response2Txt = "⚠️ Rate limit exceeded. Please wait a minute and try again."
    
    if (gemini_btn == "True"):
        time.sleep(2)  # Delay to avoid rate limiting with same API key
        try:
            qryGem = "You are response3 (or just response). Past chat in form of json: " + get_chat_history_for_prompt() + "\n\n Current Query: " + qry
            client3 = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            response3 = client3.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[qryGem]
            )
            response3Txt = response3.text
        except Exception as e:
            print(f"Gemini Error (Gemini): {e}")
            response3Txt = "⚠️ Rate limit exceeded. Please wait a minute and try again."
    
    if email is not None and chat_id is not None:
        # Update the correct chat document by _id
        
        
        eFuncs.update_one(id = chat_id, email = email, qry = qry or '', rep = responseTxt or '', rep2 = response2Txt or '', rep3 = response3Txt or '')
        
        
        
    elif email is not None:
        # Fallback: create new document if chat_id/session is missing
        eFuncs.insert_one({
            "email": email,
            "queries": [qry],
            "response": [responseTxt],
            "response2": [response2Txt],
            "response3": [response3Txt]
        })

    return {
        "response": responseTxt,
        "response2": response2Txt,
        "response3": response3Txt
    }

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
        # Use parameterized query to insert data
        query = "INSERT INTO \"user\" (name, email, password) VALUES (%s, %s, %s)"
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
    print("password: ", password)
    if password is None:
        # Handle the error, e.g., return an error message
        return jsonify({"status": "error", "message": "Password cannot be empty"}), 401
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    query = "SELECT * FROM \"user\" WHERE email = %s AND password = %s"
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
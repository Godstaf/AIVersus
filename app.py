from flask import *
from google import genai
import mysql.connector as my

app = Flask(__name__)

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


@app.route("/register", methods=["POST", "GET"])
def register_page():
    return render_template("register.html")


@app.route("/query", methods=["POST"])
def query_page():
    qry = request.form.get("Query")
    print("\n\n", qry, "\n\n")
    client = genai.Client(api_key="AIzaSyDLtRhhQTS05XcusmCaYX0m-NHEJK_Wq88")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=[qry]
    )
    print("\n\n", response.text, "\n\n")
    # print("\n\n", response, "\n\n")
    
    return{"response": response.text}
    
    # return {"response": response.results[0].content}
    # return {"response": qry} 
    
@app.route("/registerit", methods=["POST", "GET"])
def registerit():
    pass
    # password = request.form.get("password")
    # if password.isspace():
    #     return False
    
    # elif len(password) < 8:
    #     return False
    
    
    # emailId = request.form.get("email")
    # name = request.form.get("name")
    
    # cr.execute("CREATE TABLE IF NOT EXISTS user (name VARCHAR(100), email VARCHAR(50), password VARCHAR(50))")
    
    

    

if __name__ == "__main__":
    app.run(debug=True)

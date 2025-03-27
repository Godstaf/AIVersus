from flask import *
from google import genai


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login_page():
    return render_template("login.html")


@app.route("/query", methods=["POST"])
def query_page():
    qry = request.form.get("Query")
    print("\n\n", qry, "\n\n")
    client = genai.Client(api_key="AIzaSyDLtRhhQTS05XcusmCaYX0m-NHEJK_Wq88")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=[qry]
    )
    print("\n\n", response.text, "\n\n")
    return {"response": response.results[0].content}
    # return {"response": qry}
    


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/docs")
def docs():
    return render_template("docs.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        return "POST Request"
    return render_template("index.html")


app.run(debug=True)

from crypt import methods
import email
from unicodedata import name
from flask import Flask, request, render_template, url_for, redirect

app = Flask(__name__, template_folder="templates")

formDataList = []

@app.route("/success")
def FormData():
    print(formDataList)
    return render_template("success.html", formDataFlask = formDataList)

@app.route("/", methods = ['POST','GET'])
def Index():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        comment = request.form["comment"]
        formData = {
            "username" : username,
            "email" : email,
            "password" : password,
            "comment" : comment
        }
        formDataList.append(formData)
        return redirect(url_for('FormData'))
    else:
        return render_template("index.html")


app.run(port=5000, debug=True)
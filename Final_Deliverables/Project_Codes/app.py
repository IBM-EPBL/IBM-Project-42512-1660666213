import os
os.add_dll_directory('C:/Users/SUJINKUMAR/AppData/Local/Programs/Python/Python39/Lib/site-packages/clidriver/bin')
import json
from flask_session import Session
from flask import Flask, render_template, redirect, request, session, jsonify, url_for
from datetime import datetime

import ibm_db
import ibm_db_dbi

from dotenv import load_dotenv
load_dotenv()


string_conn = "DATABASE=bludb;\
    HOSTNAME={0};\
    PORT={1};\
    SECURITY=SSL;\
    SSLServerCertificate=DigiCertGlobalRootCA.crt;\
    PROTOCOL=TCPIP;\
    UID={2};\
    PWD={3}"
string_conn = string_conn.format(os.environ.get("HOSTNAME"),os.environ.get("PORT"),os.environ.get("UID"),os.environ.get("PWD"))
con = ibm_db.connect(string_conn,'','')

pconn = ibm_db_dbi.Connection(con)

app = Flask(__name__, template_folder="templates")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = 'smart fashion recommender application'

@app.route("/", methods = ['POST','GET'])
def Index():
    my_cursor = pconn.cursor()
    sql = 'select * from products'
    my_cursor.execute(sql)
    account = my_cursor.fetchall()
    print(account)
    return render_template("index.html", products = account)

@app.route("/signup",methods = ['POST','GET'])
def signup():
    if 'user' in session:
        return redirect(url_for('Index'))
    else:
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
           
            sql = "select * from users where username = ? or email = ?"
            ss = ibm_db.prepare(con, sql)
            ibm_db.bind_param(ss, 1, username)
            ibm_db.bind_param(ss, 2, email)
            ibm_db.execute(ss)
            dicts = ibm_db.fetch_row(ss)
            
            if dicts:
                return render_template("signup.html", msg = "user with username or email alreay exists.")
            elif request.form['password'] != request.form['cpass']:
                return render_template("signup.html", msg = "Password Mismatch.")
            else:
                sql = "insert into users(username, email, password) values (?,?,?)"
                ss = ibm_db.prepare(con, sql)
                ibm_db.bind_param(ss, 1, username)
                ibm_db.bind_param(ss, 2, email)
                ibm_db.bind_param(ss, 3, password)
                try:
                    ibm_db.execute(ss)
                    return redirect(url_for('Index'))
                except:
                    return render_template("signup.html", msg = "Error while trying to register user. Please try again after some time.")
        else:
            return render_template("signup.html", msg = "")
    
@app.route("/login", methods = ['POST','GET'])
def login():
    if 'user' in session:
        return redirect(url_for('Index'))
    else:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            
            sql = "select * from users where username = ? and password = ?"
            ss = ibm_db.prepare(con, sql)
            ibm_db.bind_param(ss, 1, username)
            ibm_db.bind_param(ss, 2, password)
            ibm_db.execute(ss)
            dicts = ibm_db.fetch_assoc(ss)
            print(dicts)
            if dicts:
                session['user'] = username
                session['time'] = datetime.now()
                session['uid'] = dicts['ID']

            print(session)
            # Redirect to Home Page
            if 'user' in session:
                return redirect(url_for('Index'))
            else:
                return render_template("login.html", msg = "Please Check The Credentials")
                
        else:
            return render_template("login.html", msg = "")

@app.route("/logout", methods = ['GET'])
def logout():
    session.clear()
    return redirect(url_for('Index'))

@app.route("/orders", methods = ['GET'])
def cart():
    account = ''
    FLAG = True
    my_cursor = pconn.cursor()
    sql = "select * from data where iden = ? and type = ?"
    try:
        params = (int(session.get("uid")),0)
        my_cursor.execute(sql,params)
        account = my_cursor.fetchall()
        print(account)
    except Exception as e:
        FLAG = e
    return render_template("shopping-cart.html", data = account, Flag = FLAG)

@app.route("/add-cart", methods = ['POST'])
def addCart():
    print(session)
    req = json.loads(request.data)
    FLAG = True

    sql = "select * from data where iden = ? and name = ?"
    ss = ibm_db.prepare(con, sql)
    ibm_db.bind_param(ss, 1, int(req['jinja']))
    ibm_db.bind_param(ss, 2, (req['name']))
    try:
        ibm_db.execute(ss)
    except Exception as e:
        FLAG = False

    dicts = ibm_db.fetch_assoc(ss)
    if dicts:
        sql = "update data set quantity = ? where ID = ?"
        ss = ibm_db.prepare(con,sql)
        ibm_db.bind_param(ss, 1, int(req['quantity']))
        ibm_db.bind_param(ss, 2, int(dicts['ID']))
        try:
            ibm_db.execute(ss)
        except:
            FLAG = False
    else:
        try:
            sql = "insert into data(name, image, price, quantity, category, type, iden) values (?,?,?,?,?,?,?)"
            ss = ibm_db.prepare(con, sql)
            print("name")
            ibm_db.bind_param(ss, 1, req['name'])
            print("image")
            ibm_db.bind_param(ss, 2, req['image'])
            print("price")
            ibm_db.bind_param(ss, 3, req['price'])
            print("quan")
            ibm_db.bind_param(ss, 4, int(req['quantity']))
            print("cat")
            ibm_db.bind_param(ss, 5, req['category'])
            print("typ")
            ibm_db.bind_param(ss, 6, int(req['type']))
            print("jin")
            ibm_db.bind_param(ss, 7, int(req['jinja']))

            ibm_db.execute(ss)
        except Exception as e:
            FLAG = e
    
    if not FLAG:
        return jsonify({"success" : FLAG})
    else:
        cnt = int(req['productCount']) - int(req['quantity'])
        sql = "update ZGS46818.PRODUCTS set quantity = ? where name = ?"
        ss = ibm_db.prepare(con,sql)
        ibm_db.bind_param(ss,1, int(req['productCount']) - int(req['quantity']))
        ibm_db.bind_param(ss,2, req['name'])

        ibm_db.execute(ss)

        return jsonify({"success" : True})

@app.route("/shop", methods = ["GET"])
def shop():
    my_cursor = pconn.cursor()
    sql = 'select * from products'
    my_cursor.execute(sql)
    account = my_cursor.fetchall()
    return render_template("shop.html", products = account)

@app.route("/contact", methods = ["GET"])
def contact():
    return render_template("contact.html")

@app.route("/admin", methods = ['GET'])
def admin():
    if not ('user' in session and session['user'] == 'admin'):
        return redirect(url_for('Index'))
    my_cursor = pconn.cursor()
    sql = 'select * from products'
    my_cursor.execute(sql)
    account = my_cursor.fetchall()
    proLen = len(account)

    sql2 = 'select * from users'
    my_cursor.execute(sql2)
    users = my_cursor.fetchall()
    userLen = len(users)

    sql3 = 'select * from data'
    my_cursor.execute(sql3)
    bought = my_cursor.fetchall()
    boughtLen = len(bought)

    return render_template('admin.html', account = account, proLen = proLen, users = users, userLen = userLen, bought = bought, boughtLen = boughtLen)

app.run(port=5000, debug=True)
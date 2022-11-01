
import json
from flask_session import Session
from flask import Flask, render_template, redirect, request, session, jsonify, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

import ibm_boto3
from ibm_botocore.client import Config, ClientError

COS_ENDPOINT = "https://s3.jp-tok.cloud-object-storage.appdomain.cloud" 
COS_API_KEY_ID = "T-NC4U3lQbvp0D0BKO30i65LGt-DDVBbRjjc9Ln8WWw4" 
COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/51776cc89a5d4278a626571bfea117fb:9fc3c795-01fd-429c-a84a-891a142a9a14::" 

cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

print("Retrieving list of buckets")
try:
    buckets = cos.buckets.all()
    for bucket in buckets:
        print("Bucket Name: {0}".format(bucket.name))
except ClientError as be:
    print("CLIENT ERROR: {0}\n".format(be))
except Exception as e:
    print("Unable to retrieve list buckets: {0}".format(e))

print("Retrieving bucket contents from: {0}".format("imagestoring123"))
try:
    files = cos.Bucket("imagestoring123").objects.all()
    for file in files:
        print("Item: {0} ({1} bytes).".format(file.key, file.size))
except ClientError as be:
    print("CLIENT ERROR: {0}\n".format(be))
except Exception as e:
    print("Unable to retrieve bucket contents: {0}".format(e))
        
import ibm_db

# con = ibm_db.connect("DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zgs46818;PWD=Hb8AHGHxiHjV6ZNv",'','')

# sql = "select * from users"
# stmt = ibm_db.execute(con,sql)
# dicts = ibm_db.fetch_assoc(stmt)
# print(dicts)


app = Flask(__name__, template_folder="templates")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = 'smart fashion recommender application'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'loki@123'
app.config['MYSQL_DB'] = 'fashion'
 
 
mysql = MySQL(app)

@app.route("/", methods = ['POST','GET'])
def Index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products')
    account = cursor.fetchall()
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
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users where username = %s and email = %s',[username, email])
            account = cursor.fetchone()
            if account:
                return render_template("signup.html", msg = "user with username alreay exists.")
            else:
                cursor.execute('INSERT INTO users( username, email, password ) values (%s,%s,%s)',[username, email, password])
                mysql.connection.commit()
                return redirect(url_for('Index'))
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
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users where username = %s and password = %s',[username, password])
            account = cursor.fetchone()
            if account != None:
                session['user'] = username
                session['time'] = datetime.now( )
                session['uid'] = account['id']

            print(session)
            # Redirect to Home Page
            if 'user' in session:
                return redirect(url_for('Index'))
            else:
                return render_template("login.html", msg = "Please Check The Credentials")
                
        else:
            return render_template("login.html", msg = "")

@app.route("/cart", methods = ['GET'])
def cart():
    return render_template("cart.html")

@app.route("/add-cart", methods = ['POST'])
def addCart():
    req = json.loads(request.data)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from products where id = %s",[req['id']])
    data = cursor.fetchone()
    cursor.execute('INSERT INTO user_products( name, descr, image, price, quantity, category ) values (%s,{} ,%s,%s,%s,%s)'.format(data['quantity']),[data['name'], data['image'], data['price'], req['quantity'], data['category']])
    mysql.connection.commit()
    cursor.execute('update products set quantity = %s where id = %s',[ str(int(data['quantity'])-1), data['id']])
    mysql.connection.commit()
    return req
    

app.run(port=5000, debug=True)
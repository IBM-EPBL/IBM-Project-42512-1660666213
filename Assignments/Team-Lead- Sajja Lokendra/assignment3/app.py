from flask import Flask, request, render_template, url_for, redirect

app = Flask(__name__, static_url_path='/static')

jobList = []

@app.route("/", methods = ['POST','GET'])
def Index():
    return jobList

@app.route("/add-job",methods = [ 'POST','GET' ])
def AddJob():
    jobData = {
        "jobId" : 123,
        "Name" : "ueru",
        "Email" : "fghnpoihgdty",
        "postedOn" : 123456,
        "updatedOn" : 3456789
    }
    jobList.append(jobData)
    return jobList

@app.route("/delete-job", methods = [ 'DELETE','GET' ])
def DeleteJob():
    for i in jobList :
        if i["jobId"] == 123:
            jobList.remove(i)
    return jobList



app.run(port=5000, debug=True)
from flask import Flask, request, render_template, request, url_for, redirect
from redisDb import redisMaster, redisSlave
from cassandraDb import cassandraDb
import re

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/", methods=["PUT"])
def put_request():
    shorturl = request.args.get('short')
    longurl = request.args.get('long')
    if (shorturl and longurl):
        if not re.match("^(https?:\/\/)?(www.)?[a-z0-9]+\.[a-z]+.*$", longurl):
            return render_template("400_bad_request.html")
        # write put request to logs
        f.write(shorturl + " " + longurl + "\n")
        f.flush()
        try:
            redisMaster.set(shorturl, longurl) # set longurl:shorturl in cache
            redisMaster.addToQueue({shorturl: longurl}) # put in queue to add to cassandra
        except:
            # add directly to cassandra if redis adds fails
            db.insertUrl(shorturl, longurl)
        return render_template("201_created.html")
    return render_template("400_bad_request-2.html")

@app.route("/<short>", methods=["GET"])
def get_request(short):
    if (short):
        if (short != 'favicon.ico'): # ignore if it's trying to get favicon
            redisResult = redisSlave.get(short)
            if redisResult is not None: # check if the short url is in cache
                return redirect(redisResult)
            else: #check cassandra since short url is not in cache
                results = db.selectUrl(short)
                for result in results:
                    return redirect(result[1])
            # since it hasn't returned from previous statements, it can't find matching shorturl
    return render_template("404_not_found.html")

if __name__ == "__main__":
    db = cassandraDb(['10.11.1.118', '10.11.2.118', '10.11.3.118']) # CHANGE THIS IP WHEN RUNNING
    redisMaster = redisMaster()
    redisSlave = redisSlave()
    try:
        db.keyspaceCreation()
    except:
        pass
    db.setKeyspace()
    try:
        db.tableCreation()
    except:
        pass
    f = open("/logs/putRequests", "a")
    app.run(host="0.0.0.0", port=80)
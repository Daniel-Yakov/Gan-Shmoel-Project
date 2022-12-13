from flask import Flask, jsonify
from database import *

app = Flask(__name__)

DB=DataBase("billdb", "root")

def my_generator():
    i=1
    while i>0:
        i+=1
        yield i
gen = my_generator()


# need to add healthcheck of the database!!!
@app.route("/health", methods=["GET"])
def isHealthy():
    
    status=DB.getHealthCheck()
    if status == 1:
        return jsonify("OK"),200
    else:
        return jsonify(status="Database Failure"),500

@app.route("/provider", methods=['POST'])
def CreateProvider():
    name='Provider'+str(next(gen))
    DB.addProvider(name)
    id={"id":DB.GetProviderByName(name)} 
    return jsonify(id)

    
@app.route("/provider/<id>",methods=['PUT'])
def ChangeName(id):
    new_name='Provider'+str(next(gen))
    DB.changeProviderName(id,new_name)
    return "changed"

@app.route("/rates", methods=["GET"])
def downloadFile():
    pass

@app.route("/rates", methods=["POST"])
def updateFile():
    pass

@app.route("/truck", methods=["POST"])
def addTruck():
    pass

@app.route("/truck/<id>",methods=["PUT"])    
def updateProvider():
    pass

@app.route("/truck/<id>?from=t1&to=t2",methods=["GET"])    
def my_func_1():
    pass

@app.route("/bill/<id>?from=t1&to=t2",methods=["GET"])
def my_func_2():
    pass


if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)
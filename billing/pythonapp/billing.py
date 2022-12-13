from flask import Flask, jsonify,request
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
    DB.cleanRatesTable()
    DB.createRatesFromFile()
    return "Success"

@app.route("/truck", methods=["POST"])
def addTruck():
    
    id = request.args.get('id')
    plate = request.args.get('plate')
        
    if id==None:
        return jsonify("error"),500
    if plate==None:
        return jsonify("error"),500
    
    return jsonify(DB.addTruck(int(id),str(plate)))


@app.route("/truck/<id>", methods=["PUT"])
def changIDtruck(id):
    plate = request.args.get('plate')
    Truck=DB.ChangeTruckID(plate,id)
    return jsonify(Truck)








if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)
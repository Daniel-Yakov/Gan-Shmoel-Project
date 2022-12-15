from flask import Flask, jsonify,request, send_file
from database import *
import shutil
import requests
import os

#create flask
app = Flask(__name__)

# port specified
app_port = int(os.environ['BILLING_APP_PORT'])
weight_port = int(os.environ['WEIGHT_APP_PORT'])


# create database connection with 'database' class
DB=DataBase("billdb", "root")


def my_id_generator():
    i=1
    while i>0:
        i+=1
        yield i
gen = my_id_generator()



# health check of both the flask and the database
@app.route("/health", methods=["GET"])
def isHealthy():
    status=DB.getHealthCheck()
    if status == 1:
        return jsonify("OK"),200
    else:
        return jsonify(status="Database Failure"),500



# create new provider in the database
@app.route("/provider", methods=['POST'])
def CreateProvider():
    name = request.args.get('name')
    if name == None:
        name='Provider'+str(next(gen))
    DB.addProvider(name)
    return jsonify(id=DB.GetProviderByName(name))



# to change name of existing provider by the drovider's id    
@app.route("/provider/<id>",methods=['PUT'])
def ChangeName(id):
    new_name = request.args.get('name')
    if new_name == None:
        new_name='Provider'+str(next(gen))
    DB.changeProviderName(id,new_name)
    return jsonify(success="provider name has changed")



# download the xlsx file of the rates (/in/rates.xlsx) 
# into backups folder in the container (/rates_backups/)
@app.route('/rates', methods=['GET'])
def downloadFile():
#   file_name = request.args.get('file_name')
  file_path = '/in/rates.xlsx'
  shutil.copy(file_path, f'./rates_backups/ratesBU_{str(next(gen))}.xlsx')
  return jsonify(success='File downloaded successfully')



# method to update the database according to the rates.xlsx file on the host
@app.route("/rates", methods=["POST"])
def updateFile():
    DB.cleanRatesTable()
    DB.createRatesFromFile()
    return jsonify(success="Rates table is up to date")



# method to create a new truck
@app.route("/truck", methods=["POST"])
def addTruck():    
    id = request.args.get('id')
    plate = request.args.get('plate')
        
    if id==None:
        return jsonify(error="id is missing"),500
    if plate==None:
        return jsonify(error="plate is missing"),500
    
    return jsonify(DB.addTruck(int(id),str(plate)))


# change truck's plate 
@app.route("/truck/<id>", methods=["PUT"])
def changIDtruck(id):
    plate = request.args.get('plate')
    if plate==None:
        return jsonify(error="plate is missing"),500
    Truck=DB.ChangeTruckID(plate,id)
    return jsonify(success=Truck)


@app.route("/truck/<id>", methods=["GET"])
def Gettruck(id):
    From = request.args.get('from')
    to= request.args.get('to')
    if DB.CheckForTruckID(id)==None:
        return jsonify("Truck not found"),404 
    
    truckID=int(DB.CheckForTruckID(id)[0][0])
    #WEIGH= requests.get(f"http://localhost:{weight_port}/health?from={From}&to={to}").json()
    WEIGH=[{ "id": 10001, "session": [ { "time": "Wed, 14 Dec 2022 09:55:38 GMT","weight": "T-14409"}]}]
    
    return WEIGH




    

@app.route("/bill/<id>", methods=["GET"])
def getBill(id):
    weight_list = requests.get(f"http://localhost:{weight_port}/weight?from=t1&to=t2").json()
    my_id = id
    name  = DB.GetProviderByID(id)
    start = request.args.get('from')
    end = request.args.get('to')
    
    
    
if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)
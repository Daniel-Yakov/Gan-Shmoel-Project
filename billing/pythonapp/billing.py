from flask import Flask,Response, jsonify,request, send_file,render_template, make_response
from database import *
import shutil
import requests
import os
import time


#create flask
app = Flask(__name__)

# port specified
app_port = int(os.environ['BILLING_APP_PORT'])
weight_port = int(os.environ['WEIGHT_APP_PORT'])
app.config["JSON_SORT_KEYS"] = False

# create database connection with 'database' class
try:
    DB=DataBase("billdb", "root")
except:
    time.sleep(3)
    DB=DataBase("billdb", "root")


def statement_return(action, content, code):
    answer = {f"{action}":f"{content}"}
    answer= jsonify(answer)
    answer = answer.get_data().decode('utf-8')
    return make_response(render_template("base.html", answer=answer),code)


def my_id_generator():
    i=1
    while i>0:
        i+=1
        yield i
gen = my_id_generator()


# home page route
@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")



# health check of both the flask and the database
@app.route("/health", methods=["GET"])
def isHealthy():
    status=DB.getHealthCheck()
    if status == 1:
        return statement_return("OK", "server is up and run", 200)
    else:
        return statement_return("ERROR", "Database Failure", 500)



# create new provider in the database
@app.route("/provider", methods=['POST'])
def CreateProvider():
    name = request.form['name']
    if name == "":
        return statement_return("ERROR", "Name is missing", 500)
    DB.addProvider(name)
    return statement_return("ID", DB.GetProviderByName(name), 200)



# to change name of existing provider by the drovider's id    
@app.route("/provider",methods=['GET'])
def ChangeName():
    new_name = request.args.get('name')
    id = request.args.get('id')
    if new_name == "":
        return statement_return("ERROR", "Name is missing", 500)
    elif id == "":
        return statement_return("ERROR", "ID is missing", 500)
    DB.changeProviderName(id,new_name)
    return statement_return("Success", "Provider name has changed", 200)



# download the xlsx file of the rates (/in/rates.xlsx) 
# into backups folder in the container (/rates_backups/)
@app.route('/rates', methods=['GET'])
def downloadFile():
#   file_name = request.args.get('file_name')
    file_path = '/in/rates.xlsx'
    shutil.copy(file_path, f'./rates_backups/ratesBU_{str(next(gen))}.xlsx')
    
    return statement_return("Success", "File downloaded successfully", 200)



# method to update the database according to the rates.xlsx file on the host
@app.route("/rates", methods=["POST"])
def updateFile():
    DB.cleanRatesTable()
    DB.createRatesFromFile()
    return statement_return("Success", "Rates table is up to date", 200)



# method to create a new truck
@app.route("/truck", methods=["POST"])
def addTruck():    
    id = request.form["id"]
    plate = request.form["plate"]
        
    if id=="":
        return statement_return("ERROR", "ID is missing", 500)
    elif plate=="":
        return statement_return("ERROR", "Plate is missing", 500)
    else:
        ans = DB.addTruck(int(id),str(plate))
        return statement_return("New Truck", ans, 200)



# change truck's provider 
@app.route("/truckpro", methods=["GET"])
def changIDtruck():
    plate = request.args.get('plate')
    id = request.args.get('id')
    if id=="":
        return statement_return("ERROR", "ID is missing", 500)
    elif plate=="":
        return statement_return("ERROR", "Plate is missing", 500)
    
    Truck=DB.ChangeTruckID(plate,id)
    return statement_return("Success", Truck, 200)



@app.route("/truck", methods=["GET"])
def Gettruck():
    id = request.args.get('plate')
    From = request.args.get('From')
    to= request.args.get('to')
    if DB.CheckForTruckID(id)==None:
        return jsonify("Truck not found"),404 

    truckID=int(DB.CheckForTruckID(id)[0][0])
    #WEIGH= requests.get(f"http://localhost:{WEIGHT_APP_PORT}/item?from={From}&to={to}").json()
    WEIGH=[ { "id": "T-3", "session": [ { "bruto": 200, "containers": "None", "datetime": "Thu, 15 Dec 2022 11:17:30 GMT", "direction": "out", "id": 10027, "neto": 0, "produce": "apple", "truck": "T-3", "truckTara": 200 }, { "bruto": 200, "containers": "None", "datetime": "Thu, 15 Dec 2022 11:17:53 GMT", "direction": "out", "id": 10028, "neto": 0, "produce": "apple", "truck": "T-3", "truckTara": 200 } ], "tara": "na" } ]
    id=WEIGH[0]['id']
    tara=WEIGH[0]['session'][0]['truckTara']
    session=WEIGH[0]['session']
    result={'ID':id,
            'tara':tara,
            'session':session
        }
    answer = jsonify(result)
    answer = answer.get_data().decode('utf-8')
    return make_response(render_template("base.html", answer=answer),200)

   

@app.route("/bill", methods=["GET"])
def getBill():
    id = request.args.get("id")
    name  = DB.GetProviderByID(id)
    start = request.args.get('from')
    end = request.args.get('to')
    
    truckList=DB.get_Truck_By_Provider_ID(id)
    provider_trucks = ""
    for tr in truckList:
        provider_trucks+=f"{tr[0]} "
    truckList = set()
    
    sessionCount=0
    products=[]
    url = f"http://<weight_domain_name>:{weight_port}/weight?from={start}&to={end}"
    url = f"http://localhost:5000/weight"
    weight_list = requests.get(url).json()

    for ses in weight_list:
        if str(ses["id"]) in provider_trucks:
            sessionCount+=1
            truckList.add(ses["id"])
            already_exist = False
            for n in products:
                if n["product"] == ses["produce"]:
                    already_exist = True
                    n["count"] = str(int(n["count"])+1)
                    n["amount"] += (ses["bruto"])
                    n["pay"] = n["amount"]*n["rate"]
                    break
            
            if already_exist:
                continue
            else:
                
                new_product = {"product":ses["produce"], 
                               "count": "1",
                               "amount": ses["bruto"],
                               "rate": DB.get_rate_from_product(ses["produce"],id)[0][0],
                               "pay": ses["bruto"]*DB.get_rate_from_product(ses["produce"],id)[0][0]
                               }
                products.append(new_product)
    
    total = 0
    for prod in products:
        total += prod["pay"]
    
    bill = {"id":id,
            "name":name,
            "from":start,
            "to": end,
            "truckCount":len(truckList),
            "sessionCount":sessionCount,
            "products":products,
            "total":total
            }
    products=bill['products']
    return render_template('bill.html',products=products,total=total)


# # in case that weight service is not ready a deadline
@app.route("/weight", methods=["GET"])
def my_try():
    return  render_template("test.json")  
    


if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)
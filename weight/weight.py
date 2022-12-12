#!/usr/bin/python3
from flask import Flask ,request ,jsonify
import conncetion
import requests

app_w= Flask(__name__)
test_url = "https://www.google.com"

@app_w.route('/')
def home():
    pass


# POST /weight (called by new weight)
@app_w.post('/weight')
def weight_post():
########################################################################################################
       #get data from request
    req_data = request.get_json()
    direction = req_data.get('direction')
    truck = req_data.get('truck')
    containers = req_data.get('containers')
    weight = req_data.get('weight')
    unit = req_data.get('unit')
    force = req_data.get('force')
    produce = req_data.get('produce')
    
    #check if all the required fields are present
    if(direction == None or weight == None or unit == None or force == None or produce == None):
        return "Missing parameters!", 400
    
    #check if truck is provided if weighing a truck
    if(direction == "in" or direction == "out") and truck == None:
        return "Missing truck parameter!", 400
    
    #check if containers are provided if weighing a container
    if(direction == "none") and containers == None:
        return "Missing containers parameter!", 400
    
    #check if force is true/false
    if(force != True and force != False):
        return "Force parameter should be true/false!", 400
    
    #check if direction is "in", "out" or "none"
    if(direction != "in" and direction != "out" and direction != "none"):
        return "Direction should be in/out/none!", 400
    
    #check if unit is "lbs" or "kg"
    if(unit != "lbs" and unit != "kg"):
        return "Unit should be lbs/kg!", 400
    
    #check if produce is a valid produce
    if(produce != "na"):
        r = requests.get(test_url)
        if(r.status_code != 200):
            return "Invalid produce!", 400
    
    #if all the checks pass, start recording data
    conn = conncetion.get_connection()
    cur = conncetion.get_cursor(conn)
    
    #generate a unique weight id
    weight_id = generate_weight_id(conn)
    
    #add data to the DB
    query = "INSERT INTO weights (id, direction, truck, containers, weight, unit, force, produce) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cur.execute(query, (weight_id, direction, truck, containers, weight, unit, force, produce))
    conn.commit()
    
    #return the weight id
    return jsonify({"id": weight_id, "truck": truck, "bruto": weight, "truckTara": 0, "neto": 0})


def generate_weight_id(conn):
    cur = conncetion.get_cursor(conn)
    query = "SELECT MAX(id) AS max_id FROM weights"
    cur.execute(query)
    row = cur.fetchone()
    if row is None:
        return "weight_1"
    else:
        max_id = row[0]
        max_id_int = int(str(max_id).split("_")[1])
        new_id_int = max_id_int + 1
        return "weight_"+str(new_id_int)

        ####################################################################################

# POST /batch-weight (called by admin)
@app_w.post('/batch-weight')
def batchWeight_post():
    pass


# GET /unknown (called by admin)
@app_w.get('/unknown')
def unknown():
    pass


# GET /weight (report by time)
@app_w.get('/weight')
def weight_get():
    pass


# GET /item/<id> (truck/container report)
@app_w.get('/item/<id>')
def item_id():
    pass


# GET /session/<id> (weighing report)
@app_w.get('/session/<id>')
def session_id():
    pass


#GET /health
@app_w.get('/health')
def health():

    page = requests.get(test_url)
    status=str(page.status_code)

    if status == "200":
    # if(conncetion.db_health_check() and status == "200"):
        return "OK " + status
    else:
        return "BAD " + status


if __name__ == "__main__":
    app_w.run(host="0.0.0.0", debug=True)

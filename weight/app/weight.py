#!/usr/bin/python3
from flask import Flask, request, jsonify
import connection
import requests
from datetime import datetime,date

app_w = Flask(__name__)
test_url = "https://www.google.com"


@app_w.route('/')
def home():
    pass


# POST /weight (called by new weight)
@app_w.post('/weight')
def transaction_post():
    # get data from request
    req_data = request.get_json()
    direction = req_data.get('direction')
    truck = req_data.get('truck')
    containers = req_data.get('containers')
    tweight = int(req_data.get('weight'))
    #unit = req_data.get('unit')
    # force = req_data.get('force')
    produce = req_data.get('produce')
    # check if all the required fields are present
    if (direction == None or tweight == None or produce == None):
        return "Missing parameters!", 400

    # check if truck is provided if weighing a truck
    if (direction == "in" or direction == "out") and truck == None:
        return "Missing truck parameter!", 400

    # check if containers are provided if weighing a container
    if (direction == "none" and containers == None):
        return "Missing containers parameter!", 400

    # check if force is true/false
    # if not force:
    #     force=False
    # check if direction is "in", "out" or "none"
    if (direction != "in" and direction != "out" and direction != "none"):
        return "Direction should be in/out/none!", 400

    # check if unit is "lbs" or "kg"
    # if (unit != "lbs" and unit != "kg"):
    #    return "Unit should be lbs/kg!", 400

    # check if produce is a valid produce
    if produce == "":
        produce = "na"

    # if all the checks pass, start recording data
    conn = connection.get_connection()
    cur = conn.cursor()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # להכניס לתוך הטבלה

    # generate a unique weight id לשנות את הקוד להשתמש ומזהה דיפולטיבי
    cur = conn.cursor()
    query = "SELECT MAX(id) AS max_id FROM transactions"
    cur.execute(query)
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row[0] is None:
        transaction_id = 1
    else:
        max_id = row[0]
        max_id_int = int(max_id) + 1
        transaction_id = max_id_int

    # add data to the DB
    # direction, truck, containers, weight, unit, force, produce
   
    total_weight_containers = 0
# Iterate through the list of containers_id
    conn = connection.get_connection()
    cur = conn.cursor()
    listContainers=str(containers).split(",")
    for container_id in listContainers:
        cur.execute("SELECT weight FROM containers_registered WHERE container_id = %s", (container_id))
        result = cur.fetchone()
        if result != None:
            total_weight_containers += result[0]
        else: pass
    cur.close()
    conn.close()

    # return
    if direction == "out":
        truckTaraVal=int(tweight-total_weight_containers)
        netoVal=int(tweight-total_weight_containers-(tweight-total_weight_containers))
        conn = connection.get_connection()
        cur = conn.cursor()
        query = f"INSERT INTO transactions (direction,datetime, truck,produce,containers,bruto,truckTara,neto) VALUES ('{direction}', '{timestamp}', '{truck}', '{produce}','{containers}','{tweight}','{truckTaraVal}','{netoVal}')"
        # Add a containers after the truck
        cur.execute(query)
        conn.commit()
    
        cur.close()
        conn.close()
        return jsonify({"id": transaction_id, "truck": truck, "bruto": tweight, "truckTara": truckTaraVal, "neto":netoVal})
    else:
        conn = connection.get_connection()
        cur = conn.cursor()
        query = f"INSERT INTO transactions (direction,datetime, truck,produce,containers,bruto) VALUES ('{direction}', '{timestamp}', '{truck}', '{produce}','{containers}','{tweight}')"
        # Add a containers after the truck
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()


        return jsonify({"id": transaction_id, "truck": truck, "bruto": tweight})

       
        ####################################################################################
# POST /batch-weight (called by admin)



@app_w.post('/batch-weight')
def batchWeight_post():
    pass


# GET /unknown (called by admin)
@app_w.get('/unknown')
def unknown():
    conn = connection.get_connection()
    cur = conn.cursor()
    sql = "SELECT container_id FROM containers_registered WHERE weight IS NULL"
    cur.execute(sql)
    unknown_containers = cur.fetchall()
    cur.close()
    conn.close()
    return "".join(str(unknown_containers))


# GET /weight (report by time)
@app_w.get('/weight')
def transaction_get():
    # t1 = request.args.get('from')
    # t2 = request.args.get('to')
    # filter = request.args.get('filter')
    # # default t1 is "today at 000000". default t2 is "now".
    # if t1 is None:
    #     t1 = 'today at 000000'
    # if t2 is None:
    #     t2 = 'now'
    # # default filter is "in,out,none"
    # if filter is None:
    #     filter = 'in'

    now = datetime.now()
    date_time_str = int(now.strftime("%Y%m%d%H%M%S"))
    today = date.today()
    t1_str=int(today.strftime("%Y%m%d000000"))
    t1 = request.args.get(f"from {t1_str}")
    t2 = request.args.get(f"to {date_time_str}")
    filter = request.args.get('filter')
    # default t1 is "today at 000000". default t2 is "now".
    # if t1 is None:
    #     t1 = t1_str
    # if t2 is None:
    #     t2 = date_time_str
    # # default filter is "in,out,none"
    # if filter is None:
    #     filter = 'in'
    if filter is None:
        conn = connection.get_connection()
        # get weight data
        cur = conn.cursor()
        cur.execute("SELECT id,direction,bruto,neto,produce,containers FROM transactions")
        rows = cur.fetchall()
        cur.close()
        conn.close()
    else:
        # create a connection to the DB
        conn = connection.get_connection()
        
        # get weight data
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE datetime BETWEEN %s AND %s AND direction = %s", (t1_str, date_time_str, filter))
        #cur.execute("SELECT id,direction,bruto,neto,produce,containers FROM transactions")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # format json data
    data=[]
    
    for row in rows:
        data.append({
            'id': row[0],
            'direction': row[1],
            'bruto': row[2],
            'neto': row[3],
            'produce': row[4],
            'containers': str(row[5]).split(',')}) #לעשות משהו אחר אם קורה שאין IN

#    cur.close()
#   conn.close()
    return jsonify(data)



# GET /item/<id> (truck/container report)
# GET /item/<id> (truck/container report)
@app_w.get('/item/<id>')
def item_id(id):
    # assume the server time is the current time
    server_time = datetime.now()
    # get the item id from the request URL
   
   
    # item_id = request.args.get('id')
    item_id=id
   
    # get the start and end timestamps from the request URL
    # use default values if not provided
    t1 = request.args.get('from', datetime.strftime(server_time, '%Y%m01000000'))
    t2 = request.args.get('to', datetime.strftime(server_time, '%Y%m%d%H%M%S'))
    # convert the timestamps to datetime objects
    t1 = datetime.strptime(t1, '%Y%m%d%H%M%S')
    t2 = datetime.strptime(t2, '%Y%m%d%H%M%S')
    conn = connection.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, truckTara FROM transactions WHERE truck= %s", (item_id))
    ListofTuple= cur.fetchall()#
    myId,my_truckTara=ListofTuple[0]
    cur.close()
    conn.close()
    # if rows[0] ==None:
    #     conn = connection.get_connection()
    #     cur = conn.cursor()
    #     cur.execute("SELECT id FROM containers_registered WHERE container_id = %s", (item_id))
    #     rows = cur.fetchall()
    #     cur.close()
    #     conn.close()


    if ListofTuple is None:
        return 404
    # retrieve the item from the database
    # item = db.get_item(item_id)
    data=[]
    for myId, my_truckTara in ListofTuple:
        print(f'{myId}: {my_truckTara}')

        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE id=%s" ,(myId))
        resultSes = cur.fetchall()
        cur.close()
        conn.close()
    
    
        if my_truckTara is type==int:
            Tara=int(my_truckTara)
        else:
            Tara="na"
        ses_data=[]
        for row in resultSes:
            ses_data.append({
                'time' : row[1],
                'weight' : row[3]
            })

        data.append({
            'id':myId,
            'tara':Tara,
            'session' : ses_data
            })
    return jsonify(data)


# GET /session/<id> (weighing report)
@app_w.get('/session/<id>')
def session_id(id):
    my_id=id
    conn = connection.get_connection()
    cur = conn.cursor()

    cur.execute("SELECT direction from transactions where id =%s",my_id)
    if cur.fetchone()=="out":
        isout=False
    else:
        isout=True
    cur.close()
    conn.close()

   
    if isout == False:
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id,truck,bruto from transactions where id =%s",my_id)
        row = cur.fetchone()
        cur.close()
        conn.close()
        id1, truck1, bruto1 = row[0], row[1], row[2]


        
        # End of part 1
        return{ "id": id1, 
        "truck": truck1 or "na",
        "bruto": bruto1}
    else:
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id,truck,bruto,weight from transactions where id =%s",my_id)
        row = cur.fetchone()
        id1, truck1, bruto1,weight = row[0], row[1], row[2], row[3]
        cur.close()
        conn.close()
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT containers from transactions where id =%s",my_id)
        my_containers=cur.fetchone()
        my_containers=str(my_containers).split(" ")
        cur.close()
        conn.close()

        # Iterate through the list of containers_id

        total_weight_containers = 0

        for container_id in my_containers:
            conn = connection.get_connection()
            cur = conn.cursor()
            # Execute the SQL query
            cur.execute("SELECT weight FROM containers_registered WHERE container_id = %s", (container_id))
            # Fetch the result
            result = cur.fetchone()
            cur.close()
            conn.close()
            # If the container_id is found in the table, add its weight to the total
            if result is not None:
                total_weight_containers += result[0]
            # Checks if there is a container that has no weight
            else:
                flag=True
        # Final calculation rely on the flag
        if flag:
            Neto="na"
        else:
            Neto=total_weight_containers-bruto1- (int(weight)-total_weight_containers)

        # End of part 2
        return{ "id": id1, 
        "truck": truck1 or "na",
        "bruto": bruto1,
        "truckTara": int(weight)-total_weight_containers,
        "neto": Neto
          }


#GET /health
@app_w.get('/health')
def health():

    page = requests.get(test_url)
    status = str(page.status_code)
    print(True)
    if status == "200":
        # if(conncetion.db_health_check() and status == "200"):
        return "OK " + status
    else:
        return "BAD " + status


if __name__ == "__main__":
    app_w.run(host="0.0.0.0", debug=True)


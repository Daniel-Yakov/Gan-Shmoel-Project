#!/usr/bin/python3
from flask import Flask, request, jsonify
import connection
import requests
from datetime import datetime,date
import csv,json,os
app_w = Flask(__name__)
test_url = "https://www.google.com"


@app_w.route('/')
def home():
    pass


def check_direction(direction, truck, force):
    conn = connection.get_connection()
    cur = conn.cursor()
    # Checks the last id of a transaction of a truck
    query1 = f"SELECT MAX(id) AS max_id FROM transactions where truck='{truck}'"
    cur.execute(query1)
    lastID = cur.fetchone()[0]
    cur.close()
    conn.close()
    conn = connection.get_connection()
    cur = conn.cursor()
    # Checks the last id of a transaction of a truck headed in
    query2 = f"SELECT MAX(id) AS max_id FROM transactions where truck='{truck}' and direction='in'"
    cur.execute(query2)
    lastInID = cur.fetchone()[0]
    cur.close()
    conn.close()
    direction = str(direction)
    if lastID == lastInID and lastID is not None:
        res = "in"
    elif lastID is None or lastInID is None:  # מחזיר שקר כדי שיעשה שני דברים
        return True
    else:
        res = "out"
    if direction == "in" and res == "in":
        if force:
            return True
        else:
            return False
    elif direction == "out" and res == "out":
        if force:
            return True
        else:
            return False
    elif direction == "in" and res == "out":
        return True
    elif direction == "out" and res == "in":
        return True
    else:
        return True

def isIn(truck,direction):
    conn = connection.get_connection()
    cur = conn.cursor()
    # Checks the last id of a transaction of a truck
    query1 = f"SELECT MAX(id) AS max_id FROM transactions where truck='{truck}'"
    cur.execute(query1)
    lastID = cur.fetchone()
    cur.close()
    conn.close()
    conn = connection.get_connection()
    cur = conn.cursor()
    # Checks the last id of a transaction of a truck headed in
    query2 = f"SELECT MAX(id) AS max_id FROM transactions where truck='{truck}' and direction='in'"
    cur.execute(query2)
    lastInID = cur.fetchone()
    cur.close()
    conn.close()
    direction = str(direction)
    if lastID == lastInID: ###############3and lastID is not None:
        return True
    else:
        return False

# POST /weight (called by new weight)
@app_w.post('/weight')
def transaction_post():
    # get data from request
    req_data = request.get_json()
    direction = req_data.get('direction')
    truck = req_data.get('truck')
    containers = req_data.get('containers')
    weight = int(req_data.get('weight'))
    unit = req_data.get('unit')
    force = req_data.get('force')
    produce = req_data.get('produce')
    timestamp = datetime.now().strftime(r"%Y%m%d%H%M%S")
    # BAG לבדוק מה קורה שלא שולחים כלום
    # check if all the required fields are present
    if direction not in ["in", "out", "none"]:
        return "Direction should be in/out/none!", 400

    if unit not in ["lbs", "kg"]:
        return "Unit should be lbs/kg!", 400

    if weight is None:
        return "Missing weight parameter!", 400

    if containers is None:
        return "Missing containers parameter!", 400

    if force is None:
        force = False

    if produce is None:
        produce = "na"

    if truck is None:
        truck = "na"

    total_weight_containers = 0
    # Iterate through the list of containers_id
    conn = connection.get_connection()
    cur = conn.cursor()
    listContainers = str(containers).split(",")
    for container_id in listContainers:
        cur.execute(
            "SELECT weight FROM containers_registered WHERE container_id = %s", (container_id))
        result = cur.fetchone()
        if result != None:
            total_weight_containers += result[0]
        else:
            pass
    cur.close()
    conn.close()

    if check_direction(direction, truck, force) == False:  # מחזירה שקר אם יש בעיה בכיוונים
        return "Error"
    elif force:
        # Overwrite the existing row with a new POST request
        conn = connection.get_connection()
        cur = conn.cursor()
        query = f"SELECT MAX(id) AS max_id FROM transactions where truck='{truck}'"
        cur.execute(query)
        resID = cur.fetchone()[0]
        cur.close()
        conn.close()
        conn = connection.get_connection()
        cur = conn.cursor()
        if direction == "in" and isIn(truck, direction):
            query = f"UPDATE transactions SET datetime='{timestamp}', direction='{direction}', containers='{containers}', bruto='{weight}', produce='{produce}' WHERE id='{resID}' and truck='{truck}'"
            cur.execute(query)
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"id": resID, "truck": truck, "bruto": weight})
        elif direction == "out": ########OUT הוא בעייתי בגלל הוא מקבל אחרי אין רק עם יש פורס
            truckTaraVal = weight  # Weight of truck
            query = f"SELECT bruto FROM transactions where truck='{truck}' and direction='in' <(SELECT MAX(id) AS max_id FROM transactions)"
            cur.execute(query)
            total_weight = cur.fetchone()[0]
            conn.close()
            cur.close()
            netoVal = int(
                total_weight - total_weight_containers - truckTaraVal)
            conn = connection.get_connection()
            cur = conn.cursor()
            query = f"UPDATE transactions SET datetime='{timestamp}', direction='{direction}', containers='{containers}', bruto='{weight}',truckTara='{truckTaraVal}', neto='{netoVal}', produce='{produce}' WHERE id='{resID}' and truck='{truck}'"
            cur.execute(query)
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"id": resID, "truck": truck, "bruto": total_weight, "truckTara": truckTaraVal, "neto": netoVal})

    # if all the checks pass, start recording data
    conn = connection.get_connection()
    cur = conn.cursor()

    # להכניס לתוך הטבלה

    # generate a unique weight id לשנות את הקוד להשתמש ומזהה דיפולטיבי
    # cur = conn.cursor()
    # query = "SELECT MAX(id) AS max_id FROM transactions"
    # cur.execute(query)
    # row = cur.fetchone()
    # cur.close()
    # conn.close()
    # if row[0] is None:
    #     transaction_id = 1
    # else:
    #     max_id = row[0]
    #     max_id_int = int(max_id) + 1
    #     transaction_id = max_id_int

    # add data to the DB
    # direction, truck, containers, weight, unit, force, produce

    # return
    if direction == "in" and isIn(truck, direction):
        # outquery = "SELECT direction FROM transactions WHERE truck is %s", (
        #     truck)################# אין לא עובד עם אחרי אוט
        conn = connection.get_connection()
        cur = conn.cursor()
        # cur.execute(outquery)
        # if cur.fetchone() == :
        #     pass
        query = f"INSERT INTO transactions (direction,datetime, truck,produce,containers,bruto) VALUES ('{direction}', '{timestamp}', '{truck}', '{produce}','{containers}','{weight}')"
        # Add a containers after the truck
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT max(id) FROM transactions where truck='{truck}'")
        transaction_id = cur.fetchone()[0]
        cur.close()
        conn.close()
        #my_id = transaction_id[0]
        return jsonify({"id": transaction_id, "truck": truck, "bruto": weight})
    # and isIn(truck,direction)==False############################:
    elif direction == "out" and isIn(truck, direction) == False:  # Force
        conn = connection.get_connection()
        cur = conn.cursor()######################בעיה עם אוט לא נכנס אלא עם זה פורס
        query = f"SELECT MAX(id) AS max_id FROM transactions where truck='{truck}'"
        cur.execute(query)
        resID = cur.fetchone()[0]
        cur.close()
        conn.close()
        truckTaraVal = weight  # Weight of truck
        conn = connection.get_connection()
        cur = conn.cursor()
        # <(SELECT MAX(id) AS max_id FROM transactions)"
        query = f"SELECT bruto FROM transactions where truck='{truck}' and direction='in'"
        cur.execute(query)
        total_weight = cur.fetchone()[0]####################TypeError: 'NoneType' object is not subscriptable
        conn.close()
        cur.close()
        netoVal = int(total_weight-total_weight_containers - truckTaraVal)
        conn = connection.get_connection()
        cur = conn.cursor()
        query = f"UPDATE transactions SET direction='{direction}', truckTara='{truckTaraVal}', neto='{netoVal}' WHERE truck='{truck}' AND id='{resID}'"
        # Add a containers after the truck
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT max(id) FROM transactions")
        transaction_id = cur.fetchone()
        cur.close()
        conn.close()
        my_id = transaction_id[0]
        return jsonify({"id": my_id, "truck": truck, "bruto": total_weight, "truckTara": truckTaraVal, "neto": netoVal})
        # return jsonify(transaction_id[0])
    else:
        return "ERROR", 404
        ####################################################################################


# POST /batch-weight (called by admin)
@app_w.post('/batch-weight')
def batchWeight_post():
    filename = request.form.get("filename")
    passw = request.form.get("password")
    fext = os.path.splitext(filename)[1]
    if passw != 'root':
        return "\nWrong Password\n"
    # file.save(f'./in/{file.filename}')
    F="./in/"+filename
    try:
        FirstCsv=True
        with open(F,'r') as file:
            if fext == '.csv':
                csvreader = csv.reader(file)
                for row in csvreader:
                    valist = []
                    if FirstCsv:
                        FirstCsv=False
                        unit=row[1]#kg/lbs
                    else:
                        valist.append(row)
                    
            elif fext == '.json':
                data=json.load(file)
                valist = []
                for item in data:
                    valist.append((item['id'], item['weight'], item['unit']))
                unit = valist[0][2]
                print(valist)
                print(unit)
            else:
                return "ERRO1"
    except:
        return "ERRO2"
    if FirstCsv ==False: 
        for inserting in valist:
            pass
    allContainer=connection.fetchall('SELECT container_id FROM containers_registered')
    # return jsonify(allContainer)
    listofUpdate=[]
    for con_id in allContainer:
        if con_id[0] in valist:
            listofUpdate.append[con_id[0]]
   
    for inserting[0] in valist:###CSV ['K-8263', '666']  ##JSON ('T-14409', 528, 'lbs')
        
        if inserting[0] in listofUpdate:####################### כמעט מוכן 
            connection.execute_commit(f"UPDATE containers_registered SET weight = '{inserting[1]}', unit = '{unit}' WHERE container_id = '{inserting[0]}'")
        else:
            connection.execute_commit(f"INSERT INTO containers_registered (container_id,weight,unit) VALUES ('{inserting[0]}','{inserting[1]}','{unit}')")        

    return filename+" uploaded successfully"
       
        
    




    # conn = connection.get_connection()
    # cur = conn.cursor()
    # allCID = cur.execute('SELECT container_id FROM containers_registered')
    # cur.execute('SELECT container_id FROM containers_registered')
    # res=cur.fetchall()#why we not use in res
    # cur.close()
    # conn.close()
    #print(allCID)   #fo tstin
    # allCID = [i[0] for i in allCID]#what is allCID
    # for i in valist:
    #     if i[0] in allCID :
    #         conn = connection.get_connection()
    #         cur = conn.cursor()
    #         cur.execute(f"UPDATE containers_registered SET weight = {int(i[1])}, unit = '{unit}' WHERE container_id = '{i[0]}'")
    #         res=cur.fetchall()#########################
    #         cur.close()
    #         conn.close()
    #     else:
    #         conn = connection.get_connection()
    #         cur = conn.cursor()
    #         cur.execute(f"INSERT INTO containers_registered (container_id,weight,unit) VALUES ('{i[0]}',{int(i[1])}, '{unit}')")
    #         res=cur.fetchall()#################################
    #         cur.close()
    #         conn.close()
    # return valist


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
    now = datetime.now()
    t2 = int(now.strftime("%Y%m%d%H%M%S"))
    today = date.today()
    t1=int(today.strftime("%Y%m%d000000"))
    
    filter = request.args.get('filter')
    
    if filter is None:#######################################מחכה לבדיקה לאחר שהפוסט היה מוכן
        data=[]
        conn = connection.get_connection()
        # get weight data
        cur = conn.cursor()
        cur.execute("SELECT truck,direction,bruto,neto,produce,containers FROM transactions")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        for row in rows:
            data.append({
            'truck': row[0],
            'direction': row[1],
            'bruto': row[2],
            'neto': row[3],
            'produce': row[4],
            'containers': str(row[5]).split(',')}) #לעשות משהו אחר אם קורה שאין IN
        return jsonify(data)
    else:
        # create a connection to the DB
        conn = connection.get_connection()
        
        # get weight data
        cur = conn.cursor()
        cur.execute("SELECT truck,direction,bruto,neto,produce,containers FROM transactions WHERE datetime BETWEEN %s AND %s AND direction = %s", (t1, t2, filter))
        #cur.execute("SELECT id,direction,bruto,neto,produce,containers FROM transactions")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # format json data
    data=[]
    
    for row in rows:
        data.append({
            'truck': row[0],
            'direction': row[1],
            'bruto': row[2],
            'neto': row[3],
            'produce': row[4],
            'containers': str(row[5]).split(',')}) 

#    cur.close()
#   conn.close()
    return jsonify(data)




# GET /item/<id> (truck/container report)
@app_w.get('/item/<id>')#####################בדיקה לאחר פוסט
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
    cur.execute("SELECT id FROM transactions WHERE truck= %s and datetime BETWEEN %s AND %s and direction= 'out'", (item_id,t1, t2))
    ListofTuple= cur.fetchall()#######################
    if len(ListofTuple)==0:
            return jsonify("Not Found " + item_id)
    else:
        myID=ListofTuple[0]
        cur.close()
        conn.close()
        # if len(ListofTuple)==0:
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM containers_registered WHERE container_id = %s", (item_id))
        ListofTuple = cur.fetchall()
        cur.close()
        conn.close()
        if len(ListofTuple)==0:
            return jsonify("Not Found " + item_id)
    # retrieve the item from the database
    # item = db.get_item(item_id)
    data=[]
    listS=[]
    for myID in ListofTuple:
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE id=%s and direction='out'" ,myID[0])
        resultSes = cur.fetchall()
        cur.close()
        conn.close()
        for i in resultSes:
            my_res={"id":i[0],"datetime":i[1],"direction":i[2],"truck":i[3],"containers":i[4],"bruto":i[5],"truckTara":i[6],"neto":i[7],"produce":i[8]}
        listS.append(my_res)
    conn = connection.get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT bruto FROM transactions where truck='{item_id}' and direction='out' <(SELECT MAX(id) AS max_id FROM transactions)")
    my_bruto = cur.fetchall()
    cur.close()
    conn.close()
    if isinstance(my_bruto, int):
        Tara=int(my_bruto)
    else:
        Tara="na"
    ses_data=[]
    data.append({
        'id':item_id,
        'tara':Tara,
        'session' : listS
        })
    return jsonify(data)
################################################################################

@app_w.get('/session1/<id>')
def session_id1(id):
    my_id=id
    query=(f"SELECT direction FROM transactions WHERE id ='{my_id}'")
    res=connection.fetchall(query)
    return jsonify(res)
############################################################################################3
# GET /session/<id> (weighing report)
@app_w.get('/session/<id>')#עושה הרבה בעיות 
def session_id(id):
    my_id_truck=id
    conn = connection.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT direction FROM transactions WHERE id =%s",my_id_truck)
    res=cur.fetchone()
    if res=="out":
        isout=True
    else:
        isout=False
    cur.close()
    conn.close()
    if isout == False:
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id,truck,bruto from transactions where id =%s",my_id_truck)
        row = cur.fetchone()
        cur.close()
        conn.close()
        # return jsonify(row)###############################בעיה של NULL לטפל
        id1, truck1, bruto1= row[0], row[1], row[2]
        # if isinstance(truck1, int):
        #     Tara=int(my_bruto)
        # else:
        #     Tara="na"
        # End of part 1
        return{ "id": id1,
        "truck": truck1 or "na",
        "bruto": bruto1,
        }
    else:
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id,truck,bruto,truckTara,neto from transactions where id =%s",my_id_truck)
        row = cur.fetchone()
        id1, truck1, bruto1,truckTara,neto1= row[0], row[1], row[2], row[3], row[4]
        cur.close()
        conn.close()
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT containers from transactions where id =%s",my_id_truck)
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
                total_weight_containers += result[container_id]
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
    isconnect=connection.db_health_check()
    

    if( isconnect and status == "200"):
        return jsonify("APP ON AIR")
    elif status == "200":
        return jsonify("OK " + status+" & BAD Connection")
    else :
        print(status)
        return jsonify(status)

if __name__ == "__main__":
    app_w.run(host="0.0.0.0", debug=True)


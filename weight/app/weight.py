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


def isIn(truck, direction):
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
    if lastID == lastInID:  # 3and lastID is not None:
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
    weight = req_data.get('weight')
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
    listContainers = str(containers).split(",")
    for container_id in listContainers:
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT weight, unit FROM containers_registered WHERE container_id = %s", (container_id))
        result = cur.fetchone()
        cur.close()
        conn.close()
        notForCalc=False
        if result != None:
            try:#if no weight or weight =NULL
                temp=1
                temp+=result[0]
            except:
                notForCalc=True

            if result[1] == "lbs":
                result = float(result[0]) // 2.2046226218
            if not notForCalc :
                total_weight_containers += result
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
        if direction == "in" and isIn(truck, direction):
            conn = connection.get_connection()
            cur = conn.cursor()
            query = f"UPDATE transactions SET datetime='{timestamp}', direction='{direction}', containers='{containers}', bruto='{weight}', produce='{produce}' WHERE id='{resID}' and truck='{truck}'"
            cur.execute(query)
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"id": resID, "truck": truck, "bruto": weight})
        elif direction == "out":
            conn = connection.get_connection()
            cur = conn.cursor()
            truckTaraVal = weight  # Weight of truck
            # <(SELECT MAX(id) AS max_id FROM transactions)"
            query = f"SELECT bruto FROM transactions where truck='{truck}' and direction='{direction}'"
            cur.execute(query)
            total_weight = cur.fetchone()
            conn.close()
            cur.close()
            if total_weight is None:
                return "You're trying to force an update on a transaction with no weight documented"
            total_weight = total_weight[0]
            if notForCalc:
                netoVal="na"
            else:
                netoVal = total_weight - total_weight_containers - truckTaraVal
                netoVal=round(netoVal, 2)
            conn = connection.get_connection()
            cur = conn.cursor()
            query = f"UPDATE transactions SET datetime='{timestamp}', direction='{direction}', containers='{containers}',truckTara='{truckTaraVal}', neto='{netoVal}', produce='{produce}' WHERE id='{resID}' and truck='{truck}'"
            cur.execute(query)
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"id": resID, "truck": truck, "bruto": total_weight, "truckTara": truckTaraVal, "neto":netoVal})
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
    if direction == "in":
        # outquery = "SELECT direction FROM transactions WHERE truck is %s", (
        #     truck)
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
        cur.execute(f"SELECT max(id) FROM transactions where truck='{truck}'")
        transaction_id = cur.fetchone()[0]
        cur.close()
        conn.close()
        #my_id = transaction_id[0]
        return jsonify({"id": transaction_id, "truck": truck, "bruto": weight})
    # and isIn(truck,direction)==False############################:
    # and isIn(truck, direction) == False:  # Force ##### Gives error when trying to update an IN transaction
    elif direction == "out":
        conn = connection.get_connection()
        cur = conn.cursor()
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
        # total_weight query gives a Type Error when 2 OUT's in a row without a force - instead of a customized error message
        total_weight = cur.fetchone()
        conn.close()
        cur.close()
        if total_weight is None:
            return "Error"
        total_weight = total_weight[0]
        if notForCalc:
            netoVal="na"
        else:
            netoVal = total_weight - total_weight_containers - truckTaraVal
            netoVal=round(netoVal, 2)
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
        cur.execute(f"SELECT max(id) FROM transactions where truck='{truck}'")
        transaction_id = cur.fetchone()
        cur.close()
        conn.close()
        my_id = transaction_id[0]
        return jsonify({"id": my_id, "truck": truck, "bruto": total_weight, "truckTara": truckTaraVal, "neto":netoVal})
        # return jsonify(transaction_id[0])
    elif direction == "none":
        conn = connection.get_connection()
        cur = conn.cursor()
        querylastin = f"SELECT max(id) FROM transaction where truck='{truck}' and direction='in'"
        cur.execute(querylastin)
        lastIN = cur.fetchone()
        if lastIN is not None:
            return "There's a transaction where truck is heading in, no 'none' direction transaction can be proccessed"
        query = f"INSERT INTO transactions (direction,datetime, truck,produce,containers,bruto) VALUES ('{direction}', '{timestamp}', '{truck}', '{produce}','{containers}','{weight}')"
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        conn = connection.get_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT max(id) FROM transactions where truck='{truck}'")
        transaction_id = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"id": transaction_id, "truck": truck, "bruto": weight})
    else:
        return "ERROR", 404
        ####################################################################################


# POST /batch-weight (called by admin)
@app_w.post('/batch-weight')
def batchWeight_post():
    filename = request.form.get("filename")
    passw = request.form.get("password")
    fext = os.path.splitext(filename)[1]#.csv#.json#
    if passw != 'root':
        return "\nWrong Password\n"
    F="./in/"+filename
    try:
        FirstCsv=True
        with open(F,'r') as file:
            if fext == '.csv':
                csvreader = csv.reader(file)
                valist = []
                for row in csvreader:
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
            else:
                return "file name is not csv/json"
    except:
        return "can't open this file"
    
   
    # return jsonify(allContainer)
    
    flatList=[]
    for item in valist:########################
        flatList.extend(item)
    
   
    for inserting in valist:###CSV ['K-8263', '666']  ##JSON ('T-14409', 528, 'lbs')
        
        
        try:
            connection.execute_commit(f"INSERT INTO containers_registered (container_id,weight,unit) VALUES ('{inserting[0]}','{inserting[1]}','{unit}')")        
        except:
            connection.execute_commit(f"UPDATE containers_registered SET weight = '{inserting[1]}', unit = '{unit}' WHERE container_id = '{inserting[0]}'")

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
    try:
        if unknown_containers[0] is None:
            return "No unknow Containers"
    except:
        return "No unknow Containers"
    cur.close()
    conn.close()
    myRes=[]
    for conta in unknown_containers:
        myRes.append((list(conta)))
    myRes = [item for sublist in myRes for item in sublist]# O(n*m)
    return myRes



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
        if len(data) == 0:
            return "No Session"    
        else:
            return jsonify(data)
    else:
        # create a connection to the DB
        conn = connection.get_connection()
        
        # get weight data
        cur = conn.cursor()
        cur.execute("SELECT truck,direction,bruto,neto,produce,containers FROM transactions WHERE datetime BETWEEN %s AND %s AND direction = %s", (t1, t2, filter))
       
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


    if len(data) == 0:
            return "No Session"    
    else:
        return jsonify(data)




# GET /item/<id> (truck/container report)
@app_w.get('/item/<id>')#####################בדיקה לאחר פוסט
def item_id(id):
    
    server_time = datetime.now()
    
    item_id=id
   
    t1 = request.args.get('from', datetime.strftime(server_time, '%Y%m01000000'))
    t2 = request.args.get('to', datetime.strftime(server_time, '%Y%m%d%H%M%S'))
    # convert the timestamps to datetime objects
    t1 = datetime.strptime(t1, '%Y%m%d%H%M%S')
    t2 = datetime.strptime(t2, '%Y%m%d%H%M%S')
    conn = connection.get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM transactions WHERE truck= '{item_id}' and datetime BETWEEN '{t1}' AND '{t2}' ")
    ListofTuple= cur.fetchall()#######################
    cur.close()
    conn.close()
    ### IStruck
    notFound=True#########################CHECK IF HERE
    try:
        if ListofTuple[0] is None:
            notFound=True
        else:notFound=False
    except:
        notFound=True


    if notFound==False:##############################################3
       
        listRes=[]
        myID=[]
        for list_id in ListofTuple:
            myID.append(list_id[0])
        #direction='out'
        listOfIDs=[]
        for res_id in myID:
            conn = connection.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM transactions WHERE id=%s and direction='out'" ,res_id)
            resultOut = cur.fetchone()
            if resultOut is not None:
                listOfIDs.append(resultOut)
            cur.close()
            conn.close()
            
        
        for i in listOfIDs:
            listRes.append(i[0])
          
        
        ##direction='in'"
        listOfIDs=[]
        for res_id in myID:
            conn = connection.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM transactions WHERE id=%s and direction='in'" ,res_id)
            resultOut = cur.fetchone()
            if resultOut is not None:
                listOfIDs.append(resultOut)
            cur.close()
            conn.close()
          
        for i in listOfIDs:
            listRes.append(i[0])
        

        
        Tara=connection.fetchone(query=f"SELECT truckTara FROM transactions WHERE truck='{item_id}' and direction ='out' and id =(SELECT MAX(id) AS max_id FROM transactions WHERE truck='{item_id}')")
        # return jsonify(Tara)
        try:
            if Tara[0] is None:Tara="na"
            else:Tara=Tara[0]
        except:
            Tara="na"        
       
        return jsonify({"id":item_id,"instance":"truck","tara":Tara,"sessions":listRes})
    #### for containers
    
    else:
        ListofTuple=connection.fetchone(f"SELECT * FROM containers_registered WHERE container_id = '{item_id}'")  
      
        notFound=True#########################CHECK IF HERE
    try:
        if ListofTuple[0] is None:
            notFound=True
        else:notFound=False
    except:
        notFound=True
    if notFound:
        return jsonify("Not Found " + item_id)
    else :
        
        myconta=connection.fetchall("SELECT id,containers FROM transactions ") 
        Sessions=[]
        for containesStr in myconta:
            look=str(containesStr[1]).split(',')
            if item_id in look:

                Sessions.append(containesStr[0])
        
        return jsonify({"id":item_id,"instance":"container","tara":ListofTuple[1],"sessions":Sessions})
       


############################################################################################3
# GET /session/<id> (weighing report)
@app_w.get('/session/<id>')
def session_id(id):

    conn = connection.get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM transactions WHERE id='{id}' ")
    ListofTuple= cur.fetchall()#######################
    cur.close()
    conn.close()

    try:######בדיקה שקיים שסאן 
        if ListofTuple[0] is None:
             return jsonify("Not Found " + id)
    except:
         return jsonify("Not Found " + id) 

    if ListofTuple is None: ######בדיקה שקיים שסאן 
             return jsonify("Not Found " + id)
    else:
        
        myID=[]
        for list_id in ListofTuple:
            myID.append(list_id[0])
    resultOut=connection.fetchone(f"SELECT * FROM transactions WHERE id='{id}'")

    if resultOut[2]=='out':
        return jsonify({"id":resultOut[0],"direction":resultOut[2],"truck":resultOut[3],"bruto":resultOut[5],"truckTara":resultOut[6],"neto":resultOut[7]})
    if resultOut[2]=='in':
        return jsonify({"id":resultOut[0],"direction":resultOut[2],"truck":resultOut[3],"bruto":resultOut[5]})
    


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


import pymysql
def get_connection():
    connection = pymysql.connect(
        host="my_data",
        user="root",
        port=3306,
        password="root",
        database="weight",
        # charset="utf8mb4",
        # cursorclass=pymysql.cursors.DictCursor
    )
    return connection


# def Database_check():
#     mycur=connection.cursor()
#     mycur.execute("SHOW DATABASES")
# # Fetch all the rows in a list of lists result
#     result = mycur.fetchall()
#     for r in result:
#         if "weight" not in r:
#             with open('weightdb.sql','r') as f:
#                 sql_command = f.read()
#                 mycur.execute(sql_command,multi=True)
#                 connection.commit()
#                 connection.close()
#         else:
#             mycur.execute("use weight")
def execute(query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(str(query))
    cur.close()
    conn.close()

def execute_commit(query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(str(query))
    conn.commit()
    cur.close()
    conn.close()

def fetchall(query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(str(query))
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def fetchone(query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(str(query))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res

def db_health_check():
    try:
        with get_connection().cursor() as cursor:
            sql = "select 1"
            cursor.execute(sql)
            
        return True
    except Exception:
        return False






# Database_check()
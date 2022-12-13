import pymysql
connection = pymysql.connect(
    host="my_data",
    user="root",
    port=3306,
    password="root",
    database="weight",
    # charset="utf8mb4",
    # cursorclass=pymysql.cursors.DictCursor
)


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

def db_health_check():
    try:
        with connection.cursor() as cursor:
            sql = "select 1"
            cursor.execute(sql)
        return True
    except Exception:
        return False


def get_connection():
    return connection


def get_cursor(my_connect):
    # לבדוק אם החיבור חוקי
    return connection.cursor()
# Database_check()
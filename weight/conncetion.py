import pymysql
connection = pymysql.connect(
    host="app_weight",
    user="root",
    port=3306,
    password="root",
    database="weight",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)


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
    #לבדוק אם החיבור חוקי
    return connection.cursor()

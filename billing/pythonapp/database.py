import mysql.connector


class DataBase:
    
    def __init__(self, db_name, db_password):
        self.connection = mysql.connector.connect(
            host="mysql", port="3306", user="root", password=f"{db_password}", database=f"{db_name}")
        print("DB connected!")
        self.cursor = self.connection.cursor()


    def addProvider(self, name):
        sql = "INSERT INTO Provider (id, name) VALUES (%d, %s)"
        val = (name)
        self.cursor.execute(sql, val)
        self.connection.commit()
    
    
    def changeProviderName(self, id, new_name):
        sql = f"UPDATE Provider SET name = '{new_name}' WHERE id = '{id}'"
        self.cursor.execute(sql)
        self.connection.commit()
    
    def getProvidersCount(self):
        self.cursor.execute("SELECT count(*) FROM Provider")
        result = self.cursor.fetchall()
        return result
            
    def GetProviderByName(self,name):
        sql=f"SELECT * FROM Provider WHERE name = '{name}'"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

        

import mysql.connector


class DataBase:
    db_host ="localhost"
    db_port = "3306"
    db_user = "root"
    
    def __init__(self, db_name, db_password):
        self.password = db_password
        self.name = db_name
        self.connection = mysql.connector.connect(
            host=DataBase.db_host, port=DataBase.db_port, user=DataBase.db_user, password=db_password, database=db_name)
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

        

import mysql.connector


class DataBase:
    
    def __init__(self, db_name, db_password):
        self.connection = mysql.connector.connect(
            host="mysql", port="3306", user="root", password=f"{db_password}", database=f"{db_name}")
        print("DB connected!")
        self.cursor = self.connection.cursor()


    def getHealthCheck(self):
        self.cursor.execute("SELECT 1;")
        result = self.cursor.fetchall()
        return result[0][0]
        
    def addProvider(self, name):
        sql = f"INSERT INTO Provider (name) VALUES ('{name}');"
        self.cursor.execute(sql)
        self.connection.commit()
    
    
    def changeProviderName(self, id, new_name):
        sql = f"UPDATE Provider SET name='{new_name}' WHERE id='{id}';"
        self.cursor.execute(sql)
        self.connection.commit()
    
    def getProvidersCount(self):
        self.cursor.execute("SELECT count(*) FROM Provider;")
        result = self.cursor.fetchall()
        return result
            
    def GetProviderByName(self,name):
        sql=f"SELECT id FROM Provider WHERE name='{name}';"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

        
    def addTruck(self,providerID,truckID):
        sql="INSERT INTO Trucks (id, provider_id) VALUES ("+str(truckID)+","+ str(providerID)+");"
        self.cursor.execute(sql)
        self.connection.commit()
        return truckID
    def ChangeTruckID(self,plate,newProvider):
        sql=f"UPDATE Trucks SET provider_id='{newProvider}' WHERE id='{plate}';"
        self.cursor.execute(sql)
        self.connection.commit()
        return newProvider
        

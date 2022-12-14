import mysql.connector
import pandas as pd
import openpyxl


class DataBase:
    
    
    def __init__(self, db_name, db_password):
        self.connection = mysql.connector.connect(
            host="billmysql", port="3306", user="root", password=f"{db_password}", database=f"{db_name}")
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
    
    
    # change to return a number        
    def GetProviderByName(self,name):
        sql=f"SELECT id FROM Provider WHERE name='{name}';"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result
    
    
    def GetProviderByID(self,id):
        sql=f"SELECT name FROM Provider WHERE id='{id}';"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result[0][0]
    
    
    def cleanRatesTable(self):
        sql = f"DELETE FROM Rates;"
        self.cursor.execute(sql)
        self.connection.commit()
    
    
    def createRatesFromFile(self):
        text = pd.read_excel("/in/rates.xlsx")
        text = text.to_numpy().tolist()
        for t in text:
            product_id = t[0]
            rate = t[1]
            scope = t[2]
            sql =  f"INSERT INTO Rates (`product_id`, `rate`, `scope`) VALUES ('{product_id}', {rate}, '{scope}')"    
            self.cursor.execute(sql)
        self.connection.commit()
    
        
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
        

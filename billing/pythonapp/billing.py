from flask import Flask 
import os
from database import *
import mysql.connector

app = Flask(__name__)


DB=DataBase('billdb','root')


@app.route("/provider", methods=['POST'])
def CreateProvider():
    name='Provider'+str(DB.getProvidersCount())
 
    DB.addProvider(name)

    return 200

    
@app.route("/provider/<id>",methods=['PUT'])
def ChangeName(id):
    new_name=''
    DB.changeProviderName(id,new_name)
    return 200




    

if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)
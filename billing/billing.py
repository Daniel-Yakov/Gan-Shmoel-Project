from flask import Flask 
from database import *

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
    app.run()
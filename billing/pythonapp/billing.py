from flask import Flask, jsonify
from database import *

app = Flask(__name__)

DB=DataBase("billdb", "root")

def my_generator():
    i=1
    while i>0:
        i+=1
        yield i
gen = my_generator()

@app.route("/health", methods=["GET"])
def isHealthy():
    return jsonify("OK"),200


@app.route("/provider", methods=['POST'])
def CreateProvider():
    name='Provider'+str(next(gen))
    DB.addProvider(name)
    id={"id":DB.GetProviderByName(name)} 
    return jsonify(id)

    
@app.route("/provider/<id>",methods=['PUT'])
def ChangeName(id):
    new_name='Provider'+str(next(gen))
    DB.changeProviderName(id,new_name)
    return "changed"

    

if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)
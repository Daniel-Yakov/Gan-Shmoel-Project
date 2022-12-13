from flask import Flask, request
import json
import os

app = Flask(__name__)


@app.get('/health')
def health_check():
    return "OK"

@app.post('/trigger')
def trigger():
    
    # data = json.loads(request)
    # print(f'action = {data["action"]}, repository.branches_url={data["repository.branches_url"]}')
    return "OK"


app.run(host="0.0.0.0")
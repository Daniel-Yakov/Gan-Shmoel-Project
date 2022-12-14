from flask import Flask, request
import json
import subprocess

app = Flask(__name__)


@app.get('/health')
def health_check():
    return "OK"

@app.post('/trigger')
def trigger():


    exit_code = subprocess.call('./test-env.sh')
    
    # success
    # if exit_code == 0:
        # send mail of success 
        # deploy the new image

    # failure
    # else:
        # send mails of failure
        
    
     
    
    # data = json.loads(request)
    # print(f'action = {data["action"]}, repository.branches_url={data["repository.branches_url"]}')
    return "OK"


app.run(host="0.0.0.0")
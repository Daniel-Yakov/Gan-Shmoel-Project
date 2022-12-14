from flask import Flask, request
from flask_mail import Mail,Message
import json
import subprocess

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'yuval.klechvsky44@gmail.com'
app.config['MAIL_PASSWORD'] = 'jhmsyydwqjkhyslg'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER']= 'yuval.klechvsky44@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail = Mail(app)

def succeed_email():
    msg = Message('Test Status', recipients = ["daniel577000@gmail.com"])
    msg.add_recipient("DavidovDav@outlook.com")
    msg.body = "Hello the all the testing was succeeded \n You can see Your report here \n\n\n "
    with app.open_resource("report.txt") as report:
        msg.attach("report.txt","text/txt", report.read())
    mail.send(msg)
           
  
def fail_email():
     msg = Message('Test Status', recipients = ["daniel577000@gmail.co"])
     msg.add_recipient("DavidovDav@outlook.com")
     msg.body = "Hello the all the testing was failed \n You can see Your report here"
     with app.open_resource("report.txt") as report:
        msg.attach("report.txt","text/txt", report.read())
     mail.send(msg)


@app.get('/health')
def health_check():
    return "OK"

@app.post('/trigger')
def trigger():
    succeed_email()
    

    #exit_code = subprocess.call('./test-env.sh')
    
    # success
   # if exit_code == 0:
      
       

    

    # failure
    #else:
        #fail_email()

        
    
     
    
    # data = json.loads(request)
    # print(f'action = {data["action"]}, repository.branches_url={data["repository.branches_url"]}')
    return "Mail has been sent to you, go check it !"


app.run(host="0.0.0.0")
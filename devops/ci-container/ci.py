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
    msg.add_recipient("kareem.smartdoc@gmail.com")
    msg.add_recipient("shoval123055@gmail.com")
    msg.body = "Hello the all the testing was succeeded \n You can see Your report added in this mail\n\n "
    with app.open_resource("report.txt") as report:
        msg.attach("report.txt","text/txt", report.read())
    mail.send(msg)
           
  
def fail_email():
     msg = Message('Test Status', recipients = ["daniel577000@gmail.co"])
     msg.add_recipient("DavidovDav@outlook.com")
     msg.add_recipient("kareem.smartdoc@gmail.com")
     msg.add_recipient("shoval123055@gmail.com")
     msg.body = "Hello the all the testing was failed \n You can see Your report added in this mail\n\n"
     with app.open_resource("report.txt") as report:
        msg.attach("report.txt","text/txt", report.read())
     mail.send(msg)


@app.get('/health')
def health_check():
    return "OK"

@app.post('/trigger')
def trigger():
    
    # create test-env
    exit_code = subprocess.call('./test-env.sh')
    
    # removes the test-env
    subprocess.call('./remove-test-env.sh')
    
    # success, deploy new containers in prod-env
    if exit_code == 0:
      subprocess.call('./prod-env.sh')
       
    # failure
    else:
        fail_email()

    return "OK"


app.run(host="0.0.0.0")
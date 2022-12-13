from flask import Flask
from flask_mail import Mail,Message


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





@app.route("/trigger")
def index():
  msg = Message('Test Status', recipients = ['bagoxi8407@nazyno.com'])
  #msg.add_recipient("somebodyelse@example.com")
  msg.body = "Hello you have a failer"
  mail.send(msg)
  return "Mail sent!"

if __name__ == '__main__':
   app.run(debug = True)



from flask import Flask
from flask_mail import Mail, Message

app =Flask(__name__)
mail=Mail(app)


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'phardik2130@gmail.com'
app.config['MAIL_PASSWORD'] = 'ikapucsieflapchx'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
@app.route("/check")
def index():
   msg = Message('Hello', sender = 'phardik2130@gmail.com', recipients = ['phardik2130@gmail.com'])
   msg.body = "click here to verify your account : http://localhost:5000/api/email/verify/{}".format(token)
   mail.send(msg)
   return "Mail Sent please check"

if __name__ == '__main__':
   app.run(debug = True)
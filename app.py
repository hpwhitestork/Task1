from flask import Flask,jsonify,request,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_smorest import Blueprint , abort
from marshmallow import Schema,fields,validate, ValidationError
from flask_mail import Mail,Message
from itsdangerous import URLSafeTimedSerializer
import psycopg2
from passlib.hash import pbkdf2_sha256




app = Flask(__name__)



app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'phardik2130@gmail.com'
app.config['MAIL_PASSWORD'] = 'ikapucsieflapchx'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config["JWT_SECRET_KEY"] = 'secert-key'
mail=Mail(app)
s = URLSafeTimedSerializer(app.config["JWT_SECRET_KEY"])


app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:admin@localhost:5432/Email"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False

db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    __tablename__="user_table"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100),unique=True)
    display_name = db.Column(db.String(100))
    email = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(255))
    email_verified_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at =  db.Column(db.DateTime, default=datetime.utcnow)
    updated_at =  db.Column(db.DateTime)
    

class UserSchema(Schema):
    id=fields.Integer()
    username=fields.String(validate=validate.Length(min=3,max=100),error_messages={"required": "Please enter valid length (max length is 3)"})
    email = fields.String()
    display_name = fields.String(validate=validate.Length(min=3,max=100),error_messages={"required": "Please enter valid length"})
    password = fields.String()
    email_verified_at = fields.String()
    status = fields.String()
    created_at = fields.Date()
    updated_at = fields.Date()



class VerificationRequest(db.Model):
    email = db.Column(db.String(120), primary_key=True)
    token = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.get("/api/email/verify/<token>")
def verify_email(token):
    token_req = VerificationRequest.query.filter(VerificationRequest.token == token).first()
    if not token_req: 
        return jsonify({'message': 'Token invalid'}), 400
    user = User.query.filter(User.email == token_req.email).first()
    if not user: 
        return jsonify({'message': 'user not found'}), 400
    if user.email_verified_at: 
       return jsonify({'message': 'already email verified'}), 400
   
    user.email_verified_at = datetime.now()
    db.session.add(user)
    db.session.commit()
    
    # delete1=VerificationRequest.query.filter(VerificationRequest.token == token).delete()
    db.session.delete(token_req)
    db.session.commit()

    return jsonify({'message': 'email verified successfully.'}), 200
    

    # user = VerificationRequest.query.filter_by(token=token).first()
    # if user.token:
    #     db.session.delete(user)
    #     db.session.commit()
    # return{"messsage":" token deleted"}
   
@app.post("/api/register")
def register_api():
    data = request.get_json()
    if User.query.filter(User.username == data["username"]).first():
        #abort (409,message="Username already exists.")
        return jsonify({'message': 'Username already exists.'}), 409

    if User.query.filter(User.email == data["email"]).first():
        return jsonify({'message': 'Email already exists.'}), 409

    token = str(uuid.uuid4())

    user_data = User(**data)
    db.session.add(user_data)
    db.session.commit()
    
    validation_req = VerificationRequest()
    validation_req.email = user_data.email
    validation_req.token = token
    db.session.add(validation_req)
    db.session.commit()
   
    msg = Message('Hello', sender = 'phardik2130@gmail.com', recipients = ['phardik2130@gmail.com'])
    msg.body = "click here to verify your account : http://localhost:5000/api/email/verify/{}".format(validation_req.token)
    mail.send(msg)

    return jsonify({'message': 'User created  successfully.'}), 200

@app.post("/auth")
def register_auth():
    data = request.get_json()
    email = data.get('email')
    created_at = data.get('created_at')

    user = User.query.filter_by(email=email).first()
    
    access_token = create_access_token(identity = user.id)   
    return{"email":email,"acess_token":access_token,"created_at":created_at}
   
   
    email=request.form['email']
  # token = s.dumps(gmail, salt = 'email-confirmation-key')
    msg=Message(subject='Link',sender='phardik2130@gmail.com',recipients=[email])
    msg.body = "Hello this is my first mail app"
    # link = url_for('confirm',external = True)
    # msg.body = "link" + link
    mail.send(msg)
    return jsonify({'message': 'mail send successfully.'})





@app.get("/get_user")
def get_user_data():
    user_data=User.query.all()
    
    serializer= UserSchema(many=True)

    data=serializer.dump(user_data)
   

    return jsonify(
        data
    )

@app.delete("/user_del/<string:token_req>")
def delete_user(token_req):
    
    user = VerificationRequest.query.filter_by(token=token_req).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return{"messsage":"token deleted"}
    
    return{"message":"token not found"}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)







   
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

import os




app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] ="postgres://darasa_user:VxWloJVvTk5XoRxfeaSNtL24z3fmWb1m@dpg-cp8r1kf109ks739v9s9g-a/darasa"
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://darasa_user:VxWloJVvTk5XoRxfeaSNtL24z3fmWb1m@dpg-cp8r1kf109ks739v9s9g-a/darasa')


app.config["SQLALCHEMY_TRACK_MODIFICATION"] = True
app.config["SECRET_KEY"] = "92256b9d8a05214dab4362d83c9e17d1"



app.json.compact=False
db =SQLAlchemy()
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
db.init_app(app)
CORS(app, origins="https://studentportal-yaoq.onrender.com")
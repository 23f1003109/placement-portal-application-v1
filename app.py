from constraints import *
from flask import Flask, rennder_template
from config import Config
from extensions import db
from models import *


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


with app.app_context():
    db.create_all()
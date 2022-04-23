# __init__.py
from flask import Flask
from flask_bcrypt import Bcrypt  



application = Flask(__name__)

bcrypt = Bcrypt(application)
application.secret_key = 'Open_Sesame'
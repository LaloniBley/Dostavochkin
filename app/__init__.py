from flask import Flask
from flask_wtf import FlaskForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dostavochkin-secret-key-2026'
app.config['WTF_CSRF_ENABLED'] = False

from app import routes
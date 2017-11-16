from flask import Flask
from flask import jsonify
app = Flask(__name__, static_url_path='')

from . import routes

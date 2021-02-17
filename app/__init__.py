from flask import Flask

app = Flask(__name__)

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "game_reviews"

settings = {
    'MONGODB_SERVER': MONGODB_SERVER,
    'MONGODB_PORT': MONGODB_PORT,
    'MONGODB_DB': MONGODB_DB
}

import db
coll = db.get_collection(db.get_db(settings, False), 'reviews')

from app import routes
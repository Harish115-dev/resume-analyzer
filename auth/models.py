import bcrypt 
from db.mongodb import db
from datetime  import datetime


class user(db.Document):
    meta={
        "collection":"user",
        "indexes":"emails"
    }
    name=db.StringField()

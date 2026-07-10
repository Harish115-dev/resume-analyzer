import bcrypt 
from db.mongodb import db
from datetime import datetime, timezone

class user(db.Document):
    meta = {
    "collection": "users",
    "indexes": ["email"]
    }
    name = db.StringField(required=True, max_length=50)
    email = db.EmailField(required=True, unique=True)
    password_hash = db.StringField(required=True)

    is_active = db.BooleanField(default=True)
    created_at = db.DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = db.DateTimeField(default=lambda: datetime.now(timezone.utc))


    def set_password(self, plain_text_password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(plain_text_password.encode("utf-8"), salt).decode("utf-8")
    def check_password(self,plain_text_password):
         return bcrypt.checkpw(plain_text_password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def save(self, *args, **kwargs):
        self.updated_at=datetime.now(timezone.utc)
        return super(user,self).save(*args,**kwargs)

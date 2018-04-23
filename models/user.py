from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.column(db.Integer, primaryKey=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def json(self):
        return {"id": self.id, "username": self.username, "password": self.password}


    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

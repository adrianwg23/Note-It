from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String())

    notes = db.relationship("NoteModel", lazy="dynamic")

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def item_json(self):
        return {"user_id": self.id, "username": self.username, "notes": [note.json() for note in self.notes.all()]}

    def user_json(self):
        return {"user_id": self.id, "username": self.username, "password": self.password}

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

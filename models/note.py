from db import db


class NoteModel(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    note = db.Column(db.String)
    priority = db.Column(db.Integer)
    updated_at = db.Column(db.BigInteger)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("UserModel")

    def __init__(self, title, note, priority, updated_at, user_id):
        self.title = title
        self.note = note
        self.priority = priority
        self.updated_at = updated_at
        self.user_id = user_id

    def json(self):
        return {"note_id": self.id, "title": self.title,
                "note": self.note, "priority": self.priority,
                "updated_at": self.updated_at, "user_id": self.user_id}

    @classmethod
    def find_by_note_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

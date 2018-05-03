from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.note import NoteModel
from models.user import UserModel

parser = reqparse.RequestParser()
parser.add_argument("title", type=str, required=False)
parser.add_argument("note", type=str, required=False)
parser.add_argument("priority", type=int, required=False)
parser.add_argument("user_id", type=int, required=True, help="Every note needs a user id.")


class Note(Resource):
    @jwt_required
    def get(self, note_id):
        note = NoteModel.find_by_note_id(note_id)
        if note:
            return note.json()
        return {"msg": "note not found"}, 404

    @jwt_required
    def put(self, note_id):
        data = parser.parse_args()
        note = NoteModel.find_by_note_id(note_id)

        if note is None:
            note = NoteModel(**data)
        else:
            note.title = data["title"]
            note.note = data["note"]
            note.priority = data["priority"]

        try:
            note.save_to_db()
        except:
            return {"msg": "An error occurred saving the item."}, 500

        return note.json()

    @jwt_required
    def delete(self, note_id):
        note = NoteModel.find_by_note_id(note_id)
        if note:
            note.delete_from_db()

        return{"msg": "note deleted"}


class NewNote(Resource):
    @jwt_required
    def post(self):
        data = parser.parse_args()
        note = NoteModel(**data)

        try:
            note.save_to_db()
        except:
            return {"msg": "An error occurred saving the item."}, 500

        return note.json(), 201


class NoteList(Resource):
    @jwt_required
    def get(self, username):
        user = UserModel.find_by_username(username)
        if user:
            return user.item_json()
        return {"msg": "user not found"}, 404
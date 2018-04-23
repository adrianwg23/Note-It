from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.note import NoteModel
from models.user import UserModel

parser = reqparse.RequestParser()
parser.add_argument("user_id", type=float, required=True, help="Every item needs a user id!")


class Note(Resource):
    @jwt_required
    def get(self, _id):
        note = NoteModel.find_by_note_id(_id)
        if note:
            return note.json()
        return {"message", "note not found"}, 404

    @jwt_required
    def put(self, _id):
        data = parser.parse_args()
        note = NoteModel.find_by_note_id(_id)

        if note is None:
            note = NoteModel(**data)
        else:
            note.title = data["title"]
            note.note = data["note"]
            note.priority = data["priority"]

        try:
            note.save_to_db()
        except:
            return {"message": "An error occurred saving the item."}, 500

        return note.json()

    @jwt_required
    def delete(self, _id):
        pass


class NewNote(Resource):
    @jwt_required
    def post(self):
        data = parser.parse_args()
        note = NoteModel(data["user_id"], data["title"], data["note"], data["priority"])

        try:
            note.save_to_db()
        except:
            return {"message": "An error occurred saving the item."}, 500

        return note.json(), 201


class NoteList(Resource):
    def get(self, username):
        user = UserModel.find_by_username(username)
        if user:
            return user.item_json()
        return {"message": "user not found"}, 404
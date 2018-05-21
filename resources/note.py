from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.note import NoteModel
from models.user import UserModel

parser = reqparse.RequestParser()
parser.add_argument("title", type=str, required=False)
parser.add_argument("note", type=str, required=False)
parser.add_argument("priority", type=int, required=False)
parser.add_argument("updated_at", type=int, required=True, help="Every note needs a time stamp.")
parser.add_argument("user_id", type=int, required=True, help="Every note needs a user id.")

sync_parser = reqparse.RequestParser()
sync_parser.add_argument("note_list", type=list, required=True)


class Note(Resource):
    @jwt_required
    def get(self, note_id):
        note = NoteModel.find_by_note_id(note_id)
        if note:
            return note.json()
        return {"message": "note not found"}, 404

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
            note.updated_at = data["updated_at"]

        try:
            note.save_to_db()
        except:
            return {"message": "An error occurred saving the item."}, 500

        return note.json()

    @jwt_required
    def delete(self, note_id):
        note = NoteModel.find_by_note_id(note_id)
        if note:
            note.delete_from_db()

        return{"message": "note deleted"}


class NewNote(Resource):
    @jwt_required
    def post(self):
        data = parser.parse_args()
        note = NoteModel(**data)

        try:
            note.save_to_db()
        except:
            return {"message": "An error occurred saving the item."}, 500

        return note.json(), 201


class NoteList(Resource):
    @jwt_required
    def get(self, username):
        user = UserModel.find_by_username(username)
        if user:
            return user.item_json()
        return {"message": "user not found"}, 404


class Sync(Resource):
    @jwt_required
    def post(self, username):
        user = UserModel.find_by_username(username)
        my_dict = user.item_json()
        size = 0

        client_note_list = sync_parser.parse_args()
        server_note_list = my_dict["notes"]

        if len(client_note_list) - len(server_note_list) >= 0:
            size = len(client_note_list)
        else:
            size = len(server_note_list)

        for x in range(size):
            client_note = client_note_list.get(x)
            server_note = server_note_list.get(x)

            if client_note["note_id"] == server_note["note_id"]:
                # If the user updated a note client side
                if client_note["updated_at"] != server_note["updated_at"]:
                    note = NoteModel.find_by_note_id(client_note["note_id"])
                    note.title = client_note["title"]
                    note.note = client_note["note"]
                    note.priority = client_note["priority"]
                    note.updated_at = client_note["updated_at"]
                    note.save_to_db()
            # If user added a note client side
            elif client_note["note_id"] > server_note["note_id"]:
                note = NoteModel(**client_note)
                note.save_to_db()
            # If user deleted a note client side
            elif client_note["note"] < server_note["note_id"]:
                note = NoteModel.find_by_note_id(server_note["note_id"])
                note.delete_from_db()

        return {"notes": client_note_list}
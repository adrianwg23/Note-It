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
sync_parser.add_argument("notes", type=list, required=True)


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

        return {"message": "note deleted"}


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
        data = sync_parser.parse_args()

        client_note_list = data["notes"]
        server_note_list = my_dict["notes"]

        client_note_id_list = [x["note_id"] for x in client_note_list]
        server_note_id_list = [x["note_id"] for x in server_note_list]

        a = set(client_note_id_list)
        b = set(server_note_id_list)

        add_list = [x for x in client_note_list if x["note_id"] not in b]
        delete_list = [x for x in server_note_list if x["note_id"] not in a]
        intersection_list = [x for x in client_note_list if x["note_id"] in b]

        for add_note in add_list:
            note = NoteModel(**add_note)
            note.save_to_db()

        for delete_note in delete_list:
            note = NoteModel.find_by_note_id(delete_note["note_id"])
            note.delete_from_db()

        for intersection_note in intersection_list:
            note = NoteModel.find_by_note_id(intersection_note["note_id"])
            note.title = intersection_note["title"]
            note.note = intersection_note["note"]
            note.priority = intersection_note["priority"]
            note.updated_at = intersection_note["updated_at"]


        return {"notes": add_list}

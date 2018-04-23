from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models.note import NoteModel


class Note(Resource):
    pass


class NoteList(Resource):
    pass
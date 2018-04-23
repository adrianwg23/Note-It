import os

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.note import Note, NoteList
from resources.user import UserRegister, UserList

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api = Api(app)

api.add_resource()

app.config["JWT_SECRET_KEY"] = '\x9a\xf5\xba.qTE<e\xd2\xd4\x1c\x13\xa2\x83\x8a\x90\xbb\xfe\xb5%\xd0\xa1#'
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)

api.add_resource(Note, "/note/<string:id>")
api.add_resource(NoteList, "/notes")
api.add_resource(UserRegister, "/register")
api.add_resource(UserList, "/users")


if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
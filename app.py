import os

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.note import Note, NewNote, NoteList, Sync
from resources.user import UserRegister, UserLogin, UserLogoutAccess, UserLogoutRefresh, TokenRefresh, UserList
from models.revoked_token import RevokedTokenModel

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
api = Api(app)


# uncomment this if running locally
# @app.before_first_request
# def create_tables():
#      db.create_all()


app.config["JWT_SECRET_KEY"] = '\x9a\xf5\xba.qTE<e\xd2\xd4\x1c\x13\xa2\x83\x8a\x90\xbb\xfe\xb5%\xd0\xa1#'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = False
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)


api.add_resource(Sync, "/sync/<string:username>")
api.add_resource(Note, "/note/<int:note_id>")
api.add_resource(NewNote, "/note/new")
api.add_resource(NoteList, "/notes/<string:username>")
api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogoutAccess, "/logout/access")
api.add_resource(UserLogoutRefresh, "/logout/refresh")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserList, "/users")


if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
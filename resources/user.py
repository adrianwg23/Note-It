from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import UserModel
from models.revoked_token import RevokedTokenModel
from flask_jwt_extended import (
    create_access_token, jwt_refresh_token_required,
    create_refresh_token, get_jwt_identity, get_raw_jwt
)

parser = reqparse.RequestParser()
parser.add_argument("username", type=str, required=True, help="This field cannot be blank.")
parser.add_argument("password", type=str, required=True, help="This field cannot be blank.")


class UserRegister(Resource):
    def post(self):
        data = parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": "A user with that username already exists"}, 400

        user = UserModel(data["username"], generate_password_hash(data["password"]))
        try:
            user.save_to_db()
            return {"message": "User created successfully"}, 201
        except:
            return {"message": "An error occurred creating the user"}, 500


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        user = UserModel.find_by_username(data["username"])
        if user and check_password_hash(user.password, data["password"]):
            ret = {
                "access_token": create_access_token(identity=user.username),
                "refresh_token": create_refresh_token(identity=user.username),
                "user_id": user.id
            }
            return ret, 200

        return {"message": "Bad username or password"}, 401


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        ret = {
            "access_token": create_access_token(identity=current_user)
        }
        return ret, 200


class UserList(Resource):
    @jwt_required
    def get(self):
        return {"users": [user.user_json() for user in UserModel.query.all()]}
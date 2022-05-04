from flask_restful import Resource
from util import verify_token, verify_admin_token
from database import Database


class GroupsInterface(Resource):
    def get(self):
        from main import tokens
        token = verify_token()
        user_id = tokens[token]
        db = Database(f"{user_id}.groups")
        groups = db.query("SELECT * FROM groups")
        db.shutdown()
        return [_[0] for _ in groups]

    def post(self):
        return {

        }

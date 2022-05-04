from flask_restful import Resource, abort

from util import JSON


class UserInterface(Resource):
    def get(self, userID):
        from main import user_db

        user = user_db.get(id=userID)
        if type(user) is not User:
            abort(500, message="Error")

        return user.get_dict()

    def put(self, userID):
        # TODO update user
        return

    def delete(self, userID):
        # TODO delete user
        return


class User(JSON):
    ID = None
    name = None
    profilePicture = None
    status = None
    __passwordHash = None
    __admin = None


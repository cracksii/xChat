from flask_restful import Resource, abort

from util import JSON, verify_token, verify_admin_token, is_group_admin, is_member_of_group, add_to_group


class GroupInterface(Resource):
    def get(self, groupID):
        from main import group_db

        group = group_db.get(id=groupID)
        if type(group) is not Group:
            abort(500, message="Error")

        return group.get_dict()

    def put(self, groupID):
        return {
            "status": 200
        }

    def delete(self, groupID):
        return {
            "status": 200
        }


class GroupManageInterface(Resource):
    def post(self, groupID, userID):
        from main import tokens
        token = verify_token()

        if not verify_admin_token(token) and not is_group_admin(tokens[token], groupID):
            abort(401, message=f"You do not have permission to add users to group {groupID}")

        if is_member_of_group(userID, groupID):
            abort(400, message=f"User {userID} is already part of group {groupID}")

        add_to_group(userID, groupID)

    def delete(self, groupID, userID):
        pass


class Group(JSON):
    ID = None
    adminID = None
    name = None
    description = None
    groupPicture = None
    __memberTable = None


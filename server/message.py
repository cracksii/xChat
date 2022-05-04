from flask_restful import Resource, abort
from util import JSON, verify_token, verify_admin_token, is_author_of_message, is_member_of_group


class MessageInterface(Resource):
    def get(self, messageID):
        token = verify_token()
        from main import message_db, tokens
        msg = message_db.get(ID=messageID)
        if type(msg) != Message:
            abort(400, message="Message not found")

        if not is_member_of_group(tokens[token], msg.groupID):
            abort(401, message="You are not allowed to receive this message")

        return msg.get_dict()

    def put(self, messageID):
        from main import tokens, parser, message_db

        token = verify_token()
        if not is_author_of_message(tokens[token], messageID) and not verify_admin_token(token):
            abort(401, message="Not allowed to edit message")
        json = parser.parse_args()["json"]

        if json is None:
            abort(400, message="Missing parameter 'json'")

        print(json)
        msg = UpdateMessage.from_json(json)
        print(msg.__dict__)
        msg = message_db.update(msg)
        return msg

    def delete(self, messageID):
        from main import tokens, message_db
        token = verify_token()
        token = verify_token()
        if not is_author_of_message(tokens[token], messageID) and not verify_admin_token(token):
            abort(401, message="Not allowed to delete message")

        msg = message_db.get(id=messageID)
        msg.deleted = True
        msg.content = "This message was deleted"
        message_db.update(msg)

        return message_db.get(id=messageID).get_dict()


class Message(JSON):        # Server-side representation of a message
    ID = None
    authorID = None
    groupID = None
    content = None
    timestamp = None
    deleted = None


class UpdateMessage(JSON):
    ID = None
    content = None

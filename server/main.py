import datetime

from flask import Flask
from flask_restful import Api
from flask_restful.reqparse import RequestParser

from database import UserDatabase, MessageDatabase, GroupDatabase
from tokens import TokenInterface
from groups import GroupsInterface
from group import GroupInterface, GroupManageInterface
from messages import MessagesInterface
from message import MessageInterface
from user import UserInterface


app = Flask(__name__)
api = Api(app)

parser = RequestParser()
parser.add_argument("timespan")
parser.add_argument("json")
parser.add_argument("content")


tokens = {}
user_db = UserDatabase()
message_db = MessageDatabase()
group_db = GroupDatabase()

api.add_resource(TokenInterface,    "/token")
api.add_resource(GroupsInterface,   "/groups")
api.add_resource(GroupInterface,    "/group/<int:groupID>")
api.add_resource(MessagesInterface, "/messages/<int:groupID>")
api.add_resource(MessageInterface,  "/message/<int:messageID>")
api.add_resource(UserInterface,     "/user/<int:userID>")

api.add_resource(GroupManageInterface, "/group/<int:groupID>/<int:userID>")


@app.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Token"
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)


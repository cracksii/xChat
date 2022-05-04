from flask import request, Request
from flask_restful import Resource, abort
from datetime import datetime
from util import verify_token, is_member_of_group
from json import loads


class MessagesInterface(Resource):
    def get(self, groupID):
        from main import parser, message_db, tokens
        token = verify_token()

        if not is_member_of_group(tokens[token], groupID):
            abort(401, message="User is not part of group")

        args = parser.parse_args()

        if args["timespan"] == "*":
            msgs = message_db.get(groupID=groupID)
            if type(msgs) == list:
                return [_.ID for _ in msgs]
            elif msgs is not None:
                return [msgs.ID]
            else:
                print("No messages found")
                return []

        if args["timespan"] is None or "-" not in args["timespan"] or len(args["timespan"].split("-")) != 2:
            abort(400, message="Error while parsing parameter 'timestamp'")

        start = datetime.fromtimestamp(float(args["timespan"].split("-")[0]))
        end = datetime.fromtimestamp(float(args["timespan"].split("-")[1]))

        if start > end:
            abort(400, message="Invalid timestamps")

        msgs = message_db.get(groupID=groupID, sql=f"timestamp BETWEEN {start.timestamp()} AND {end.timestamp()}")
        if type(msgs) == list:
            return [_.ID for _ in msgs]
        else:
            abort(400, message="No messages found")

    def post(self, groupID):
        from main import tokens, parser, message_db

        token = verify_token()
        print(is_member_of_group(tokens[token], groupID))
        if not is_member_of_group(tokens[token], groupID):
            abort(401, message="Not part of group")

        args = parser.parse_args()
        if args["content"] is None or args["content"] == "":
            abort(400, message="Error while parsing parameter 'content'")

        content = args["content"]
        msg = message_db.insert(tokens[token], groupID, content)
        return msg.get_dict()
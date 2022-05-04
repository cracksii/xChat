from flask_restful import Resource, abort
from flask import request
from secrets import token_urlsafe
from util import JSON, check_password
from base64 import b64decode, b64encode


class TokenInterface(Resource):
    def get(self):
        from main import tokens
        token = token_urlsafe(60)

        if "Authorization" not in request.headers:
            abort(400, message="Missing header 'Authorization'")

        auth_header = b64decode(request.headers["Authorization"].encode("utf-8")).decode("utf-8")

        if ":" not in auth_header or len(auth_header.split(":")) != 2:
            abort(400, message="Wrong format for header 'Authorization'")

        user, password_hash = auth_header.split(":")

        if not check_password(user, password_hash):
            abort(401, message="Invalid password")

        if user in tokens.values():
            del tokens[list(tokens.keys())[list(tokens.values()).index(user)]]
        tokens[token] = user

        print(tokens)

        return {"Token": b64encode(token.encode("utf-8")).decode("utf-8")}, 200, {
            "Token": b64encode(token.encode("utf-8")).decode("utf-8")
        }


class Token(JSON):
    token = None
    isAdminToken = None

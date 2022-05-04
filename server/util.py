from flask_restful import abort
from flask import request
from base64 import b64decode
import json as js
from database import Database


class JSON:
    def to_json(self):
        dictionary = type(self).__dict__.copy()
        dictionary.update({k: v for k, v in self.__dict__.items() if v})

        return js.dumps({k: v for k, v in dictionary.items() if not k.startswith("_") and not str(v).startswith("<")})

    def get_dict(self):
        dictionary = type(self).__dict__.copy()
        dictionary.update({k: v for k, v in self.__dict__.items() if v})

        return {k: v if v is not None else 0 for k, v in dictionary.items() if not k.startswith("_") and not str(v).startswith("<")}

    @classmethod
    def from_json(cls, json):
        try:
            instance = cls()
            json = js.loads(json)
            for key, value in json.items():
                if key in cls.__dict__:
                    instance.__dict__[key] = value
                else:
                    raise Exception(f"Trying to initialize not defined property '{key}'")
            return instance
        except js.decoder.JSONDecodeError:
            print("JSON ERROR")
            abort(400, message="Invalid JSON")

    @classmethod
    def create(cls, **kwargs):
        instance = cls()
        instance.__dict__ = kwargs
        return instance


def verify_token():
    from main import tokens

    if "Token" not in request.headers:
        abort(401, message="Token required")
    elif b64decode(request.headers["Token"]).decode("utf-8") not in tokens.keys():
        abort(401, message="Invalid token")
    else:
        return b64decode(request.headers["Token"]).decode("utf-8")


def verify_admin_token(token):
    return True


def is_group_admin(userID, groupID):
    return True


def is_member_of_group(userID, groupID):
    return True

def is_author_of_message(userID, messageID):
    return True


def check_password(userID, password_hash):
    from main import user_db
    from user import User

    user = user_db.get(id=userID)
    if type(user) != User:
        return False
    if user.__passwordHash == password_hash:
        return True

    return False


def add_to_group(user_id, group_id):
    gdb = Database(f"{user_id}.groups")

    if group_id in [_[0] for _ in gdb.query(f"SELECT * FROM groups")]:
        gdb.shutdown()
        return

    gdb.query(f"INSERT INTO groups VALUES ({group_id})")
    gdb.shutdown()

    udb = Database(f"{group_id}.members")
    udb.query(f"INSERT INTO users VALUES ({user_id})")
    udb.shutdown()


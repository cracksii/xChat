import sqlite3
from datetime import datetime
import threading


class Database:
    def __init__(self, name):
        self._db = sqlite3.connect("databases/" + name, check_same_thread=False)
        self._cursor = self._db.cursor()
        self.lock = threading.Lock()

    def shutdown(self):
        self._db.close()

    def query(self, sql, fetch=True):
        try:
            self.lock.acquire(True)
            self._cursor.execute(sql)
            self._db.commit()
            if fetch:
                return self.fetch()
        except sqlite3.OperationalError as e:
            print(sql)
            raise e
        finally:
            self.lock.release()

    def fetch(self):
        return self._cursor.fetchall()


class UserDatabase:
    def __init__(self):
        self.db = Database("users.db")
        self.db.query("CREATE TABLE IF NOT EXISTS users (id int, name text, passwordHash text, profilePicture text, "
                      "status text, admin bool)")
        self.next_id = len(self.db.query("SELECT * FROM users")) + 1

    def insert(self, name, password_hash, profilePicture="", status="", admin=False):
        from user import User

        self.db.query(f'INSERT INTO users VALUES ({self.next_id}, "{name}", "{password_hash}", "{profilePicture}", '
                      f'"{status}", {admin})')

        gdb = Database(f"{self.next_id}.groups")
        gdb.query("CREATE TABLE groups (ID int)")
        gdb.shutdown()

        self.next_id += 1
        return User.create(name=name, profilePicture=profilePicture, status=status, _admin=admin)

    def get(self, **kwargs):
        from user import User

        sql = f'SELECT * FROM users WHERE'
        for key in kwargs:
            if key != "sql":
                sql += f" {key}=" if list(kwargs.keys()).index(key) == 0 else f" and {key}="
                sql += f'{kwargs[key]}' if type(kwargs[key]) == int else f'"{kwargs[key]}"'
            else:
                sql += f" and {kwargs[key]}"
                break

        data = self.db.query(sql)
        if len(data) > 1:
            return [User.create(ID=id, name=name, __passwordHash=pwd, profilePicture=profilePicture, status=status,
                                __admin=bool(admin)) for id, name, pwd, profilePicture, status, admin in data]
        elif len(data) == 1:
            data = data[0]
            return User.create(ID=data[0], name=data[1], __passwordHash=data[2], profilePicture=data[3],
                               status=data[4], __admin=bool(data[5]))
        else:
            return None

    def delete(self, **kwargs):
        sql = f'DELETE FROM users WHERE {list(kwargs.keys())[0]}='
        sql += f'{list(kwargs.values())[0]}' if type(
            list(kwargs.values())[0]) == int else f'"{list(kwargs.values())[0]}"'

        print(sql)
        self.db.query(sql)

    def update(self):
        pass


class MessageDatabase:
    def __init__(self):
        self.db = Database("messages.db")
        self.db.query("CREATE TABLE IF NOT EXISTS messages (ID int, authorID int, groupID int, content text, timestamp"
                      " int, deleted bool)")
        self.next_id = len(self.db.query("SELECT * FROM messages")) + 1

    def insert(self, author_id, group_id, content):
        from message import Message

        ts = datetime.now().timestamp()
        self.db.query(f'INSERT INTO messages VALUES ({self.next_id}, {author_id}, {group_id}, "{content}", {ts}, 0)')

        self.next_id += 1
        return Message.create(ID=self.next_id - 1, authorID=author_id, groupID=group_id, content=content, timestamp=ts,
                              deleted=False)

    def get(self, **kwargs):
        from message import Message

        sql = f'SELECT * FROM messages WHERE'
        for key in kwargs:
            if key != "sql":
                sql += f" {key}=" if list(kwargs.keys()).index(key) == 0 else f" and {key}="
                sql += f'{kwargs[key]}' if type(kwargs[key]) == int else f'"{kwargs[key]}"'
            else:
                sql += f" and {kwargs[key]}"
                break

        print(sql)
        data = self.db.query(sql)
        if data == None:
            return None

        if len(data) > 1:
            return [Message.create(ID=id, authorID=author_id, groupID=group_id, content=content, timestamp=timestamp,
                                   deleted=deleted) for id, author_id, group_id, content, timestamp, deleted in data]
        elif len(data) == 1:
            data = data[0]
            return Message.create(ID=data[0], authorID=data[1], groupID=data[2], content=data[3], timestamp=data[4],
                                  deleted=data[5])
        else:
            return None

    def update(self, msg):
        from message import Message, UpdateMessage
        assert isinstance(msg, Message) or isinstance(msg, UpdateMessage)

        old_msg = self.get(id=msg.ID)
        updates = {}
        for k, v in msg.__dict__.items():
            if old_msg.__dict__[k] != v:
                updates[k] = v

        if len(updates) == 0:
            return msg.get_dict()

        sql = "UPDATE messages SET "
        for k, v in updates.items():
            sql += f'{k} = "{v}", ' if type(v) is not int else f"{k} = {v}, "
        sql = sql[:-2] + f" WHERE ID={msg.ID}"
        print(sql)
        self.db.query(sql)
        return self.get(id=msg.ID).get_dict()


class GroupDatabase:
    def __init__(self):
        self.db = Database("groups.db")
        self.db.query("CREATE TABLE IF NOT EXISTS groups (ID int, adminID int, name text, description text, "
                      "memberTable text, groupPicture text)")
        self.next_id = len(self.db.query("SELECT * FROM groups")) + 1

    def insert(self, name, admin_id, description="Nothing here yet", group_picture=""):
        from group import Group
        member_table = f"{self.next_id}.members"

        self.db.query(f'INSERT INTO groups VALUES ({self.next_id}, {admin_id}, "{name}", "{description}", '
                      f'"{member_table}", "{group_picture}")')

        udb = Database(f"{self.next_id}.members")
        udb.query("CREATE TABLE users (ID int)")
        udb.shutdown()

        gdb = Database(f"{admin_id}.groups")
        gdb.query(f"INSERT INTO groups VALUES ({self.next_id})")
        gdb.shutdown()

        self.next_id += 1
        return Group.create(ID=self.next_id - 1, adminID=admin_id, name=name, description=description,
                            __memberTable=member_table, groupPicture=group_picture)

    def get(self, **kwargs):
        from group import Group

        sql = f'SELECT * FROM groups WHERE'
        for key in kwargs:
            if key != "sql":
                sql += f" {key}=" if list(kwargs.keys()).index(key) == 0 else f" and {key}="
                sql += f'{kwargs[key]}' if type(kwargs[key]) == int else f'"{kwargs[key]}"'
            else:
                sql += f" and {kwargs[key]}"
                break

        print(sql)
        data = self.db.query(sql)

        if data == None:
            return None

        if len(data) > 1:
            return [Group.create(ID=id, adminID=admin_id, name=name, description=description,
                                 __memberTable=member_table, groupPicture=group_picture)
                    for id, admin_id, name, description, member_table, group_picture in data]
        elif len(data) == 1:
            data = data[0]
            return Group.create(ID=data[0], adminID=data[1], name=data[2], description=data[3],
                                __memberTable=data[4], groupPicture=data[5])
        else:
            return None

    def delete(self, **kwargs):
        sql = f'DELETE FROM groups WHERE {list(kwargs.keys())[0]}='
        sql += f'{list(kwargs.values())[0]}' if type(
            list(kwargs.values())[0]) == int else f'"{list(kwargs.values())[0]}"'

        print(sql)
        self.db.query(sql)

    def update(self):
        pass


def create_samples():
    from util import add_to_group
    udb = UserDatabase()

    udb.insert("cracksii", "cracksii187", "images/image1.jpg", "offline", True)
    udb.insert("wacom", "xppen", "images/image2.jpg", "in war", False)
    udb.insert("razer", "apple", "images/image3.jpg", "developing new procuts", False)
    for _ in udb.db.query("SELECT * FROM users"):
        print(_)

    print()
    mdb = MessageDatabase()
    mdb.insert(2, 1, "Yo bro wyding?")
    mdb.insert(3, 1, "just chillin")
    mdb.insert(2, 2, "ok")
    mdb.insert(1, 1, "me 2 bro")
    mdb.insert(2, 1, "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")

    for _ in mdb.db.query("SELECT * FROM messages"):
        print(_)

    print()
    gdb = GroupDatabase()
    gdb.insert("Kebab Connection", 1, "Cry emoji x 27", "images/groupImage1.jpg")
    gdb.insert("Hey Vsauce Michael Here", 2, "What is a Déjà vu?", "images/groupImage2.jpg")

    for _ in gdb.db.query("SELECT * FROM groups"):
        print(_)

    add_to_group(1, 2)
    add_to_group(2, 1)
    add_to_group(3, 1)

    return udb, mdb, gdb


if __name__ == '__main__':
    user_db, message_db, group_db = create_samples()

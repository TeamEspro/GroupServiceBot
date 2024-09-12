import threading

from sqlalchemy import Column, String

from GroupService.modules.sql import BASE, SESSION


class GroupChats(BASE):
    __tablename__ = "Group_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


GroupChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_Group(chat_id):
    try:
        chat = SESSION.query(GroupChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()


def set_Group(chat_id):
    with INSERTION_LOCK:
        Groupchat = SESSION.query(GroupChats).get(str(chat_id))
        if not Groupchat:
            Groupchat = GroupChats(str(chat_id))
        SESSION.add(Groupchat)
        SESSION.commit()


def rem_Group(chat_id):
    with INSERTION_LOCK:
        Groupchat = SESSION.query(GroupChats).get(str(chat_id))
        if Groupchat:
            SESSION.delete(Groupchat)
        SESSION.commit()

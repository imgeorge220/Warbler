"""Seed database with sample data from CSV Files."""


import os
from models import db, User, Message, Follows, Fancy

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.drop_all()
db.create_all()


def creat_test_db():
    """Creates seed test-database"""
    
    # Add test users
    user1 = User.signup("user1-test", 'test1@test.com', "pw-test")
    user2 = User.signup("user2-test", 'test2@test.com', "pw-test")
    user3 = User.signup("user3-test", 'test3@test.com', "pw-test")

    users = [user1, user2, user3]

    db.session.add_all(users)
    db.session.commit()

    # Add messages
    user_num = 1

    for user in users:
        for num in range(user_num):
            msg = Message(text=f"TEST MESSAGE-{user.id}-{num}", user_id=user.id)
            db.session.add(msg)

        user_num += 1

    db.session.commit()

    # Add Follows
    for i in range(len(users)):
        for j in range(i):
            follow = Follows(user_being_followed_id=users[j].id,
                            user_following_id=users[i].id)
            db.session.add(follow)

    db.session.commit()


    # Add Fancies
    msgs = Message.query.order_by(Message.id).all()
    fancy1 = Fancy(message_id=msgs[0].id, user_id=users[0].id)
    fancy2 = Fancy(message_id=msgs[1].id, user_id=users[0].id)
    fancy3 = Fancy(message_id=msgs[2].id, user_id=users[0].id)

    fancies = [fancy1, fancy2, fancy3]

    db.session.add_all(fancies)
    db.session.commit()

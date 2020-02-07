"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Fancy

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app
from app import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Fancy.query.delete()

        self.u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(self.u1)
        db.session.add(self.u2)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up failed transactions"""

        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        msg = Message(text="Testing this", user_id=self.u1.id)
        db.session.add(msg)
        db.session.commit()

        # Message should exist, have its user known, have no fanciers, and should repr properly
        self.assertEqual(len(Message.query.all()), 1)
        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(self.u1, msg.user)
        self.assertEqual(len(msg.fanciers), 0)
        self.assertEqual(str(msg), f"<Message - User: {self.u1} - Testing this>")

    def test_message_fancy(self):
        """Do fancies show up?"""

        msg = Message(text="Testing this", user_id=self.u1.id)
        db.session.add(msg)
        db.session.commit()

        fancy = Fancy(message_id=msg.id, user_id=self.u2.id)
        db.session.add(fancy)
        db.session.commit()

        # Fancy should exist on message, as being fancied by u2, with the correct count of fancies
        self.assertEqual(len(Fancy.query.all()), 1)
        self.assertEqual(msg.count_fancies(), 1)
        self.assertTrue(msg.is_fancied_by(self.u2))
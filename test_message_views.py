"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Fancy

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Fancy.query.delete()

        self.client = app.test_client()

        self.test_user1 = User.signup(username="testuser",
                                     email="test@test.com",
                                     password="testuser",
                                     image_url=None)

        self.test_user2 = User.signup(username="testuser2",
                                      email="test2@test.com",
                                      password="testuser",
                                      image_url=None)

        db.session.commit()

        self.msg = Message(text="Placeholder", user_id=self.test_user1.id)
        db.session.add(self.msg)

        db.session.commit()

    def tearDown(self):
        """Clean up failed transactions"""

        db.session.rollback()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user1.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new",
                          data={"text": "Hello"}, follow_redirects=True)

            # Make sure it redirects to a successful page
            self.assertEqual(resp.status_code, 200)

            msg = Message.query.filter_by(text="Hello").one()
            self.assertEqual(msg.user_id, self.test_user1.id)
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]
    
    def test_delete_message(self):
        """Can user delete a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user1.id

            # Errors if it fails to find exactly one message.
            msg = Message.query.filter_by(text="Placeholder").one()

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)

            # Make sure it redirects to a successful page
            self.assertEqual(resp.status_code, 200)

            self.assertEqual(len(Message.query.all()), 0)
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]
    
    def test_add_other_user_message(self):
        """Can user add a message as another user?
        
        ... no, there's no way to tell the server you want to
        """
        return ":)"
        
    
    def test_delete_other_user_message(self):
        """Can user delete a message of another user?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                # Our only message (self.msg) was added by test_user1
                sess[CURR_USER_KEY] = self.test_user2.id

            # Errors if it fails to find exactly one message.
            msg = Message.query.filter_by(text="Placeholder").one()

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            # Make sure it redirects to a successful page
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertEqual(len(Message.query.all()), 1)
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]

    def test_logged_out_post(self):
        """Are we prohibited from adding messages while logged out?"""

        with self.client as c:
            resp = c.post("/messages/new",
                          data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertEqual(len(Message.query.all()), 1)

    def test_logged_out_delete(self):
        """Are we prohibited from deleting messages while logged out?"""

        with self.client as c:
            # Errors if it fails to find exactly one message.
            msg = Message.query.filter_by(text="Placeholder").one()

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertEqual(len(Message.query.all()), 1)



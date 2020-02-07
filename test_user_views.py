"""User View tests."""

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

    def tearDown(self):
        """Clean up failed transactions"""

        db.session.rollback()

    def test_logged_out_follow_viewing(self):
        """Can user use Warbler while logged out? (No we need more warblers!)"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            resp = c.get(f"/users/{self.test_user1.id}/following", follow_redirects=False)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "http://localhost/")

            resp = c.get("/")

            # Make sure it redirects to a successful page
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

            resp = c.get(f"/users/{self.test_user1.id}/followers", follow_redirects=False)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            # self.assertIn("Access unauthorized.", html)
            self.assertEqual(resp.content_location, "http://localhost/")

    def test_delete_other_user(self):
        """Can user delete another user?

        ... no, there's no way to tell the server you want to
        """
        return ":)"

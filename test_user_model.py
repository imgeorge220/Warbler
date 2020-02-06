"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows, Fancy

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Fancy.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up failed transactions"""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should exist, have no messages & no followers, and should repr properly
        self.assertEqual(len(User.query.all()), 1)
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(str(u), f"<User #{u.id}: testuser, test@test.com>")

    def test_user_follow(self):
        """Does following model work?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        follow = Follows(user_following_id=u1.id, user_being_followed_id=u2.id)
        db.session.add(follow)
        db.session.commit()

        #
        self.assertEqual(len(Follows.query.all()), 1)
        self.assertTrue(u2.is_followed_by(u1))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))
        self.assertEqual(len(u2.followers), 1)
        self.assertEqual(len(u1.followers), 0)

    def test_user_authenticate(self):
        """Does authentification work?"""

        u1 = User.signup("username", "email@test.gov", "password1")

        db.session.commit()

        #
        self.assertEqual(len(User.query.all()), 1)
        self.assertTrue(User.authenticate("username", "password1"))
        self.assertTrue(u1.check_password("password1"))
        self.assertFalse(User.authenticate("username", "password2"))
        self.assertFalse(u1.check_password("password2"))
        with self.assertRaises(Exception):
            User.signup("username", "email2@test.gov","password2")
            db.session.commit()

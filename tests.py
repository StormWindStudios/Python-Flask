from datetime import datetime, timedelta
import unittest 
from config import Config
from app import db
from app.main.models import User, Post
from app import create_app

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):

        u = User(
            first_name = 'Test',
            last_name = 'User',
            email = 'test.user@testuser.org'
        )

        u.set_password('password')

        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('password'))

    def test_avatar(self):
        u = User(
            first_name = 'Test',
            last_name = 'User',
            email = 'test.user@testuser.org'
        )

        self.assertEqual(u.avatar(128), (
            'https://www.gravatar.com/avatar/'
            '980bf7835dbbe25b0bdb9aa7f8c1a773'
            '?d=identicon&s=128'))

    def test_follow(self):
        user1 = User(
            first_name = 'Test1',
            last_name = 'User',
            email = 'test1.user@testuser.org'
        )

        user2 = User(
            first_name = 'Test2',
            last_name = 'User',
            email = 'test2.user@testuser.org'
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.assertEqual(user1.followed.all(), [])
        self.assertEqual(user2.followed.all(), [])

        user1.follow(user2)
        db.session.commit()

        self.assertTrue(user1.is_following(user2))
        self.assertEqual(user1.followed.count(), 1)
        self.assertEqual(user1.followed.first().first_name, 'Test2')

        self.assertEqual(user2.followers.count(), 1)
        self.assertEqual(user2.followers.first().first_name, 'Test1')

        user1.unfollow(user2)
        db.session.commit()

        self.assertFalse(user1.is_following(user2))
        self.assertEqual(user1.followed.count(), 0)
        self.assertEqual(user2.followers.count(), 0)

    def test_follow_posts(self):
        user1 = User(
            first_name = 'Test1',
            last_name = 'User',
            email = 'test1.user@testuser.org'
        )

        user2 = User(
            first_name = 'Test2',
            last_name = 'User',
            email = 'test2.user@testuser.org'
        )

        user3 = User(
            first_name = 'Test3',
            last_name = 'User',
            email = 'test3.user@testuser.org'
        )

        user4 = User(
            first_name = 'Test4',
            last_name = 'User',
            email = 'test4.user@testuser.org'
        )

        db.session.add_all([user1, user2, user3, user4])

        p1 = Post(
            title = 'Test Post 1',
            body = 'Test post body 1',
            author = user1,
            timestamp = datetime.now() + timedelta(seconds=1)
        )

        p2 = Post(
            title = 'Test Post 2',
            body = 'Test post body 2',
            author = user2,
            timestamp = datetime.now() + timedelta(seconds=2)
        )

        p3 = Post(
            title = 'Test Post 3',
            body = 'Test post body 3',
            author = user3,
            timestamp = datetime.now() + timedelta(seconds=3)
        )

        p4 = Post(
            title = 'Test Post 4',
            body = 'Test post body 4',
            author = user4,
            timestamp = datetime.now() + timedelta(seconds=4)
        )

        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        user1.follow(user2)
        user1.follow(user4)
        user2.follow(user3)
        user3.follow(user4)
        db.session.commit()

        f1 = user1.followed_posts().all()
        f2 = user2.followed_posts().all()
        f3 = user3.followed_posts().all()
        f4 = user4.followed_posts().all()

        self.assertEqual(f1, [p4, p2, p1])
        self.assertEqual(f2, [p3, p2])
        self.assertEqual(f3, [p4, p3])
        self.assertEqual(f4, [p4])

if __name__ == '__main__':
    unittest.main(verbosity=2)
import unittest
from budget_app.app import app, db
from budget_app.models import User

class AuthTest(unittest.TestCase):
    '''Tests for sign up and authentication routes.'''

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # in-memory DB
        self.client = app.test_client()

        with app.app_context():
            db.create_all() # Builds tables fresh for each test run.

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_signup_creates_user(self):
        response = self.client.post('/signup',
                                    data={
                                        "username" : "testuser",
                                        'password': 'testpassword'
                                    })
        
        self.assertIn(response.status_code, [200, 302])

        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertNotEqual('testpassword', User.password_hash) # TODO fix way to test password 

    def test_duplicate_username_rejected(self):
        with app.app_context():
            db.session.add(User(username='audrey', password_hash="fake"))
            db.session.commit()

        response = self.client.post('/signup',
                                    data={
                                        'username': 'audrey',
                                        'password': 'newpw'
                                    })
        
        self.assertEqual(response.status_code, 422)
        self.assertIn("Username already taken.", response.get_data(as_text=True))

    def test_empty_signup_rejected(self):
        empty_error_message = "Username or password must be filled out."
        response = self.client.post('/signup',
                                    data={
                                        'username': '',
                                        'password': ''
                                    })
        self.assertEqual(response.status_code, 422)
        self.assertIn(empty_error_message, response.get_data(as_text=True))

        response = self.client.post('/signup',
                                    data={
                                        'username': 'foo',
                                        'password': ''
                                    })
        self.assertEqual(response.status_code, 422)
        self.assertIn(empty_error_message, response.get_data(as_text=True))

        response = self.client.post('/signup',
                                    data={
                                        'username': '',
                                        'password': 'bar'
                                    })
        self.assertEqual(response.status_code, 422)
        self.assertIn(empty_error_message, response.get_data(as_text=True))

    def test_succesful_login(self):
        self.client.post('/signup',
                                    data={
                                        "username" : "testuser",
                                        'password': 'testpassword'
                                    }) # create user & pw

        response = self.client.post('/login',
                                    data={
                                        "username" : "testuser",
                                        'password': 'testpassword'
                                    },
                                    follow_redirects=True)
        
        self.assertIn(response.status_code, [200, 302])
        self.assertIn("Login successful!", response.get_data(as_text=True))
        self.assertIn("Budget Home", response.get_data(as_text=True))
        # # self.assertIn('Log Out', response.get_data(as_text=True)) # TODO add functionality, then test

    def test_unsuccesful_login(self):
        invalid_login_message = 'Invalid username or password.'
        self.client.post('/signup',
                                    data={
                                        "username" : "testuser",
                                        'password': 'testpassword'
                                    }) # create user & pw

        response = self.client.post('/login',
                                    data={
                                        "username" : "testuser",
                                        'password': ''
                                    },
                                    follow_redirects=True) # empty pw
        
        self.assertEqual(response.status_code, 422)
        self.assertIn(invalid_login_message, response.get_data(as_text=True))

        response = self.client.post('/login',
                                    data={
                                        "username" : "",
                                        'password': 'testpassword'
                                    },
                                    follow_redirects=True) # empty username
        
        self.assertEqual(response.status_code, 422)
        self.assertIn(invalid_login_message, response.get_data(as_text=True))
         
        response = self.client.post('/login',
                                    data={
                                        "username" : "testuser",
                                        'password': 'testpw'
                                    },
                                    follow_redirects=True) # incorrect pw
        
        self.assertEqual(response.status_code, 422)
        self.assertIn(invalid_login_message, response.get_data(as_text=True))



if __name__ == '__main__':
    unittest.main()
import unittest
from budget_app import create_app, db
from budget_app.models import User

class AuthTest(unittest.TestCase):
    '''Tests for sign up and authentication routes.'''

    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            # remove session and drop tables to fully clean state
            db.session.remove()
            db.drop_all()

    def test_signup_creates_user(self):
        response = self.client.post('/signup',
                                    data={
                                        "username" : "testuser",
                                        'password': 'testpassword'
                                    }, follow_redirects=True)
        
        self.assertIn(response.status_code, [200, 302])

        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertNotEqual('testpassword', user.password_hash) # TODO fix way to test password 

    def test_duplicate_username_rejected(self):
        with self.app.app_context():
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
        
        # inspect session after login: it should have user_id
        with self.client.session_transaction() as sess:
            self.assertIn('user_id', sess)
            user_id = sess['user_id']['id']
            self.assertIsInstance(user_id, int)
        
        self.assertIn(response.status_code, [200, 302])
        self.assertIn("Logged in as testuser!", response.get_data(as_text=True))
        self.assertIn("Create a Budget", response.get_data(as_text=True))
        self.assertIn('Log Out', response.get_data(as_text=True))
        self.assertNotIn('Sign Up', response.get_data(as_text=True))
        
        response = self.client.get('/') # refresh shouldn't have login
        self.assertNotIn('Log In', response.get_data(as_text=True))


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
        self.assertIn('Log In', response.get_data(as_text=True))

    def test_succesful_logout(self):
        self.client.post('/signup',
                        data={
                            "username" : "testuser",
                            'password': 'testpassword'
                        }, follow_redirects=True) # create user
        
        self.client.post('/login',
                        data={
                            "username" : "testuser",
                            'password': 'testpassword'
                        }, follow_redirects=True) # log in to set session['user_id']
        
        logout_response = self.client.get('/logout', follow_redirects=True)
        self.assertIn('Logged out successfully.', logout_response.get_data(as_text=True))
        self.assertIn('Log In', logout_response.get_data(as_text=True))
        with self.client.session_transaction() as sess:
            self.assertIsNone(sess.get('user_id'))

if __name__ == '__main__':
    unittest.main()
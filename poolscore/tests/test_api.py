import os
import unittest
import tempfile

import poolscore

class APITestCase(unittest.TestCase):

    def setUp(self):
        # self.db_fd, poolscore.app.config['DATABASE'] = tempfile.mkstemp()
        # poolscore.app.config['TESTING'] = True
        poolscore.app.config['CSRF_ENABLED'] = False
        poolscore.app.config['WTF_CSRF_ENABLED'] = False
        self.app = poolscore.app.test_client()
        # with poolscore.app.app_context():
        #     poolscore.db.create_all()


    # def tearDown(self):
    #     os.close(self.db_fd)
    #     os.unlink(poolscore.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/auth/login/', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/auth/logout/', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('nick', 'password')
        assert "Welcome nick" in rv.data
        rv = self.logout()
        assert "You were logged out" in rv.data


if __name__ == '__main__':
    unittest.main()

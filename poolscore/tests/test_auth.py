import unittest

from poolscore.tests import BaseTestCase

class AuthTestCase(BaseTestCase):

    def test_login_logout(self):
        rv = self.login('nick', 'password')
        assert "Welcome nick" in rv.data
        rv = self.logout()
        assert "You were logged out" in rv.data

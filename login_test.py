import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import app
import base64
from model import db, AccessRequest, Center, Animals, Species
login='test_Case12'
password='mycoolpassword'
class TestLogin(unittest.TestCase):
'''Init App'''
    def setUp(self):
        self.app = app.test_client()
        self.db = SQLAlchemy(app)

    '''Test Login with Basic Auth format'''    
    def open_with_auth(self, url, method, username, password):
        return self.app.open(url,
            method=method,
            headers={
            'Authorization': 'Basic ' + base64.b64encode(bytes(username + ":"
            + password, 'ascii')).decode('ascii')
            }
        )
    '''Checking test conditions'''
    def test_login(self):
        response = self.open_with_auth('/login', 'GET', login,
                                    password)
        print(response.json)
        self.assertEqual(200, response.status_code)
        
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import app
from model import db, AccessRequest, Center, Animals, Species

login='test_Case12'

class RegisterTest(unittest.TestCase):
    '''Init App'''
    def setUp(self):
        self.app = app.test_client()
        self.db = SQLAlchemy(app)

    def test_successful_signup(self):
        '''initial test payload'''
        payload = json.dumps({
            "login":login,
            "password": "mycoolpassword",
            "address": "test@gmail.com"
        })

        '''Testing conditions'''
        response = self.app.post('/register', headers={"Content-Type": "application/json"}, data=payload)

        '''Testing results'''
        print(response.json)
        self.assertEqual(int, type(response.json['c_id']))
        self.assertEqual(200, response.status_code)




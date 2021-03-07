from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, ForeignKey, String, Column
from configparser import ConfigParser 
import uuid
import jwt
import datetime
import logging
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from functools import wraps
app = Flask(__name__)
app.testing=True
config = ConfigParser() 
config_file = 'config.ini' 
config.read(config_file) 


DATABASE_CONNECTION_URI=config['DB']['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
app.config['SECRET_KEY']=config['DB']['SECRET_KEY']
SQLALCHEMY_TRACK_MODIFICATIONS = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)


        
class AccessRequest(db.Model):
    ar_id=db.Column(db.Integer, primary_key=True)
    c_id = db.Column(db.Integer, nullable=False)
    timestamp = Column(db.DateTime(timezone=True), server_default=func.now())


class Center(db.Model):
    c_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    @validates('login') 
    def validate_username(self, key, login):
        if not login:
            raise AssertionError('No login provided')
        if Center.query.filter(Center.login == login).first():
            raise AssertionError('login is already in use')
        if len(login) < 5 or len(login) > 20:
            raise AssertionError('login must be between 5 and 20 characters') 
        return login
    
class Animals(db.Model):
    a_id = db.Column(db.Integer, primary_key=True, index=True)
    centerid = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    #species = db.Column(db.String(50), nullable=False, ForeignKey("species.name"))
    age = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=True)
    species = db.Column(db.String(50), nullable=True)
    
    @validates('price') 
    def validate_price(self, key, price):
        if type(price) is not float:
            raise AssertionError('Bad price format')
        return price 


class Species(db.Model):
    s_id = db.Column(db.Integer, primary_key=True, index=True)
    description = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=True)
    name = db.Column(db.String(50), nullable=False)
    @validates('price') 
    def validate_price(self, key, price):
        if type(price) is not float:
            raise AssertionError('Bad price format')
        return price 
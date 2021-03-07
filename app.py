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
from model import AccessRequest, Center, Animals, Species
from urllib.parse import urlparse
'''Reading configuration file.'''

config = ConfigParser() 
config_file = 'config.ini' 
config.read(config_file) 
'''Setting up logging.'''
logging.basicConfig(filename=config['LOG']['logfile'],
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


'''App initialization'''
app = Flask(__name__)
app.testing=True

DATABASE_CONNECTION_URI=config['DB']['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
app.config['SECRET_KEY']=config['DB']['SECRET_KEY']
SQLALCHEMY_TRACK_MODIFICATIONS = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
'''Token based authentication'''
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms="HS256")
            current_user = Center.query.filter_by(c_id=data['c_id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator

'''Adding new users'''

@app.route('/register', methods=['POST'])
def create_user():
    data=request.get_json()
    c=Center(
        login=data['login'],
        password=data['password'],
        address=data['address']
    )
    try:
        db.session.add(c)
        db.session.commit()
        app.logger.info("New user registered" + "Center ID -"+str(c.c_id) +" "+ str(c.login ))
        return{
            'c_id':c.c_id,'login':c.login, 'password':c.password,'address':c.address
        },200
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400


'''User login - gets login and password - outputs JWT'''

@app.route('/login', methods=['GET', 'POST'])   
def login_user(): 
 
  auth = request.authorization   

  if not auth or not auth.username or not auth.password:  
     return jsonify(msg='could not verify, login required'),400    

  center = Center.query.filter_by(login=auth.username).first()



  if (str(center.password) == str(auth.password)):  
    token =  jwt.encode(
        {"c_id":center.c_id},
        app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )  
    print(token.encode('UTF-8'))

    ar=AccessRequest(
        c_id=center.c_id,
        timestamp=datetime.datetime.now()
        )
    db.session.commit()
    db.session.add(ar) 
    print(ar.c_id, ar.timestamp)  
    print(center.c_id) 
    app.logger.info(" Logged in "+str(center.c_id))
    return jsonify({'token' : token})

  
  return ('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})

'''Adding new animals'''

@app.route('/animals', methods=['POST'])
@token_required
def create_animal(current_user):
    
    data=request.get_json()
    a=Animals(
        centerid=current_user.c_id,
        name=data['name'],
        age=data['age'],
        price=data['price'],
        species=data['species']

    )
    try:
        db.session.add(a)
        db.session.commit()
        app.logger.info("Animal added "+str(a.centerid)+" "+str(a.name))
        return{
            'a_id':a.a_id,'centerid':a.centerid, 
            'name':a.name,'age':a.age,'price':a.price,
            'species':a.species
        },200
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400


'''Adding new species'''

@app.route('/species', methods=['POST'])
@token_required
def create_specie(current_user):
    data=request.get_json()
    u=Species(
        description=data['description'],
        name=data['name'],
        price=data['price']

    )
    try:
        db.session.add(u)
        db.session.commit()
        app.logger.info(" Species added " +str(u.s_id)+" "+ str(u.name))
        return{
            's_id':u.s_id,'description':u.description,
            'name':u.name,'price':u.price
        },200
    except AssertionError as exception_message: 
        return jsonify(msg='Error: {}. '.format(exception_message)), 400


'''Get methods - displaying all users/animals/species 
- plus displaying one by ID'''
@app.route('/center', methods=['GET'])
def read_users():
    return jsonify([{
        'c_id':u.c_id,'login':u.login, 'password':u.password,'address':u.address
    }for u in Center.query.all()
    ])

@app.route('/center/<id>/')
def get_user(id):
	print(id)
	u = Center.query.filter_by(c_id=id).first_or_404()
	return {
		'c_id':u.c_id,'login':u.login, 'password':u.password,'address':u.address
		}


@app.route('/animals', methods=['GET'])
def read_animals():
    return jsonify([{
        'a_id':a.a_id,'centerid':a.centerid, 
        'name':a.name,'age':a.age,'price':a.price,
        'species':a.species
    }for a in Animals.query.all()
    ])

@app.route('/animals/<id>/', methods=['GET'])
def get_animal(id):
	print(id)
	a = Animals.query.filter_by(a_id=id).first_or_404()
	return {
		'a_id':a.a_id,'centerid':a.centerid, 
        'name':a.name,'age':a.age,'price':a.price,
        'species':a.species
		}


@app.route('/species', methods=['GET'])
def read_species():
    return jsonify([{
        's_id':s.s_id,'description':s.description,
         'name':s.name,'price':s.price
    }for s in Species.query.all()
    ])

@app.route('/species/<id>/', methods = ['GET'])
def get_specie(id):
	print(id)
	s = Species.query.filter_by(s_id=id).first_or_404()
	return {
		's_id':s.s_id,'description':s.description,
         'name':s.name,'price':s.price
		}

        
'''Editing existing animal'''

@app.route('/animals/<animal_id>/', methods=['PUT'])
@token_required
def update_animal(current_user,animal_id):
    data = request.get_json()
    if 'name' not in data:
        return {
        'error': 'Bad Request',
        'message': 'Name field needs to be present'
        }, 400
    else:
        a = Animals.query.filter_by(a_id=animal_id).first_or_404()
        db.session.add(a)
        db.session.commit()
        app.logger.info("animal updated"+str(a.a_id)+" "+str(a.name))

        return jsonify({
        'a_id':a.a_id,'centerid':current_user, 
        'name':a.name,'age':a.age,'price':a.price,
        'species':a.species
        }),200

'''Animal delete method'''
@app.route('/animals/<animal_id>/', methods=['DELETE'] )
@token_required
def delete_animal(current_user,animal_id):
    animal = Animals.query.filter_by(a_id=animal_id).first_or_404()
    if (current_user.c_id == animal.c_id):
        db.session.delete(animal)
        db.session.commit()
        return {
            'success': 'Data deleted successfully'
        }
    else:
        return {
            'Failure': 'You cannot delete that'
        }



if __name__ == '__main__':
    app.run(debug=True)


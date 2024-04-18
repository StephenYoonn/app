#!/usr/bin/python3

from . import app
from flask import request, jsonify
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
import string

import zlib
import hashlib
import base64
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

instance_dir = os.path.join(basedir, 'instance')

if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)

#uri databse will use
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'mydatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Mappings(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    original_url = db.Column(db.String(200), nullable=False, unique = True)
    short_Url = db.Column(db.String(80), unique = True, nullable=False)


    def __repr__(self):
        return f'<Mappings original_url={self.original_url} short_url={self.short_Url}>'
    

with app.app_context():
    db.create_all()


@app.route('/encode', methods=['POST'])
def encode():

    #json get input
    data = request.get_json()
    if 'url' in data:
        url = data['url'] 
    else:
        return jsonify({"error": "URL not provided"}), 400

    existing_mapping = Mappings.query.filter_by(original_url=url).first()
    if existing_mapping:
        #print(existing_mapping.original_url)
        #print(existing_mapping.short_Url)
        # URL already exists, return the existing short URL
        return jsonify({"oldLink": url, "encodedLink": existing_mapping.short_Url})
    
    next_id = Mappings.query.count() + 1
    short = shorten(next_id)
    if len(short) > 6:
        short = short[:6]
    short_url = f"https://short.est/{short}"
    url_entry = Mappings(original_url=url, short_Url=short_url)

    try:
        db.session.add(url_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Roll back in case of an exception
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"oldLink": url, "encodedLink": short_url})

def shorten(num, b=62):
    characters = string.digits + string.ascii_letters
    base = len(characters)
    if num == 0:
        return characters[0]
    result = []
    while num > 0:
        num, remainder = divmod(num, base)
        result.append(characters[remainder])
    return ''.join(reversed(result))


def shortUrl(url):
    newUrl = hash(url) % 1000
    return f"https://short.est/{newUrl}"

@app.route('/decode', methods=['POST'])
def decode():
    data = request.get_json()
    if 'url' in data:
        url = data['url'] 
    else:
        return jsonify({"error": "URL not provided"}), 400
    
    newUrl = Mappings.query.filter_by(short_Url=url).first()
    return jsonify({"oldLink": newUrl.original_url})
    
        
    

    

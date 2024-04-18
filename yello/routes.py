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
        print(existing_mapping.original_url)
        print(existing_mapping.short_Url)
        # URL already exists, return the existing short URL
        return jsonify({"oldLink": url, "encodedLink": existing_mapping.short_Url})
    
    short = shorten(Mappings.query.count() + 1)
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
    if b <= 0 or b > 62:
        return "defaultShort"  # Default short URL if something goes wrong
    base = string.digits + string.ascii_letters
    r = num % b
    res = base[r]
    q = num // b
    while q:
        r = q % b
        q = q // b
        res = base[r] + res
    return res



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
    
        
    

    

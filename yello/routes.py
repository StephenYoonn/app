#!/usr/bin/python3

from . import app
from flask import request, jsonify
from cryptography.fernet import Fernet
import zlib
import base64


url_mapping = {}
key = Fernet.generate_key()
f = Fernet(key)

@app.route('/encode', methods=['POST'])
def encode():

    #json get input
    data = request.get_json()
    if 'url' in data:
        url = data['url'] 
    else:
        return jsonify({"error": "URL not provided"}), 400

    compressed = zlib.compress(url.encode('utf-8'))
    encrypted =f.encrypt(compressed)
    newUrl = base64.urlsafe_b64encode(encrypted).decode('utf-8')

    return jsonify({"oldLink": url, "encodedLink": f"https://short.est/{newUrl}"})

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
    
    newUrl = f.decrypt(url)
    return jsonify({"oldLink": newUrl})
    
        
    

    

#!/usr/bin/python3

from . import app
from flask import request, jsonify


@app.route('/encode', methods=['POST'])
def encode(url):
    print(url)

    
    newUrl = shortUrl(url)
    
    
    return jsonify({"oldLink" : url, "encodedLink" : newUrl})

def shortUrl(url):
    newUrl = hash(url) % 1000
    return f"short.est/{newUrl}"

@app.route('/decode', methods=['POST'])
def decode():
    # Your existing decode logic here
    return jsonify(result="original_url_here")
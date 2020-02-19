from flask import Flask, jsonify, request
# from flask_cors import CORS
# import numpy as np
# import pandas as pd

# import requests
# from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!'

if __name__ == '__main__':
  app.run(debug=True)
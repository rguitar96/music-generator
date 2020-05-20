from os import environ
import os
from flask import Flask
import stat
os.chmod('foxsamply', stat.S_IEXEC)

app = Flask(__name__)
app.run(host= '0.0.0.0', port=environ.get('PORT'))
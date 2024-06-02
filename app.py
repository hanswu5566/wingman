from os import urandom
from flask import Flask
from db import init_db
from oauth import init_oauth
from routes import register_routes
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = urandom(24)

load_dotenv()

db = init_db(app)
oauth = init_oauth(app)
register_routes(app,oauth,db)

if __name__ == '__main__':
    # Ensure the following block is within the application context
    app.run(debug=True,port=8000)
from routes import register_routes
from extensions import celery_instance
from flask import Flask
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True,port=8000)

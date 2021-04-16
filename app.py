from flask import Flask
from flask_cors import CORS
from flask_jwt_extended.jwt_manager import JWTManager
from flask_restful import Api

from flask_pymongo import pymongo
from flask_mongoengine import MongoEngine
from api.routers import create_route
config = {
    'JSON_SORT_KEYS': False,
    'MONGODB_SETTINGS': {
        'host': 'mongodb+srv://borrowDB:borrow2543@clusterborrow.okvbh.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
    },
    'JWT_SECRET_KEY': '&F)J@NcRfUjXn2r5u7x!A%D*G-KaPdSg',
    'JWT_ACCESS_TOKEN_EXPIRES': 300,
    'JWT_REFRESH_TOKEN_EXPIRES': 604800
}

app = Flask(__name__)

app.config.update(config)

api = Api(app)
db = MongoEngine(app=app)
create_route(api=api)
jwt = JWTManager(app=app)

CORS(app, resources={r"/*": {"origin": "*"}})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

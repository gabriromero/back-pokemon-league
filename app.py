from datetime import timedelta
import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_migrate import Migrate
from flask_cors import CORS

from dotenv import load_dotenv

from flask_jwt_extended import JWTManager

from db import db

from resources.player import blp as PlayerBlueprint
from resources.match import blp as MatchBlueprint


app = Flask(__name__)
load_dotenv()
CORS(app)

app.config['API_SPEC_OPTIONS'] = {
    'security':[{"bearerAuth": []}],
    'components':{
        "securitySchemes":
            {
                "bearerAuth": {
                    "type":"http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
    }
}


app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "pokemon-league API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL","sqlite:///data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=120)
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
jwt =  JWTManager(app)

api.register_blueprint(PlayerBlueprint)
api.register_blueprint(MatchBlueprint)
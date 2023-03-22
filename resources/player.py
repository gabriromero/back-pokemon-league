from flask_jwt_extended import jwt_required, get_jwt
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from db import db
from models import PlayerModel
from schemas import PlayerSchema

blp = Blueprint("Players", __name__, description="Player operations")

@blp.route("/private/players")
class PrivatePlayers(MethodView):
    @blp.response(200, PlayerSchema(many=True))
    def get(self):
        return PlayerModel.query.all()

@blp.route("/player")
class PlayerInfo(MethodView):
    @blp.response(200, PlayerSchema())
    @jwt_required()
    def get(self):
        player = PlayerModel.query.get_or_404(get_jwt_identity())
        return player

@blp.route("/fake/players")
class PlayerInfo(MethodView):
    @blp.response(200)
    def get(self):
        return [
            {
                'username' : 'John',
                'wins'     : 7,
            },
            {
                'username' : 'Erdeiby',
                'wins'     : 9,
            },
            {
                'username' : 'Avdalian',
                'wins'     : 3,
            }
        ]

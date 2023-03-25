import os

from flask import request
from flask_jwt_extended import jwt_required, get_jwt, create_access_token, get_jwt_identity
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError

from db import db
from models import PlayerModel

from schemas import CreatePlayerSchema
from schemas import ClassificationSchema

blp = Blueprint("Players", __name__, description="Player operations")

@blp.route("/private/create-player")
class Register(MethodView):
    @blp.arguments(CreatePlayerSchema)
    def post(self, player_data):
        player = PlayerModel(
            username = player_data["username"],
            password = player_data["password"],
        )

        try:
            db.session.add(player)
            db.session.commit()
        except IntegrityError:
            abort(400,message="Player with same username exist")
        
        return {"msg" : f"Player with username {player.username} created"}, 201

@blp.route("/classification")
class Classification(MethodView):
    @blp.response(200, ClassificationSchema(many=True))
    def get(self):
        return PlayerModel.query.all()

@blp.route("/fake/classification")
class FakePlayerInfo(MethodView):
    @blp.response(200)
    def get(self):
        return [
            {
                'username' : 'John',
                'matches_won'     : 7,
            },
            {
                'username' : 'Erdeiby',
                'matches_won'     : 9,
            },
            {
                'username' : 'Avdalian',
                'matches_won'     : 3,
            },
            {
                'username' : 'Guzzom',
                'matches_won'     : 4,
            },
            {
                'username' : 'Kmilon',
                'matches_won'     : 4,
            },
            {
                'username' : 'Suli',
                'matches_won'     : 10,
            }
        ]

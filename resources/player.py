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
from schemas import DeletePlayerSchema
from schemas import ClassificationSchema
from schemas import ProfileSchema
from schemas import LoginPlayerSchema
from schemas import ProfileUpdateSchema
from schemas import PrivatePlayersSchema

blp = Blueprint("Players", __name__, description="Player operations")

@blp.route("/classification")
class Classification(MethodView):
    @blp.response(200, ClassificationSchema(many=True))
    def get(self):
        return PlayerModel.query.all()
    
@blp.route("/login")
class Login(MethodView):
    @blp.arguments(LoginPlayerSchema)
    def post(self, user_data):
        player = PlayerModel.query.filter(
            PlayerModel.username == user_data["username"]
        ).first()

        if player and player.password == user_data["password"]:
            access_token = create_access_token(identity=player.id)
            return {"access_token" : access_token}
        
        abort(401, message="Invalid credentials")

@blp.route("/myself/profile")
class Profile(MethodView):
    @blp.response(200, ProfileSchema)
    @jwt_required()
    def get(self):
        player = PlayerModel.query.get_or_404(get_jwt_identity())
        return player

    @blp.arguments(ProfileUpdateSchema)
    @blp.response(200, ProfileSchema)
    @jwt_required()
    def put(self, profile_data):
        player = PlayerModel.query.get_or_404(get_jwt_identity())

        if("profile_pic" in profile_data):
            player.profile_pic = profile_data["profile_pic"]
        
        db.session.add(player)
        db.session.commit()

        return player,200
    
@blp.route("/private/player")
class Register(MethodView):
    @blp.response(200,PrivatePlayersSchema(many=True))
    def get(self):
        return PlayerModel.query.all()
    
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
    
    @blp.arguments(DeletePlayerSchema)
    def delete(self, player_data):
        player = PlayerModel.query.get_or_404(player_data["id"])

        db.session.delete(player)
        db.session.commit()
        return {"message": f"Player {player.username} deleted."}
    
@blp.route("/private/freeze-wins")
class Register(MethodView):
    @blp.response(200)
    def put(self):
        players = PlayerModel.query.all()

        for player in players:
            player.matches_won_frozen = player.matches_won
            db.session.commit()

        return ({'message': 'Matches frozen successfully.'}), 200
    
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
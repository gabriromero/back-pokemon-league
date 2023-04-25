from operator import and_, or_

from sqlalchemy import distinct

from .decorators.decorators import secret_header_required

from flask import request
from flask_jwt_extended import jwt_required, get_jwt, create_access_token, get_jwt_identity
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError

from db import db
from models import PlayerModel, MatchModel

from schemas import CreatePlayerSchema
from schemas import DeletePlayerSchema
from schemas import ClassificationSchema
from schemas import ProfileSchema
from schemas import LoginPlayerSchema
from schemas import ProfileUpdateSchema
from schemas import PrivatePlayersSchema
from schemas import MatchDiferenciaSchema
from schemas import MarkResultSchema
from schemas import AvailableSkinsSchema

blp = Blueprint("Players", __name__, description="Player operations")

@blp.route("/myself/matches")
class MyMatches(MethodView):    
    @blp.response(200, MatchDiferenciaSchema(many=True))
    @jwt_required()
    def get(self):
        myself = PlayerModel.query.get_or_404(get_jwt_identity()) 
        jornada = int(request.args.get('jornada')) 
        matches = MatchModel.query.filter((MatchModel.player_1_id == myself.id) | (MatchModel.player_2_id == myself.id) , (MatchModel.jornada == jornada)).all()   
        for match in matches:
            if myself.id == match.player_1_id:                
                enemyId = match.player_2_id
                enemy = PlayerModel.query.get_or_404(enemyId)
                match.player_1_username = myself.username
                match.player_2_username = enemy.username
                match.player_1_profile_pic = myself.profile_pic
                match.player_2_profile_pic = enemy.profile_pic
            else:
                enemyId = match.player_1_id
                enemy = PlayerModel.query.get_or_404(enemyId)                
                match.player_1_username = enemy.username
                match.player_2_username = myself.username
                match.player_1_profile_pic = enemy.profile_pic
                match.player_2_profile_pic = myself.profile_pic
            
            match.diferencia = myself.matches_won_frozen - enemy.matches_won_frozen            
            if match.result != 0:
                match.result_username = myself.username if myself.id == match.result else enemy.username
            else:
                match.result_username = ""

        return matches
    
@blp.route("/myself/mark-result")
class MarkResult(MethodView):
    @blp.arguments(MarkResultSchema)
    @blp.response(200)
    @jwt_required()
    def post(self, match_data):
        
        jornada = match_data["jornada"]
        
        player_1_username = match_data["player_1_username"]
        player_2_username = match_data["player_2_username"]
        
        player_1 = PlayerModel.query.filter_by(username=player_1_username).first()
        player_2 = PlayerModel.query.filter_by(username=player_2_username).first()


        player_winner_username = match_data["player_winner_username"]
        player_winner = PlayerModel.query.filter_by(username=player_winner_username).first()

        player_loser_username = player_2_username if player_1_username == player_winner_username else player_1_username
        player_loser = PlayerModel.query.filter_by(username=player_loser_username).first()

        myself = PlayerModel.query.get_or_404(get_jwt_identity())
        myself_username = myself.username

        if player_1_username != myself_username and player_2_username != myself_username:
            abort(404,message="Match does not refer to actual player")


        match = MatchModel.query.filter_by(jornada=jornada).filter(
            or_(
                and_(MatchModel.player_1_id == player_1.id, MatchModel.player_2_id == player_2.id),
                and_(MatchModel.player_1_id == player_2.id, MatchModel.player_2_id == player_1.id)
            )
        ).first()

        if not match:
            abort(404,message="Match not found")

        if match.player_1_id == myself.id:
            match.player_1_finished = True
        else:
            match.player_2_finished = True

        match_acabado = match.player_1_finished == True and match.player_2_finished == True

        if(not match_acabado):
            match.result = player_winner.id

            db.session.commit()

            return f"Marked winner: {player_winner_username}",200
        else:
            coincide = match.result == player_winner.id

            if not coincide:
                match.player_1_finished = False
                match.player_2_finished = False
                match.result = 0

                db.session.commit()

                return f"Results do not coincide, restarting marks",200
            else:
                player_winner.matches_played += 1
                player_loser.matches_played += 1
                player_winner.matches_won += 1

                db.session.commit()

                return f"Marked {player_winner.username} as winner against {player_loser.username}",200
            
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
            or_(PlayerModel.username.ilike(user_data["username"]), PlayerModel.username.ilike(user_data["username"].lower()))
        ).first()

        if player and player.password == user_data["password"]:
            access_token = create_access_token(identity=player.id)
            return {"access_token" : access_token}
        
        abort(401, message="Invalid credentials")

@blp.route("/available-skins")
class AvailableSkins(MethodView):
    @blp.arguments(AvailableSkinsSchema)
    @blp.response(200)
    def get(self, skins_data):
        num_skins = skins_data["num_skins"]
        all_skins = [pic[0] for pic in db.session.query(distinct(PlayerModel.profile_pic)).all()]
        numbers_available = available_skins(all_skins, num_skins)
        return numbers_available
    
def available_skins(used_skins, num_skins):
    used_numbers = [int(skin.split("-")[1]) for skin in used_skins if skin.startswith("trainer-")]
    return [i for i in range(1, num_skins+1) if i not in used_numbers]

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
        skin_selected = profile_data["profile_pic"]

        all_skins = [pic[0] for pic in db.session.query(distinct(PlayerModel.profile_pic)).all()]

        if(skin_selected in all_skins):
            abort(400,message="Ya existe un jugador con esa skin")

        if("profile_pic" in profile_data):
            player.profile_pic = skin_selected
        
        db.session.add(player)
        db.session.commit()

        return player,200
    
@blp.route("/private/player")
class Register(MethodView):
    @blp.response(200,PrivatePlayersSchema(many=True))
    @secret_header_required
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
    @secret_header_required
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
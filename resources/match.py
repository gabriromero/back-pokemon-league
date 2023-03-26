
from itertools import combinations
import random
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from flask_jwt_extended import jwt_required, get_jwt_identity

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models import MatchModel, PlayerModel

from schemas import MatchSchema
from schemas import GenerateMatchesSchema
from schemas import HardcodeMatchSchema

from random import choice

blp = Blueprint("Matches", __name__, description="Match operations")

@blp.route("/matches")
class Matches(MethodView):
    @blp.response(200, MatchSchema(many=True))
    def get(self):
        return MatchModel.query.all()

@blp.route("/private/generate-matches")
class GenerateMatches(MethodView):
    @blp.arguments(GenerateMatchesSchema)
    @blp.response(200)
    def post(self, match_data):
        jornada = match_data["jornada"]

        for i in range(10):
            player1 = PlayerModel.query.get_or_404(get_player_matches()[0][0])
            player2 = PlayerModel.query.get_or_404(get_player_matches()[0][1])
            createSingleMatch(player1,player2, jornada)

        return "created"
        

        

@blp.route("/private/hardcode-match")
class HardcodeMatch(MethodView):
    @blp.arguments(HardcodeMatchSchema)
    def post(self, match_data):

        player1 = PlayerModel.query.get_or_404(match_data["player_1_id"])
        player2 = PlayerModel.query.get_or_404(match_data["player_2_id"])
        jornada = match_data["jornada"]

        return createSingleMatch(player1, player2, jornada)

@blp.route("/private/clean-matches")
class CleanMatches(MethodView):
    @blp.arguments(GenerateMatchesSchema)
    def delete(self, match_data):
        
        jornada = match_data["jornada"]
    
        if (jornada == 0):
            partidos = MatchModel.query.all()
        else: 
            partidos = MatchModel.query.filter(MatchModel.jornada == jornada).all()

        for partido in partidos:
            db.session.delete(partido)
        db.session.commit()

        return {"msg" : f"Partidos borrados, {len(partidos)}"}, 200

def createSingleMatch(player1, player2, jornada):

    if(player1.id == player2.id):
        abort(403, message="Mismo player")

    match_exists = ((MatchModel.query.filter(MatchModel.player_1_id == player1.id, MatchModel.player_2_id == player2.id).first() or
                            MatchModel.query.filter(MatchModel.player_1_id == player2.id, MatchModel.player_2_id == player1.id).first()) and
                            MatchModel.query.filter(MatchModel.jornada == jornada).first())
            
    if(match_exists):
        abort(403, message=f"{match_exists.player_1_id} , {match_exists.player_2_id}, Ya existe este match")

    match = MatchModel(player_1_id = player1.id,
                        player_2_id = player2.id,
                        jornada = jornada)

    try:
        db.session.add(match)
        db.session.commit()
    except IntegrityError:
        abort(
            400,
            message="Integrity error creating a match",
        )
    except SQLAlchemyError as e:
        abort(500, message="An error occurred creating a match.")

    return {"msg" : f"Partido entre {player1.username} y {player2.username} creado"}, 201

def get_player_matches():
    matches = MatchModel.query.all()

    player_combinations = {}

    for match in matches:
        player1_id = match.player_1_id
        player2_id = match.player_2_id

        players = sorted([player1_id, player2_id])

        jornada = match.jornada

        if tuple(players) not in player_combinations:
            player_combinations[tuple(players)] = [jornada]
        else:
            player_combinations[tuple(players)].append(jornada)

    combinations_list = []
    for players in combinations(PlayerModel.query.all(), 2):
        player1_id = players[0].id
        player2_id = players[1].id
        players = sorted([player1_id, player2_id])

        if tuple(players) in player_combinations:
            count = len(player_combinations[tuple(players)])
            combinations_list.append((players[0], players[1], count))
        else:
            combinations_list.append((players[0], players[1], 0))

    random.shuffle(combinations_list)
    return sorted(combinations_list, key=lambda x: x[2])
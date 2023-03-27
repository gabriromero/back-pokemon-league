
from itertools import combinations
from math import factorial
import random
import time
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
        nCombates = match_data["nCombates"]
        nPlayers = PlayerModel.query.count()
        lambdaNum = max_edges(nPlayers,nCombates)

        start_time = time.time()

        nCombatesDone = 0
        while nCombatesDone < lambdaNum:
            start_time = time.time()
            while nCombatesDone < lambdaNum and time.time() - start_time < 2:
                next_match = get_player_matches()[0]
                player1 = PlayerModel.query.get_or_404(next_match[0])
                player2 = PlayerModel.query.get_or_404(next_match[1])
                if(createSingleMatch(player1, player2, jornada, nCombates)):
                    nCombatesDone += 1

            if nCombatesDone != lambdaNum:
                nCombatesDone = 0 
                time.sleep(max(0, 2 - (time.time() - start_time)))
                delete_matches_of_jornada(jornada)
            else:
                return "Matcheo óptimo!"
        
        return "Matcheo no óptimo, borrar combates y reiniciar"

@blp.route("/private/hardcode-match")
class HardcodeMatch(MethodView):
    @blp.arguments(HardcodeMatchSchema)
    def post(self, match_data):

        player1 = PlayerModel.query.get_or_404(match_data["player_1_id"])
        player2 = PlayerModel.query.get_or_404(match_data["player_2_id"])
        jornada = match_data["jornada"]

        return {"data" :createSingleMatch(player1, player2, jornada, 1)}

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

def createSingleMatch(player1, player2, jornada, limit):

    if(get_matches_for_jornada(player1.id,jornada) >= limit or
       get_matches_for_jornada(player2.id,jornada) >= limit):
        return False

    if(player1.id == player2.id):
        return False

    match_exists = MatchModel.query.filter(
        db.and_(
            db.or_(
                MatchModel.player_1_id == player1.id,
                MatchModel.player_1_id == player2.id
            ),
            db.or_(
                MatchModel.player_2_id == player1.id,
                MatchModel.player_2_id == player2.id
            ),
            MatchModel.jornada == jornada
        )
    ).first()
            
    if(match_exists):
        return False
    
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

    return True

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

def get_matches_for_jornada(player_id, jornada):
    return MatchModel.query.join(
        PlayerModel,
        db.or_(
            MatchModel.player_1_id == PlayerModel.id,
            MatchModel.player_2_id == PlayerModel.id,
        ),
    ).filter(
        PlayerModel.id == player_id, MatchModel.jornada == jornada
    ).count()

def max_edges(n, max_aristas):
    return min(n * max_aristas // 2, n * (n - 1) // 2)

def delete_matches_of_jornada(jornada):
    db.session.query(MatchModel).filter_by(jornada=jornada).delete()
    db.session.commit()
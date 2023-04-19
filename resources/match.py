
from itertools import combinations
import random
import time

from .decorators.decorators import secret_header_required

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
    @blp.response(200)
    def get(self):
        matches = MatchModel.query.all()
        matchesAppend = []

        for match in matches:
            player_1 = PlayerModel.query.get(match.player_1_id)
            player_2 = PlayerModel.query.get(match.player_2_id)

            result = ""            
            if(PlayerModel.query.get(match.result)):
                result = PlayerModel.query.get(match.result).username


            matchesAppend.append({
                'result': result,
                'player_1_finished': match.player_1_finished,
                'player_2_finished': match.player_2_finished,
                'jornada': match.jornada,
                'player_1_username': player_1.username,
                'player_2_username': player_2.username,
                'player_1_profile_pic': player_1.profile_pic,
                'player_2_profile_pic': player_2.profile_pic,
            })

        return matchesAppend

@blp.route("/private/generate-matches")
class GenerateMatches(MethodView):
    @blp.arguments(GenerateMatchesSchema)
    @blp.response(201)
    @secret_header_required
    def post(self, match_data):
        jornada = match_data["jornada"]
        nMatches = match_data["nMatches"]
        nPlayers = PlayerModel.query.count()
        lambdaNum = max_edges(nPlayers,nMatches)

        start_time = time.time()

        nMatchesDone = 0
        while nMatchesDone < lambdaNum:
            start_time = time.time()
            while nMatchesDone < lambdaNum and time.time() - start_time < 0.5:
                next_match = get_player_matches()[0]
                player1 = PlayerModel.query.get_or_404(next_match[0])
                player2 = PlayerModel.query.get_or_404(next_match[1])
                if(createSingleMatch(player1, player2, jornada, nMatches)):
                    nMatchesDone += 1

            if nMatchesDone != lambdaNum:
                nMatchesDone = 0 
                time.sleep(max(0, 0.5 - (time.time() - start_time)))
                delete_matches_of_jornada(jornada)
            else:
                return f"Matchmaking optimized, created {nMatchesDone} matches"
        
        return "Matchmaking not optimized, delete matches and restart",403

@blp.route("/private/hardcode-match")
class HardcodeMatch(MethodView):
    @blp.arguments(HardcodeMatchSchema)
    @secret_header_required
    def post(self, match_data):

        player1 = PlayerModel.query.get_or_404(match_data["player_1_id"])
        player2 = PlayerModel.query.get_or_404(match_data["player_2_id"])
        jornada = match_data["jornada"]
        
        msg =  f'Created match between {player1.username} and {player2.username} in jornada {jornada}' if createSingleMatch(player1, player2, jornada, 1) else 'Match could not been created'

        return {"data" : msg}

@blp.route("/private/clean-matches")
class CleanMatches(MethodView):
    @blp.arguments(GenerateMatchesSchema)
    @secret_header_required
    def delete(self, match_data):
        
        jornada = match_data["jornada"]
    
        if (jornada == 0):
            matches = MatchModel.query.all()
        else: 
            matches = MatchModel.query.filter(MatchModel.jornada == jornada).all()

        for match in matches:
            db.session.delete(match)
        db.session.commit()

        return {"msg" : f"{len(matches)} matches deleted"}, 201
    
@blp.route("/fake/matches")
class Matches(MethodView):
    @blp.response(200)
    def get(self):
        return [
            {
                "jornada": 1,
                "player_1_finished": False,
                "player_1_username": "erdeiby",
                "player_2_finished": False,
                "player_2_username": "kmilon",
                "result": "erdeiby"
            },
            {
                "jornada": 1,
                "player_1_finished": False,
                "player_1_username": "john",
                "player_2_finished": False,
                "player_2_username": "avdalian",
                "result": "avdalian"
            },
            {
                "jornada": 1,
                "player_1_finished": False,
                "player_1_username": "avdalian",
                "player_2_finished": False,
                "player_2_username": "erdeiby",
                "result": ""
            },
            {
                "jornada": 1,
                "player_1_finished": False,
                "player_1_username": "guzzom",
                "player_2_finished": False,
                "player_2_username": "avdalian",
                "result": ""
            },
            {
                "jornada": 1,
                "player_1_finished": False,
                "player_1_username": "john",
                "player_2_finished": False,
                "player_2_username": "erdeiby",
                "result": "erdeiby"
            },
            {
                "jornada": 1,
                "player_1_finished": False,
                "player_1_username": "john",
                "player_2_finished": False,
                "player_2_username": "kmilon",
                "result": ""
            },
            {
                "jornada": 1,
                "player_1_finished": False,
                "player_1_username": "guzzom",
                "player_2_finished": False,
                "player_2_username": "kmilon",
                "result": "kmilon"
            },
            {
                "jornada": 2,
                "player_1_finished": False,
                "player_1_username": "guzzom",
                "player_2_finished": False,
                "player_2_username": "erdeiby",
                "result": "guzzom"
            },
            {
                "jornada": 2,
                "player_1_finished": False,
                "player_1_username": "guzzom",
                "player_2_finished": False,
                "player_2_username": "john",
                "result": ""
            },
            {
                "jornada": 2,
                "player_1_finished": False,
                "player_1_username": "avdalian",
                "player_2_finished": False,
                "player_2_username": "kmilon",
                "result": "kmilon"
            },
            {
                "jornada": 2,
                "player_1_finished": False,
                "player_1_username": "erdeiby",
                "player_2_finished": False,
                "player_2_username": "kmilon",
                "result": ""
            },
            {
                "jornada": 2,
                "player_1_finished": False,
                "player_1_username": "avdalian",
                "player_2_finished": False,
                "player_2_username": "erdeiby",
                "result": ""
            },
            {
                "jornada": 2,
                "player_1_finished": False,
                "player_1_username": "john",
                "player_2_finished": False,
                "player_2_username": "kmilon",
                "result": ""
            },
            {
                "jornada": 2,
                "player_1_finished": False,
                "player_1_username": "guzzom",
                "player_2_finished": False,
                "player_2_username": "avdalian",
                "result": ""
            }
        ]

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
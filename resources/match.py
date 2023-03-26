
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from flask_jwt_extended import jwt_required, get_jwt_identity

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models import MatchModel, PlayerModel

from schemas import MatchSchema
from schemas import GenerateMatchesSchema
from schemas import HardcodeMatchSchema

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
        
        createSingleMatch(player1, player2, jornada)
        

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

    match_exists = ((MatchModel.query.filter(MatchModel.player_1_id == player1.id, MatchModel.player_2_id == player2.id).first() or
                            MatchModel.query.filter(MatchModel.player_1_id == player2.id, MatchModel.player_2_id == player1.id).first()) and
                            MatchModel.query.filter(MatchModel.jornada == jornada).first())
            
    if(match_exists):
        abort(403, message="Ya existe este match")

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
    # Obtener todos los partidos de la base de datos
    matches = MatchModel.query.all()

    # Crear un diccionario para mantener un registro de la cantidad de veces que cada par de jugadores ha jugado juntos
    matches_played = {}

    # Iterar sobre la lista de partidos
    for match in matches:
        # Obtener los IDs de los jugadores que participaron en el partido
        player1_id = match.player_1_id
        player2_id = match.player_2_id

        # Ordenar los IDs para que siempre se almacenen en el mismo orden
        players = sorted([player1_id, player2_id])

        # Actualizar el diccionario con la información de los jugadores que han participado en ese partido
        if tuple(players) not in matches_played:
            matches_played[tuple(players)] = 1
        else:
            matches_played[tuple(players)] += 1

    # Crear una lista de tuplas para cada par de jugadores y la cantidad de partidos que han jugado juntos
        player_matches = []
        for players, count in matches_played.items():
            player1 = PlayerModel.query.get(players[0])
            player2 = PlayerModel.query.get(players[1])
            player_matches.append((player1.username, player2.username, count))

        # Devolver la lista de partidos por jugador
        return player_matches
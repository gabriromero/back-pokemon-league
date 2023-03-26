
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
        player1_id = 1 # reemplazar con el ID del jugador 1
        player2_id = 2 # reemplazar con el ID del jugador 2
        
        match_data = {
            'player_1_id': player1_id,
            'player_2_id': player2_id,
            'jornada': jornada
        }

        # llama internamente al endpoint /private/hardcode-match
        response = HardcodeMatch().post(match_data)
        # procesa la respuesta según sea necesario
        
        return 'Llamadas completadas'

@blp.route("/private/hardcode-match")
class HardcodeMatch(MethodView):
    @blp.arguments(HardcodeMatchSchema)
    def post(self, match_data):

        player1 = PlayerModel.query.get_or_404(match_data["player_1_id"])
        player2 = PlayerModel.query.get_or_404(match_data["player_2_id"])

        match_exists = ((MatchModel.query.filter(MatchModel.player_1_id == player1.id, MatchModel.player_2_id == player2.id).first() or
                        MatchModel.query.filter(MatchModel.player_1_id == player2.id, MatchModel.player_2_id == player1.id).first()) and
                        MatchModel.query.filter(MatchModel.jornada == match_data["jornada"]).first())
        
        if(match_exists):
            abort(403, message="Ya existe este match")

        match = MatchModel(**match_data)

        try:
            db.session.add(match)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="Integrity error creating a match",
            )
        except SQLAlchemyError:
            abort(500, message="An error occurred creating a match.")
    
        return {"msg" : f"Partido entre {player1.username} y {player2.username} creado"}, 201
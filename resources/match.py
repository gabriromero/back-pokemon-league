
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from flask_jwt_extended import jwt_required, get_jwt_identity

from sqlalchemy.exc import IntegrityError

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
        return match_data["jornada"]

@blp.route("/private/hardcode-match")
class HardcodeMatch(MethodView):
    @blp.arguments(HardcodeMatchSchema)
    @blp.response(200)
    def post(self, match_data):
        return match_data["jornada"]
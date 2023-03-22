
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from flask_jwt_extended import jwt_required, get_jwt_identity

from sqlalchemy.exc import IntegrityError

from db import db
from models import MatchModel, PlayerModel
from schemas import MatchSchema

        
blp = Blueprint("Matches", __name__, description="Match operations")

@blp.route("/private/matches")
class PrivateMatches(MethodView):
    @blp.response(200, MatchSchema(many=True))
    def get(self):
        return MatchModel.query.all()
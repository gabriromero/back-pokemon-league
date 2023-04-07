
from .decorators.decorators import secret_header_required

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from flask_jwt_extended import jwt_required, get_jwt_identity

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models import JornadaModel

from schemas import PutJornadaSchema

blp = Blueprint("Jornadas", __name__, description="Jornada operations")

@blp.route("/jornada-actual")
class Matches(MethodView):
    @blp.response(200)
    def get(self):
        return JornadaModel.query.filter_by(id=1).first().jornada_actual
    
@blp.route("/jornada-actual")
class Matches(MethodView):
    @blp.arguments(PutJornadaSchema)
    @blp.response(200)
    def put(self, jornada_data):
        jornada =  JornadaModel.query.filter_by(id=1).first()
        nuevaJornada = jornada_data["nuevaJornada"]
        jornada.jornada_actual = nuevaJornada
        db.session.commit()

        return f"New jornada actual: {nuevaJornada}"

@blp.route("/jornada-actual")
class Matches(MethodView):
    @blp.response(200)
    def post(self):
        jornada = JornadaModel(
            jornada_actual = 1,
        )

        try:
            db.session.add(jornada)
            db.session.commit()
        except IntegrityError:
            abort(400)

        return jornada
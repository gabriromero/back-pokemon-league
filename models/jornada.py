from db import db

class JornadaModel(db.Model):
    __tablename__ = "jornadas"

    id = db.Column(db.Integer, primary_key=True)
    jornada_actual = db.Column(db.Integer, default=1)
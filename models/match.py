from db import db

class MatchModel(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    jornada = db.Column(db.Integer, unique=False, nullable=False)

from db import db

class MatchModel(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    player_1 = db.Column(db.Integer, db.ForeignKey('players.id'), unique=False, nullable=False)
    player_2 = db.Column(db.Integer, db.ForeignKey('players.id'), unique=False, nullable=False)
    result = db.Column(db.Integer, unique=False, nullable=False)
    player_1_finished = db.Column(db.Boolean, unique=False, nullable=False)
    player_2_finished = db.Column(db.Boolean, unique=False, nullable=False)
    jornada = db.Column(db.Integer, unique=False, nullable=False)
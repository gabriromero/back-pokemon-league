from db import db

class MatchModel(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Integer, default=0)
    player_1_finished = db.Column(db.Boolean, default=0)
    player_2_finished = db.Column(db.Boolean, default=0)
    jornada = db.Column(db.Integer, nullable=False)

    player_1_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), unique=False, nullable=False
    )
    player_2_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), unique=False, nullable=False
    )
from db import db

class PlayerModel(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    profile_pic = db.Column(db.String(255), default='trainerPixel')
    matches_played = db.Column(db.Integer, default=0)
    matches_won = db.Column(db.Integer, default=0)

    matches = db.relationship("MatchModel", back_populates="player", lazy="dynamic")
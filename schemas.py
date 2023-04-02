from marshmallow import Schema, fields, validate

# Player schema
class ClassificationSchema(Schema):
    username = fields.Str(required=True, validate=[validate.Length(min=3, max=12)])
    matches_won = fields.Int()

class ProfileSchema(Schema):
    username = fields.Str(required=True, validate=[validate.Length(min=3, max=12)])
    profile_pic = fields.Str(required=True)
    matches_played = fields.Int()
    matches_won = fields.Int()

class PrivatePlayersSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=[validate.Length(min=3, max=12)])
    profile_pic = fields.Str(required=True)
    matches_played = fields.Int()
    matches_won = fields.Int()
    matches_won_frozen = fields.Int()

class CreatePlayerSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=[validate.Length(min=3, max=12)])
    password = fields.Str(required=True, validate=[validate.Length(min=3, max=12)])

class DeletePlayerSchema(Schema):
    id = fields.Int(required=True)

class LoginPlayerSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class ProfileUpdateSchema(Schema):
    profile_pic  = fields.Str()

class MarkResultSchema(Schema):
    jornada = fields.Int(required=True, validate=[validate.Range(min=0, max=10)])
    player_1_username = fields.Str(required=True)
    player_2_username = fields.Str(required=True)
    player_winner_username = fields.Str(required=True)

# Match Schema
class MatchSchema(Schema):
    jornada = fields.Int(required=True, validate=[validate.Range(min=1, max=9)])
    player_1_id = fields.Int(required=True)
    player_2_id = fields.Int(required=True)
    player_1_finished = fields.Int(required=True)
    player_2_finished = fields.Int(required=True)
    result = fields.Int(required=True)

class MatchDiferenciaSchema(Schema):
    jornada = fields.Int(required=True, validate=[validate.Range(min=1, max=9)])
    player_1_id = fields.Int(required=True)
    player_1_username = fields.Str(required=True, validate=[validate.Length(min=3, max=12)])
    player_2_id = fields.Int(required=True)
    player_2_username = fields.Str(required=True, validate=[validate.Length(min=3, max=12)])
    player_1_finished = fields.Int(required=True)
    player_2_finished = fields.Int(required=True)
    result = fields.Int(required=True) 
    diferencia = fields.Int(required=True) 

class GenerateMatchesSchema(Schema):
    jornada = fields.Int(required=True, validate=[validate.Range(min=0, max=10)])
    nMatches = fields.Int(validate=[validate.Range(min=2, max=10)])

class HardcodeMatchSchema(Schema):
    jornada = fields.Int(required=True, validate=[validate.Range(min=1, max=10)])
    player_1_id = fields.Int(required=True)
    player_2_id = fields.Int(required=True)


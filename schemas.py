from marshmallow import Schema, fields, validate

# Player schema
class ClassificationSchema(Schema):
    username = fields.Str(required=True, validate=[validate.Length(min=3, max=12)])
    matches_won = fields.Int()

class CreatePlayerSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=[validate.Length(min=3, max=12)])
    password = fields.Str(required=True, validate=[validate.Length(min=3, max=12)])

# Match Schema
class MatchSchema(Schema):
    id = fields.Int(dump_only=True)
    jornada = fields.Int(required=True, validate=[validate.Range(min=1, max=9)])
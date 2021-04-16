from mongoengine import Document, FloatField, StringField, IntField


class Rooms(Document):
    roomID = StringField(required=True, primary_key=True)
    roomType = StringField(required=True)
    person = IntField(required=True, default=0)
    price = FloatField(required=True, min_value=0)
    room_status = StringField(required=True)


class RoomsCheckIn(Document):
    roomID = StringField(required=True, primary_key=True)
    transactionID = StringField(required=True)
    userID = StringField(required=True)
    roomType = StringField(required=True)
    person = IntField(required=True, default=0)
    price = FloatField(required=True, min_value=0)
    room_status = StringField(required=True)

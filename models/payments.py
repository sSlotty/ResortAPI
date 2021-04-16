from mongoengine import Document, StringField, FloatField


class Payments(Document):
    paymentID = StringField(required=True, primary_key=True)
    transactionID = StringField(required=True)
    userID = StringField(required=True)
    guestID = StringField(required=True)
    room_price = FloatField(required=True)
    total_bill = FloatField(required=True)
    status = StringField(required=True)

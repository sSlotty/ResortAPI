from mongoengine import Document, StringField, IntField, DateTimeField
from datetime import datetime


class Transactions(Document):
    transactionID = StringField(required=True, primary_key=True)
    userID = StringField(required=True)
    guestID = StringField(required=True)
    roomID = StringField(required=True)
    transaction_date = DateTimeField(required=True, default=datetime.utcnow())
    check_in = StringField(required=False)
    check_out = StringField(required=False)
    total_bill = StringField(required=False)
    status = StringField(required=True)
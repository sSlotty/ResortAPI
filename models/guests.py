from mongoengine import Document, StringField,ObjectIdField


class Guests(Document):
    guestID = StringField(required=True, primary_key=True)
    name = StringField(required=True)
    tel = StringField(required=True, max_length=10)

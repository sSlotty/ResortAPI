from mongoengine import Document, StringField,ObjectIdField


class Guests(Document):
    _id = StringField(required=True, primary_key=True)
    userID = StringField(required=True)
    name = StringField(required=True)
    tel = StringField(required=True, max_length=10)

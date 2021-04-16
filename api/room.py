from flask import request, Response, jsonify, current_app
from flask_restful import Resource

from models.rooms import Rooms
from mongoengine import NotUniqueError
from kanpai import Kanpai


class RoomAPI(Resource):

    def post(self) -> Response:
        body = request.get_json()

        roomID = Rooms.objects(roomID=body['roomID'])
        if not len(roomID) > 0:
            schema = Kanpai.Object({
                'roomID': Kanpai.String().required(),
                'roomType': Kanpai.String().required(),
                'person': Kanpai.String().required(),
                'price': Kanpai.String().required(),
                'room_status': Kanpai.String().required(),
            })
            validate_result = schema.validate(body)
            if validate_result.get('success', False) is False:
                return Response(status=400)

            try:
                room = Rooms(**body)
                room.save()
                response = Response()
                response.status_code = 201
                return response
            except NotUniqueError:
                return Response('room id is already exist', 400)
        else:
            return Response('room id is already exist', 400)

    def get(self) -> Response:
        room = Rooms.objects()
        if len(room) > 0:
            response = jsonify(room)
            response.status_code = 200
            return response
        else:
            response = Response()
            response.status_code = 204
            return response


class RoomIdAPI(Resource):
    def get(self) -> Response:
        roomID = request.args.get('roomID')
        room = Rooms.objects(roomID=roomID)
        if len(room) > 0:
            response = jsonify(room)
            response.status_code = 200
            return response
        else:
            response = Response()
            response.status_code = 204
            return response

    def put(self) -> Response:
        body = request.get_json()
        roomID = Rooms.objects(roomID=body['roomID'])
        if len(roomID) > 0:

            schema = Kanpai.Object({
                'roomID': Kanpai.String().required(),
                'roomType': Kanpai.String().required(),
                'person': Kanpai.String().required(),
                'price': Kanpai.String().required(),
                'room_status': Kanpai.String().required(),
            })
            validate_result = schema.validate(body)
            if validate_result.get('success', False) is False:
                return Response(status=400)

            Rooms.objects(roomID=body['roomID']).update(
                set__roomType=body['roomType'],
                set__person=body['person'],
                set__price=body['price'],
                set__room_status=body['room_status']
            )
            response = Response("Success to updated room")
            response.status_code = 200
            return response
        else:
            return Response("Not have room ID :" + roomID, status=400)

    def delete(self) -> Response:
        body = request.get_json()
        room = Rooms.objects(roomID=body['roomID'])
        if len(room) > 0:
            room.delete()
            res = Response("Success to deltete room ID : " + body['roomID'])
            res.status_code = 200
            return res
        else:
            response = Response("no have room ID" + body['roomID'], status=400)
            return response

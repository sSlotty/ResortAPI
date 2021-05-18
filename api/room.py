import json
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
                res = jsonify({"data": [body], "message": "Argument error", "status": 400})
                res.status_code = 400
                return res

            try:
                room = Rooms(**body)
                room.save()
                res = jsonify({"data": [body], "message": "success", "status": 201})
                res.status_code = 201
                return res
            except NotUniqueError:
                res = jsonify({"data": [body], "message": "error", "status": 400})
                res.status_code = 400
                return res
        else:
            res = jsonify({"data": [body], "message": "error", "status": 400})
            res.status_code = 400
            return res

    def get(self) -> Response:
        room = Rooms.objects()
        if len(room) > 0:
            res = jsonify({"data": room, "message": "success", "status": 200})
            res.status_code = 200
            return res
        else:
            response = jsonify({"data": "null", "message": "error", "status": 204})
            response.status_code = 204
            return response


class RoomIdAPI(Resource):
    def get(self) -> Response:
        roomID = request.args.get('roomID')
        room = Rooms.objects(roomID=roomID)
        if len(room) > 0:
            res = jsonify({"data": room, "message": "success", "status": 200})
            res.status_code = 200
            return res
        else:
            res = jsonify({"data": "null", "message": "error", "status": 204})
            res.status_code = 204
            return res

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

            res = jsonify({"data": [body], "message": "success", "status": 200})
            res.status_code = 200
            return res
        else:
            res = jsonify({"data": body, "message": "error", "status": 400})
            res.status_code = 400
            return res

    def delete(self) -> Response:
        body = request.get_json()
        room = Rooms.objects(roomID=body['roomID'])
        if len(room) > 0:
            room.delete()
            res = jsonify({"data": room, "message": "success", "status": 200})
            res.status_code = 200
            return res
        else:
            res = jsonify({"data": body, "message": "error", "status": 400})
            res.status_code = 400
            return res


class RoomStatus(Resource):
    def get(self) -> Response:
        status = request.args.get('status')
        room = Rooms.objects(room_status=status)
        if len(room) > 0:
            res = jsonify({"data": room, "message": "success", "status": 200})
            res.status_code = 200
            return res
        else:
            res = jsonify({"data": status, "message": "error", "status": 204})
            res.status_code = 204
            return res

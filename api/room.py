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
                return jsonify({"data":[body], "message":"Argument error","status":400})

            try:
                room = Rooms(**body)
                room.save()
            
                return jsonify({"data":[body], "message":"success","status":201})
            except NotUniqueError:
                return jsonify({"data":[body], "message":"error","status":400})
        else:
            return jsonify({"data":[body], "message":"error","status":400})

    def get(self) -> Response:
        room = Rooms.objects()
        if len(room) > 0:
            
            return jsonify({"data":room, "message":"success","status":200})
        else:
            response = Response()
            response.status_code = 204
            return jsonify({"data":"null", "message":"error","status":204})


class RoomIdAPI(Resource):
    def get(self) -> Response:
        roomID = request.args.get('roomID')
        room = Rooms.objects(roomID=roomID)
        if len(room) > 0:
        
            return jsonify({"data":room, "message":"success","status":200})
        else:
        
            return jsonify({"data":"null", "message":"error","status":204})

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
            
            return jsonify({"data":[body], "message":"success","status":200})
        else:
            return jsonify({"data":body, "message":"error","status":400})

    def delete(self) -> Response:
        body = request.get_json()
        room = Rooms.objects(roomID=body['roomID'])
        if len(room) > 0:
            room.delete()
            
            return jsonify({"data":room, "message":"success","status":200})
        else:
            
            return jsonify({"data":body, "message":"error","status":400})


class RoomStatus(Resource):
    def get(self) -> Response:
        status = request.args.get('status')
        room = Rooms.objects(room_status=status)
        if len(room) > 0:
            return jsonify({"data":room, "message":"success","status":200})
        else:
            
            return jsonify({"data":status, "message":"error","status":204})

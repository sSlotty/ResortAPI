import time

from bson import json_util
from flask import request, Response, jsonify, current_app
from flask_restful import Resource

from models.guests import Guests
from models.users import Users
from mongoengine import *
import json

import uuid

class GuestAPI(Resource):

    def post(self) -> Response:
        body = request.get_json()
        guest = Guests.objects(guestID=body['guestID'])
        if not len(guest) > 0:

            Guests(**body).save()
            return jsonify({"data":body, "message":"","status":200})
        else:
            return jsonify({"data":body, "message":"Already have user id","status":400})
       

    def get(self) -> Response:
        guest = Guests.objects()
        if len(guest) > 0:
            
            return jsonify({"data":guest ,"message":"success","status": 200})
        else:
            response = jsonify({"data":"error","message":"error","status":204})
            return response

    def put(self)->Response:
        body = request.get_json()
        guest = Guests.objects(guestID=body['guestID'])
        if len(guest) > 0:
            print(body)
            Guests.objects(guestID=body['guestID']).update(
                set__name=body['name'],
                set__tel=str(body['tel'])
            )

            # print(type(body))
            return jsonify({"data":[body],"message":"success","status":200})
        else:
            return jsonify({"data":"Not have guest ID" ,"message":"error","status": 400})


class GuestIdAPI(Resource):

    def get(self) -> Response:
        guestID = request.args.get('guestID')
        guest = Guests.objects(guestID=guestID)
        if len(guest) > 0:
        
            
            return jsonify({"data":guest ,"message":"success","status": 200})
        else:
            return Response(jsonify({"data":"Not have guest ID" ,"message":"error","status": 400}))

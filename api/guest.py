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

            res = Guests(**body).save()
            return Response(status=201)
        else:
            return Response("Already have guestID", status=400)
       

    def get(self) -> Response:
        guest = Guests.objects()
        if len(guest) > 0:
            response = jsonify(guest)
            response.status_code = 200
            return response
        else:
            response = Response()
            response.status_code = 204
            return response


class GuestIdAPI(Resource):

    def get(self) -> Response:
        guestID = request.args.get('guestID')
        guest = Guests.objects(guestID)
        if len(guest) > 0:
        
            response = jsonify(guest)
            response.status_code = 200
            return response
        else:
            return Response("No have guest ID", status=400)

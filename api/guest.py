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

        key = str(uuid.uuid4().int)[3,7]
        data = {
            '_id': key,
            'userID': body['userID'],
            'name': body['name'],
            'tel': body['tel']
        }

        guest = Guests(**data)
        guest.save()
        return Response(status=201)

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
        _id = request.args.get('_id')
        guest = Guests.objects(_id=_id)
        if len(guest) > 0:
            pipline = [
                {"$match": {"_id": _id}},
                {"$lookup":
                     {'from': 'users', 'localField': 'userID', 'foreignField': '_id', 'as': 'users'},
                 }
            ]
            cursor = Guests.objects.aggregate(pipline)

            ls_guest = list(cursor)
            user = list(ls_guest[0]['users'])

            data = {
                'guest_id': ls_guest[0]["_id"],
                'guest_name': ls_guest[0]['name'],
                'guest_tel': ls_guest[0]['tel'],
                'staff_id': user[0]['_id'],
                'staff_tel': user[0]['tel'],
                'staff_gender': user[0]['gender'],
                'staff_job_position': user[0]['job_position']
            }

            response = jsonify(data)
            response.status_code = 200
            return response
        else:
            return Response("No have guest ID", status=400)

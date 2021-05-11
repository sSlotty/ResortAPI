import time
from datetime import datetime

from flask import request, Response, jsonify, current_app
from flask_restful import Resource

from mongoengine import DoesNotExist, NotUniqueError
from kanpai import Kanpai
from models.rooms import RoomsCheckIn, Rooms
from models.transactions import Transactions
from models.payments import Payments

import uuid
class TransactionAPI(Resource):
    def post(self) -> Response:

        body = request.get_json()
        schema = Kanpai.Object({
            'userID': Kanpai.String().required(),
            'guestID': Kanpai.String().required(),
            'roomID': Kanpai.String().required(),
            'transaction_date': Kanpai.String(),
            'check_in': Kanpai.String().required()
        })
        print(body)

        validate_result = schema.validate(body)
        if validate_result.get('success', False) is False:
            return Response(status=400)

        room_id = Rooms.objects(roomID=body['roomID']).values_list('room_status')
        filter_status = list(room_id)
        status = filter_status[0]

        if status == "False":
            if len(room_id) > 0:
                key = uuid.uuid4().int
                data = {
                    'transactionID': str(key)[3,7],
                    'userID': body['userID'],
                    'guestID': body['guestID'],
                    'roomID': body['roomID'],
                    'transaction_date': datetime.utcnow(),
                    'check_in': body['check_in'],
                    'status': 'False'
                }
                transaction = Transactions(**data)
                transaction.save()

                Rooms.objects(roomID=body['roomID']).update(
                    set__room_status="true"
                )
                response = Response()
                response.status_code = 201
                return response

            else:
                return Response("No have room number", status=400)
        else:
            return Response("Room is not alivable", status=400)

    def get(self) -> Response:
        transaction = Transactions.objects()
        if len(transaction) > 0:
            response = jsonify(transaction)
            response.status_code = 200
            return response
        else:
            response = Response()
            response.status_code = 204
            return response


class TransactionIdAPI(Resource):
    def get(self) -> Response:

        transactionID = request.args.get('transactionID')

        transaction = Transactions.objects(transactionID=transactionID)
        if len(transaction) > 0:
            pipline = [
                {"$match": {"_id": transactionID}},
                {"$lookup":
                     {'from': 'users', 'localField': 'userID', 'foreignField': '_id', 'as': 'users'},
                 },
                {"$lookup":
                     {'from': 'guests', 'localField': 'guestID', 'foreignField': '_id', 'as': 'guest'}
                 },
                {"$lookup":
                     {'from': 'rooms', 'localField': 'roomID', 'foreignField': '_id', 'as': 'room'}
                 }
            ]

            cursor = Transactions.objects.aggregate(pipline)
            cursor_list = list(cursor)
            guest = list(cursor_list[0]['guest'])
            user = list(cursor_list[0]['users'])
            room = list(cursor_list[0]['room'])

            data = {
                'transactionID': cursor_list[0]['_id'],
                'transaction_date': cursor_list[0]['transaction_date'],
                'room': {
                    'roomNum': room[0]['_id'],
                    'type': room[0]['roomType'],
                    'price': room[0]['price'],
                },
                'guest': {
                    'guest_id': guest[0]['_id'],
                    'name': guest[0]['name'],
                    'tel': guest[0]['tel'],
                },
                'staff': {
                    'user_id': user[0]['_id'],
                    'name': user[0]['name'],
                    'tel': user[0]['tel'],
                }
            }

            response = jsonify(data)
            response.status_code = 200
            return response
        else:
            return Response("No have guest ID", status=400)


class CheckOutAPI(Resource):
    def post(self) -> Response:
        body = request.get_json()
        transaction = body['transactionID']
        pipline = [
            {"$match": {"_id": transaction}},
            {"$lookup":
                 {'from': 'users', 'localField': 'userID', 'foreignField': '_id', 'as': 'users'},
             },
            {"$lookup":
                 {'from': 'guests', 'localField': 'guestID', 'foreignField': '_id', 'as': 'guest'}
             },
            {"$lookup":
                 {'from': 'rooms', 'localField': 'roomID', 'foreignField': '_id', 'as': 'room'}
             }
        ]
        x = Transactions.objects.aggregate(pipline)
        y = list(x)
        local = list(y)

        if local[0]['status'] == 'False':
            guest = local[0]['guest']
            staff = local[0]['users']
            room = local[0]['room']

            key = uuid.uuid4().int
            checkIN = str(local[0]['check_in']).format("%Y-%m-%d")
            checkOUT = body['check_out']
            days = days_between(checkIN, checkOUT)

            price = days * int(room[0]['price'])

            data = {
                'transactionID': transaction,
                'room': room[0],
                'price': price,
                'guest': {
                    'name': guest[0]['name'],
                    'tel': guest[0]['tel']
                },
                'staff': {
                    'name': staff[0]['name'],
                },
                'check_in': checkIN,
                'check_out': checkOUT
            }

            Transactions.objects(transactionID=transaction).update(
                set__status="True",
                set__check_out=checkOUT
            )
            data_payment = {
                'paymentID': str(key)[3,7],
                'transactionID': transaction,
                'userID': staff[0]['_id'],
                'guestID': guest[0]['_id'],
                'room_price': room[0]['price'],
                'total_bill': price,
                'status': 'False'
            }

            try:
                payment = Payments(**data_payment)
                payment.save()

                udRoom = Rooms.objects(roomID=room[0]['_id']).update(
                    set__room_status='False'
                )

                res = jsonify(data)
                res.status_code = 200
                return res
            except NotUniqueError:
                return Response(status=400)
        else:
            return Response(status=400)

    def get(self)->Response:
        transaction = Transactions.objects()
        if len(transaction) > 0:
            response = jsonify(transaction)
            response.status_code = 200
            return response
        else:
            response = Response()
            response.status_code = 204
            return response


class getAllTransacByStatus(Resource):

    def get(self)->Response:
        status = request.args.get('status')
        transac = Transactions.objects(status=status)
        if len(transac) > 0:
            response = jsonify(transac)
            response.status_code = 200
            return response
        else:
            return Response(status=240)



class CheckOutIdAPI(Resource):

    def get(self)->Response:
        id = request.args.get('id')
        transac = Transactions.objects(transactionID=id)
        if len(transac) > 0:
            response = jsonify(transac)
            response.status_code = 200
            return response
        else:
            return Response(status=240)

    def post(self)->Response:
        body = request.get_json()
        id = body['id']
        payment = Payments.objects(transactionID=id)

        if len(payment) > 0:
            Payments.objects(transactionID=id).update(
                set__status='False'
            )
            response = Response()
            response.status_code = 200
            return response
        else:
            return Response(status=400)




def days_between(d1, d2):
    d1 = datetime.strptime(str(d1), "%Y-%m-%d")
    d2 = datetime.strptime(str(d2), "%Y-%m-%d")
    return abs((d2 - d1).days)

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

        room_id = Rooms.objects(roomID=body['roomID']).values_list('room_status')
        filter_status = list(room_id)
        status = filter_status[0]

        if status == "True":
            if len(room_id) > 0:
                key = uuid.uuid4().int
                data = {
                    'transactionID': str(key)[0:6],
                    'userID': body['userID'],
                    'guestID': body['guestID'],
                    'roomID': body['roomID'],
                    'transaction_date': datetime.utcnow(),
                    'check_in': body['check_in'],
                    'check_out': "None",
                    'total_bill': "None",
                    'status': 'False'
                }
                transaction = Transactions(**data)
                transaction.save()

                Rooms.objects(roomID=body['roomID']).update(
                    set__room_status="False"
                )

                res = jsonify({"data":[None], "message":"success","status":201})
                res.status_code = 201
                return res

            else:
                res = jsonify({"data":[None], "message":"No have room number","status":400})
                res.status_code = 400
                return res
        else:
            res = jsonify({"data":[None], "message":"Room is not alivable","status":400})
            res.status_code = 400
            return res

    def get(self) -> Response:
        transaction = Transactions.objects().all().values_list('transactionID','guestID','roomID','check_in','status','check_out','total_bill')
        if len(transaction) > 0:
            res = jsonify({"data":transaction, "message":"success","status":200})
            res.status_code = 200
            return res
        else:
            res = jsonify({"data":"null", "message":"error","status":204})
            res.status_code = 204
            return res


class TransactionIdAPI(Resource):
    def get(self) -> Response:

        transactionID = request.args.get('transactionID')

        transaction = Transactions.objects(transactionID=transactionID)
        print(len(transaction))
        if len(transaction) > 0:
            pipline = [
                {"$match": {"_id": transactionID}},
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
            room = list(cursor_list[0]['room'])

            data = {
                'transactionID': cursor_list[0]['_id'],
                'check_in': cursor_list[0]['check_in'],
                'check_out': cursor_list[0]['check_out'],
                'total_bill': cursor_list[0]['total_bill'],
                'roomNum': room[0]['_id'],
                'roomType': room[0]['roomType'],
                'roomPrice': room[0]['price'],
                'guestID': guest[0]['_id'],
                'guestName': guest[0]['name'],
                'guestTel': guest[0]['tel'],
            }
            print(data)

            res = jsonify({"data":[data], "message":"success","status":200})
            res.status_code = 200
            return res
        else:
            res = jsonify({"data":"null", "message":"no have guestID","status":204})
            res.status_code = 204
            return res


class CheckOutAPI(Resource):
    def post(self) -> Response:
        body = request.get_json()
        transaction = body['transactionID']
        pipline = [
            {"$match": {"_id": transaction}},
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
            room = local[0]['room']

            key = uuid.uuid4().int
            checkIN = str(local[0]['check_in']).format("%Y-%m-%d")
            checkOUT = body['check_out']
            days = days_between(checkIN, checkOUT)

            price = days * int(room[0]['price'])

            data = {
                'transactionID': transaction,
                'room': room[0],
                'roomID':room[0]["_id"],
                'roomType':room[0]["_id"],
                'roomID':room[0]["_id"],
                'roomID':room[0]["_id"],

                'price': price,
                'guest': {
                    'name': guest[0]['name'],
                    'tel': guest[0]['tel']
                },
                'check_in': checkIN,
                'check_out': checkOUT
            }

            Transactions.objects(transactionID=transaction).update(
                set__status="True",
                set__check_out=checkOUT,
                set__total_bill=str(price),
            )
            data_payment = {
                'paymentID': str(key)[0:5],
                'transactionID': transaction,
                'guestID': guest[0]['_id'],
                'room_price': room[0]['price'],
                'total_bill': price,
                'status': 'False'
            }

            try:
                payment = Payments(**data_payment)
                payment.save()

                Rooms.objects(roomID=room[0]['_id']).update(
                    set__room_status='True'
                )

                res = jsonify({"data":[None], "message":"success","status":200})
                res.status_code = 200
                return res
            except NotUniqueError:
                res = jsonify({"data":"null", "message":"error","status":400})
                res.status_code = 400
                return res
        else:
            res = jsonify({"data":"null", "message":"error","status":400})
            res.status_code = 400
            return res

    def get(self)->Response:
        transaction = Transactions.objects()
        if len(transaction) > 0:
            res = jsonify({"data":transaction, "message":"success","status":200})
            res.status_code = 200
            return res
        else:
            res = jsonify({"data":"null", "message":"error","status":204})
            res.status_code = 204
            return res


class getAllTransacByStatus(Resource):

    def get(self)->Response:
        status = request.args.get('status')
        transac = Transactions.objects(status=status)
        if len(transac) > 0:
            res = jsonify({"data":transac, "message":"success","status":200})
            res.status_code = 200
            return res
        else:
            res = jsonify({"data":"null", "message":"error","status":204})
            res.status_code = 204
            return res



class CheckOutIdAPI(Resource):

    def get(self)->Response:
        id = request.args.get('id')
        transac = Transactions.objects(transactionID=id)
        if len(transac) > 0:
            res = jsonify({"data":transac, "message":"success","status":200})
            res.status_code = 200
            return res
        else:
            res = jsonify({"data":"null", "message":"error","status":204})
            res.status_code = 204
            return res

    def post(self)->Response:
        body = request.get_json()
        id = body['id']
        payment = Payments.objects(transactionID=id)

        if len(payment) > 0:
            Payments.objects(transactionID=id).update(
                set__status='False'
            )
            
            res = jsonify({"data":payment, "message":"success","status":200})
            res.status_code = 200
            return res
        else:
            res = jsonify({"data":"null", "message":"error","status":204})
            res.status_code = 204
            return res




def days_between(d1, d2):
    d1 = datetime.strptime(str(d1), "%Y-%m-%d")
    d2 = datetime.strptime(str(d2), "%Y-%m-%d")
    return abs((d2 - d1).days)

from flask_restful import Api

from api.authentication import SignUpAPI, TokenAPI, RefreshToken, getUserAPI

from api.guest import GuestIdAPI, GuestAPI
from api.room import RoomIdAPI, RoomAPI
from api.transaction import TransactionIdAPI, TransactionAPI, CheckOutAPI, getAllTransacByStatus, CheckOutIdAPI


def create_route(api: Api):
    api.add_resource(SignUpAPI, '/authentication/signup')
    api.add_resource(TokenAPI, '/authentication/token')
    api.add_resource(RefreshToken, '/authentication/token/refresh')
    api.add_resource(getUserAPI, '/getuser')

    api.add_resource(GuestAPI, '/guests')
    api.add_resource(GuestIdAPI, '/guests/id')

    api.add_resource(RoomAPI, '/rooms')
    api.add_resource(RoomIdAPI, '/rooms/id')

    api.add_resource(TransactionAPI, '/transactions')  # Checkin
    api.add_resource(TransactionIdAPI, '/transactions/id')  # get Transaction by id
    api.add_resource(getAllTransacByStatus, '/transactions/status')  # get all transaction and status transaction

    api.add_resource(CheckOutAPI, '/checkout')  # checkout transaction and add data to payment
    api.add_resource(CheckOutIdAPI, '/payment/id')  # get payment and confirm checkout to get money

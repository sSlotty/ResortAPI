import time
from datetime import datetime

from flask import request, Response, jsonify, current_app
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    jwt_required,
    get_jwt_identity
)
import json

from mongoengine import DoesNotExist

from models.oauth.error import OAuthErrorResponse
from models.oauth.token import TokenResponse
from models.users import Users
import uuid

class SignUpAPI(Resource):
    # Register
    def post(self) -> Response:
        body = request.get_json()

        user = Users.objects(username=body['username'])

        if not len(user) > 0:
            key = uuid.uuid4().int
            data = {
                'staffID': str(key)[0:6],
                'username': body['username'],
                'password': body['password'],
                'name': body['name'],
                'tel': body['tel']
            }

            user = Users(**data)
            user.save()
            res = jsonify({"data":[data], "message":"success","status":201})
            res.status_code = 201
            return res
        else:
            res = jsonify({"data":[body], "message":"error","status":400})
            res.status_code = 400
            return res

class TokenAPI(Resource):
    # Login
    def post(self) -> Response:
        body = request.get_json()
        if body.get is None or body.get is None:
            response = jsonify(
                OAuthErrorResponse(
                    "invalid_request", "The request is missing a required parameter."
                ).__dict__
            )
            response.status_code = 400
            return response

        try:
            user: Users = Users.objects.get(username=body.get('username'))
            auth_success = user.check_pw_hash(body.get('password'))
            if not auth_success:
                response = jsonify(
                    OAuthErrorResponse(
                        "invalid_grant", "The username or password is incorrect."
                    ).__dict__
                )
                response.status_code = 400
                return response
            else:
                return generate_token_response(str(user.id))
        except DoesNotExist:
            response = jsonify(
                OAuthErrorResponse(
                    "invalid_grant", "The username or password is incorrect."
                ).__dict__
            )
        response.status_code = 400
        return response


class RefreshToken(Resource):
    # Refresh token
    @jwt_required(refresh=True)
    def post(self):
        user = get_jwt_identity()
        return generate_token_response(user)


def generate_token_response(user: str):
    # Genarate token
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    response = jsonify(
        TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            refresh_token=refresh_token
        ).__dict__
    )
    response.status_code = 200
    # set_access_cookies(response, access_token)
    return response

class getUserAPI(Resource):
    def get(self) -> Response:
        user = Users.objects().values_list("username","name","staffID","tel")
        if len(user) > 0:
            res = jsonify({"data":user, "message":"success","status":200})
            res.status_code = 200
            return res
        else:
            res = jsonify({"data":"null", "message":"error","error":204})
            res.status_code = 204
            return res

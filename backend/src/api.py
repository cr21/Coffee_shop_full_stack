import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and
    json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# public route


@app.route("/drinks", methods=["GET"])
def get_drinks():
    # fetch all drinks Data
    drinks = Drink.query.all()
    print(drinks)
    drinks = [drink.short() for drink in drinks]
    response = {}
    response["status_code"] = 200
    response["success"] = True
    response["drinks"] = drinks

    return jsonify(response), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and
    json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drink_detail_records(payload):
    drinks = Drink.query.all()
    # print(drinks)
    drinks = [drink.long() for drink in drinks]
    response = {}
    response["status_code"] = 200
    response["success"] = True
    response["drinks"] = drinks

    return jsonify(response), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and
    json {"success": True, "drinks": drink} where
     drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def add_new_drink(payload):
    response = {}
    try:
        body = request.get_json()
        req_title = body.get("title")
        req_recipe = body.get("recipe")

        if isinstance(req_recipe, dict):
            req_recipe = [req_recipe]

        drink = Drink(title=req_title, recipe=json.dumps(req_recipe))
        drink.insert()
    except BaseException:
        print(sys.exc_info())
        abort(400)
    return jsonify({"success": True, "drinks": [drink.long()]}), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and
    json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int: id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    body = request.get_json()
    title = body.get("title")
    recipe = body.get("recipe")
    if not drink:
        abort(404)
    try:
        if title:
            drink.title = title
        if recipe:
            drink.recipe = json.dumps(recipe)
        drink.update()
    except BaseException:
        print(sys.exc_info())
        abort(500)
    return jsonify({"success": True, "drinks": [drink.long()]}), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and
    json {"success": True, "delete": id}
     where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)
    try:
        drink.delete()
    except BaseException:
        abort(400)

    return jsonify({"success": True, "delete": id}), 200


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404


@app.errorhandler(500)
def server_processing_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


@app.errorhandler(400)
def server_processing_error(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code

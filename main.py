class RepeateError(Exception):
    pass
    
class NotFound(Exception):
    pass

import uuid
from flask import Flask, Blueprint, request, jsonify, make_response
import os
from flask_cors import CORS
from firebase_admin import firestore, credentials, initialize_app

cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["SECRET_KEY"] = '12345rtfescdvf'
    app.config["CORS_HEADERS"] = "Content-Type"

    app.register_blueprint(userAPI, url_prefix='/user')

    return app


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
db = firestore.client()
state = False
user_rcmd = db.collection('rcmd')

def getDataBase():
    package_img = [doc.to_dict() for doc in user_rcmd.stream()]
    return package_img

rcmd = getDataBase()

async def updateDataBase():
    global rcmd
    package_img = [doc.to_dict() for doc in user_rcmd.stream()]
    for el in package_img:
        user_rcmd.document(el["hex"]).delete()
    for el in rcmd:
        user_rcmd.document(el["hex"]).set(el)


decision1 = [
    {
        "decision": -1,
        "hex": "73bc9b5219754380ba8b272a7396b80c",
        "imgName": "Петуорт (Сассекс), поместье графа Эгремонтского. Росистое утро",
        "userID": "ejs@mail.ru"
    }
]
userAPI = Blueprint('userAPI', __name__)

@userAPI.route('/userID', methods={ 'GET', 'POST', 'OPTIONS' })
def user():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response(), 204
    if request.method == 'GET':
        try:
            package_user = [doc.to_dict() for doc in db.collection('userID').stream()]
            return _corsify_actual_response(jsonify(package_user[0])), 200
        except Exception as e:
            return f"An Error Occured: {e}"
    if request.method == 'POST':
        try:
            id = uuid.uuid4()
            package_user = [doc.to_dict() for doc in db.collection('userID').stream()]
            if(len(package_user) > 0):
                for el in package_user:
                    db.collection('userID').document(el["hex"]).delete()
            request.json.update({"hex": id.hex})
            db.collection('userID').document(id.hex).set(request.json)
            return _corsify_actual_response(jsonify({"success": True})), 200
        except Exception as e:
            return f"An Error Occured: {e}"


@userAPI.route('/state', methods=[ 'GET' ])
def statement():
    global state
    return _corsify_actual_response(jsonify({"state": state})), 200

@userAPI.route('/decision', methods=[ 'GET', 'POST', 'OPTIONS'])
def decision():
    global decision1
    global state
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response(), 204
    if request.method == 'GET':
        #decision = [doc.to_dict() for doc in user_dcsn.stream()]
        state = False
        dec = decision1[0]
        decision1.pop(0)
        return _corsify_actual_response(jsonify(dec)), 200
    if request.method == 'POST':
        try:
            state = True
            decision1.append(request.json)
            return _corsify_actual_response(jsonify({"success": True})), 200
        except RepeateError as e:
            return f"An Error Occured: {e}"
        except Exception as e:
            return f"An Error Occured: {e}"


@userAPI.route('/rcmd', methods=['GET', 'POST', 'OPTIONS', 'DELETE'])
def recommendation():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response(), 204
    if request.method == 'GET':
        try:
            package_img = [doc.to_dict() for doc in user_rcmd.stream()]
            return _corsify_actual_response(jsonify(package_img)), 200
        except Exception as e:
            return f"An Error Occured: {e}"
    if request.method == 'POST':
        try:
            flag = False
            if(len(rcmd) > 0):
                if(request.json["src"] in list(map(lambda el: el["src"], rcmd))):    flag = True
            if(flag):   raise RepeateError("This picture has already exist!")
            id = uuid.uuid4()
            package_img = [doc.to_dict() for doc in user_rcmd.stream()]
            request.json.update({"hex": id.hex})
            user_rcmd.document(id.hex).set(request.json)
            return _corsify_actual_response(jsonify({"success": True})), 200
        except RepeateError as e:
            return f"An Error Occured: {e}"
        except Exception as e:
            return f"An Error Occured: {e}"
    if request.method == 'DELETE':
        try:
            package_img = [doc.to_dict() for doc in user_rcmd.stream()]
            if(len(package_img) > 0):
                for el in package_img:
                    if(el["src"] == request.json["src"]):    user_rcmd.document(el["hex"]).delete()
            return _corsify_actual_response(jsonify({"success": True})), 200
        except Exception as e:
            return f"An Error Occured: {e}"


@userAPI.route('/collection', methods=['GET', 'POST', 'DELETE', 'OPTIONS'], )
def collection():
    global user
    package_user = [doc.to_dict() for doc in db.collection('userID').stream()]
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response(), 204
    if request.method == 'POST':
        try:
            all_images = [doc.to_dict() for doc in db.collection(package_user[0]['userID']).stream()]
            id = uuid.uuid4()
            request.json.update({"hex": id.hex})
            db.collection(package_user[0]['userID']).document(id.hex).set(request.json)
            return _corsify_actual_response(jsonify({"success": True})), 200
        except Exception as e:
            return f"An error occured{e}"
    if request.method == 'GET':
        try:
            all_images = [doc.to_dict() for doc in db.collection(package_user[0]['userID']).stream()]
            return _corsify_actual_response(jsonify(all_images)), 200
        except Exception as e:
            return f"An Error Occured: {e}"
    if request.method == 'DELETE':
        try:
            all_images = [doc.to_dict() for doc in db.collection(package_user[0]['userID']).stream()]
            flag = False
            if(request.json["hex"] in list(map(lambda el: el["hex"], all_images))):    flag = True
            if(not flag):   raise NotFound("Not found!")
            db.collection(package_user[0]['userID']).document(request.json["hex"]).delete()
            return _corsify_actual_response(jsonify({"success": True})), 200
        except NotFound as e:
            return f"An Error Occured: {e}"
            
        except Exception as e:
            return f"An Error Occured: {e}"

def _build_cors_preflight_response():
    response = make_response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Content-Type"] = "*"
    return response

def _corsify_actual_response(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

app = create_app()

if __name__ == '__main__':
    app.run()

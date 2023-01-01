import uuid
from flask import Blueprint, request, jsonify, make_response
from firebase_admin import firestore
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class RepeateError(Exception):
    pass
    
class NotFound(Exception):
    pass

decision1 = [
    {
        "decision": -1,
        "hex": "73bc9b5219754380ba8b272a7396b80c",
        "imgName": "Петуорт (Сассекс), поместье графа Эгремонтского. Росистое утро",
        "userID": "ejs@mail.ru"
    }
]
userAPI = Blueprint('userAPI', __name__)

@userAPI.route('/state', methods=[ 'GET' ])
def statement():
    global state
    print(state)
    return _corsify_actual_response(jsonify({"state": state})), 200

@userAPI.route('/decision', methods=[ 'GET', 'POST', 'OPTIONS'])
def decision():
    global decision1
    global state

    if request.method == 'OPTIONS':
        return _build_cors_preflight_response(), 204
    if request.method == 'GET':
        state = False
        dec = decision1[0]
        decision1.pop(0)
        return _corsify_actual_response(jsonify(dec)), 200
    if request.method == 'POST':
        try:
            package_img = [doc.to_dict() for doc in user_rcmd.stream()]
            if(len(package_img) > 0):
                for el in package_img:
                    if(el["title"] == request.json["imgName"]):    user_rcmd.document(el["hex"]).delete()
            state = True
            decision1.append(request.json)
            return _corsify_actual_response(jsonify({"success": True})), 200
        except RepeateError as e:
            return f"An Error Occured: {e}"
        except Exception as e:
            return f"An Error Occured: {e}"


@userAPI.route('/rcmd', methods=['GET', 'POST', 'OPTIONS'])
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

            package_img = [doc.to_dict() for doc in user_rcmd.stream()]

            flag = False
            if(len(package_img) > 0):
                if(request.json["src"] in list(map(lambda el: el["src"], package_img))):    flag = True
            if(flag):   raise RepeateError("This picture has already exist!")
            id = uuid.uuid4()
            # user_rcmd.document(package_img[0]["hex"]).delete()
            request.json.update({"hex": id.hex})
            package_img.append(request.json)
            user_rcmd.document(id.hex).set(request.json)
            return _corsify_actual_response(jsonify({"success": True})), 200
        except RepeateError as e:
            return f"An Error Occured: {e}"
        except Exception as e:
            return f"An Error Occured: {e}"


@userAPI.route('/collection', methods=['GET', 'POST', 'DELETE', 'OPTIONS'], )
def collection():
    global user
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response(), 204
    if request.method == 'POST':
        try:
            all_images = [doc.to_dict() for doc in user_Ref.stream()]
            flag = False
            if(len(all_images) > 0):
                if(request.json["src"] in list(map(lambda el: el["src"], all_images))):   raise RepeateError("This picture has already exist!")
            id = uuid.uuid4()
            request.json.update({"hex": id.hex})
            user_Ref.document(id.hex).set(request.json)
            return _corsify_actual_response(jsonify({"success": True})), 200
        except RepeateError as e:
            return _corsify_actual_response(jsonify({"success": False})), 200
        except Exception as e:
            return f"An error occured{e}"
    if request.method == 'GET':
        try:
            all_images = [doc.to_dict() for doc in user_Ref.stream()]
            return _corsify_actual_response(jsonify(all_images)), 200
        except Exception as e:
            return f"An Error Occured: {e}"
    if request.method == 'DELETE':
        try:
            all_images = [doc.to_dict() for doc in user_Ref.stream()]
            flag = False
            if(request.json["hex"] in list(map(lambda el: el["hex"], all_images))):    flag = True
            if(not flag):   raise NotFound("Not found!")
            user_Ref.document(request.json["hex"]).delete()
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


import flask
from flask import jsonify, make_response, request
from . import db_session
from .user import User


SECRET_KEY = "EL_PSY_KONGROO"


blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users', methods=["GET"])
def get_users():
    auth_header = request.headers.get("Authorization")
    if auth_header == f"Bearer {SECRET_KEY}":
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        if not users:
            return make_response(jsonify({'error': 'Not found'}), 404)
        return jsonify(
            {
                'users':
                    [item.to_dict() for item in users]
            }
        )
    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)


@blueprint.route('/api/users/<int:user_id>', methods=["GET"])
def get_user(user_id):
    auth_header = request.headers.get("Authorization")
    if auth_header == f"Bearer {SECRET_KEY}":
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        if not user:
            return make_response(jsonify({'error': 'Not found'}), 404)
        return jsonify({
            'user': user.to_dict()
        })
    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    auth_header = request.headers.get("Authorization")
    if auth_header == f"Bearer {SECRET_KEY}":
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        if not user:
            return make_response(jsonify({'error': 'Not found'}), 404)
        db_sess.delete(user)
        db_sess.commit()
        return make_response(jsonify({'success': 'OK'}))
    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)


@blueprint.route('/api/users/', methods=['POST'])
def add_user(user_id):
    auth_header = request.headers.get("Authorization")
    if auth_header == f"Bearer {SECRET_KEY}":
        db_sess = db_session.create_session()
        if not all(key in request.json for key in ['username', 'email']):
            return make_response(jsonify({'error': 'Bad request'}), 400)
        if all(key in['username', 'rating', 'email', 'phone_number', 'password'] for key in request.json):
            user = User()
            for key in request.json:
                match key:
                    case "username":
                        user.username = request.json["username"]
                    case "rating":
                        user.rating = request.json["rating"]
                    case "email":
                        user.email = request.json["email"]
                    case "phone_number":
                        user.phone_number = request.json["phone_number"]
                    case "password":
                        user.password = request.json["password"]
            db_sess.add(user)
            db_sess.commit()
            return make_response(jsonify({"success": "OK"}), 200)
        else:
            return make_response(jsonify({'error': 'Bad request'}, 400))
    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)


@blueprint.route('/api/users/<int:user_id>', methods=["PUT"])
def change_user(user_id):
    auth_header = request.headers.get("Authorization")
    if auth_header == f"Bearer {SECRET_KEY}":
        db_sess = db_session.create_session()
        if all(key in ['username', 'rating', 'email', 'phone_number', 'password'] for key in request.json):
            user = db_sess.query(User).get(user_id)
            for key in request.json:
                match key:
                    case "username":
                        user.username = request.json["username"]
                    case "rating":
                        user.rating = request.json["rating"]
                    case "email":
                        user.email = request.json["email"]
                    case "phone_number":
                        user.phone_number = request.json["phone_number"]
                    case "password":
                        user.password = request.json["password"]
            db_sess.commit()
            return make_response(jsonify({"success": "OK"}), 200)
    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)
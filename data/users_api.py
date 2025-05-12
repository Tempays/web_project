import flask
from flask import jsonify, make_response, request
from . import db_session
from .user import User
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}


SECRET_KEY = "EL_PSY_KONGROO"


blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


def allowed(filename):
    if '.' in filename:
        if filename.rsplit('.')[-1].lower() in ALLOWED_EXTENSIONS:
            return True
    return False


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
def add_user():
    auth_header = request.headers.get("Authorization")
    if auth_header == f"Bearer {SECRET_KEY}":
        db_sess = db_session.create_session()
        required_fields = ['username', 'email', 'password']
        if not all(key in request.json for key in required_fields):
            return make_response(jsonify({'error': 'Missing required fields'}), 400)
        user = User(
            username = request.json["username"],
            email = request.json["email"]
        )
        for key in request.json:
            match key:
                case "rating":
                    user.rating = request.json["rating"]
                case "phone_number":
                    user.phone_number = request.json["phone_number"]
                case "password":
                    user.set_password(request.json["password"])
        db_sess.add(user)
        db_sess.commit()
        return make_response(jsonify({"success": "OK"}), 200)
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
                        user.set_password(request.json["password"])
            db_sess.commit()
            return make_response(jsonify({"success": "OK"}), 200)
    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)


@blueprint.route('/api/set_profile_picture/<int:user_id>', methods=["POST"])
def set_user_picture(user_id):
    auth_header = request.headers.get("Authorization")
    if auth_header == f"Bearer {SECRET_KEY}":
        if "file" not in request.files:
            return make_response(jsonify({"error": "empty"}), 400)
        file = request.files["file"]
        if file.filename == "":
            return make_response(jsonify({"error": "File is not chosen"}), 400)
        if not allowed(file.filename):
            return make_response(jsonify({"error": "Wrong extension"}), 400)
        file_path = f'static/images/users/{user_id}.jpg'
        with open(file_path, 'wb') as new_file:
            new_file.write(file.read())
        return make_response(jsonify({"success": "OK", "path": file_path}), 200)

    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)
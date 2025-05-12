import flask
from flask import jsonify, make_response, request
from . import db_session
from .accommodation import Accommodation
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

SECRET_KEY = "EL_PSY_KONGROO"


blueprint = flask.Blueprint(
    'accommodation_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/accommodations', methods=["GET"])
def get_accommodations():
    auth_header = request.headers.get("Authorization")
    if auth_header == f"Bearer {SECRET_KEY}":
        db_sess = db_session.create_session()
        accommodations = db_sess.query(Accommodation).all()
        if not accommodations:
            return make_response(jsonify({"error": "Not Found"}), 404)
        return jsonify({
                'accommodations': [item.to_dict() for item in accommodations]
            })
    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)


@blueprint.route('/api/accommodations/<int:accommodation_id>', methods=["GET"])
def get_accommodation(accommodation_id):
    auth_header = request.headers.get("Authorization")
    if auth_header == f"Bearer {SECRET_KEY}":
        db_sess = db_session.create_session()
        accommodation = db_sess.query(Accommodation).where(Accommodation.id == accommodation_id).first()
        if not accommodation:
            return make_response(jsonify({"error": "Not found"}), 404)
        return jsonify({'accommodation': accommodation.to_dict()})
    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)


@blueprint.route('/api/accommodations', methods=['POST'])
def add_accommodation():
    auth_header = request.headers.get("Authorization")
    if auth_header == f'Bearer {SECRET_KEY}':
        db_sess = db_session.create_session()
        required_fields = ['name', 'cost', 'accommodation_owner', 'address']
        if not all(key in request.json for key in required_fields):
            return make_response(jsonify({'error': 'Missing compulsory fields'}), 400)
        accommodation = Accommodation(
            name = request.json["name"],
            cost = request.json["cost"],
            accommodation_owner = request.json["accommodation_owner"],
            address = request.json["address"]
        )
        for key in request.json:
            if key == 'description':
                accommodation.description = request.json["description"]
        db_sess.add(accommodation)
        db_sess.commit()
        return make_response(jsonify({'success': 'ok'}), 200)
    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)


@blueprint.route('/api/accommodations/<int:accommodation_id>', methods=['PUT'])
def change_accommodation(accommodation_id):
    auth_header = request.headers.get("Authorization")
    if auth_header == f'Bearer {SECRET_KEY}':
        db_sess = db_session.create_session()
        accommodation = db_sess.query(Accommodation).where(accommodation_id == Accommodation.id).first()
        if not accommodation:
            return make_response(jsonify({'error': 'Not found'}), 404)
        for key in request.json:
            match key:
                case "name":
                    accommodation.name = request.json["name"]
                case "cost":
                    accommodation.cost = request.json["cost"]
                case "description":
                    accommodation.description = request.json["description"]
                case "address":
                    accommodation.address = request.json["address"]
                case "accommodation_owner":
                    accommodation.accommodation_owner = request.json["accommodation_owner"]
                case "rating":
                    accommodation.rating = request.json["rating"]
        return make_response(jsonify({'success': 'OK'}), 200)
    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)


@blueprint.route('/api/accommodations/<int:accommodation_id>', methods=['DELETE'])
def delete_accommodation(accommodation_id):
    auth_header = request.headers.get('Authorization')
    if auth_header == f'Bearer {SECRET_KEY}':
        db_sess = db_session.create_session()
        accommodation = db_sess.query(Accommodation).where(accommodation_id == Accommodation.id).first()
        if not accommodation:
            return make_response(jsonify({'error': 'Not found'}), 404)
        db_sess.delete(accommodation)
        db_sess.commit()
        return make_response(jsonify({'success': 'OK'}))
    else:
        return make_response(jsonify({'error': 'Forbidden'}), 403)
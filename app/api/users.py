from app.api import bp
from app.main.models import (
    load_user, User
)
from app.api.errors import (
    not_found,
    bad_request
)
from app import db
from flask import jsonify, request, g, abort
from app.api.auth import token_auth

@bp.route('/users/<int:user_id>', methods=["GET"])
@token_auth.login_required
def api_get_user(user_id):
    user = load_user(user_id)
    if not user:
        return not_found()

    return jsonify(user._asdict())

@bp.route('/users/', methods=["GET"])
@token_auth.login_required
def api_get_users():
    users = User.query.all()
    if not users:
        response = {}
    else:
        response = jsonify([user._asdict() for user in users])

    return response

@bp.route('/users/<int:user_id>/followers', methods=["GET"])
@token_auth.login_required
def api_get_user_followers(user_id):
    pass

@bp.route('/users/<int:user_id>/followed', methods=["GET"])
@token_auth.login_required
def api_get_user_followed(user_id):
    user = User.query.get(user_id)

    if not user:
        return not_found()
    
    return jsonify([user._asdict() for user in user.followed])

@bp.route('/users', methods=["POST"])
@token_auth.login_required
def api_create_user():
    body = request.json

    if 'first_name' not in body:
        return bad_request('Missing first_name')

    if 'last_name' not in body:
        return bad_request('Missing last_name')
    
    if 'email' not in body:
        return bad_request('Missing email')

    if 'password' not in body:
        return bad_request('Missing password')
        
    user = User(
        first_name = body['first_name'],
        last_name = body['last_name'],
        email = body['email'],
    )

    user.set_password(body['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify(user._asdict())

@bp.route('/users/<int:user_id>', methods=["PUT"])
@token_auth.login_required
def api_update_user(user_id):
    
    body = request.json
    user = User.query.get(user_id)

    if not user:
        return not_found()
    
    if 'first_name' in body:
        user.first_name = body['first_name']
    
    if 'last_name' in body:
        user.last_name = body['last_name']

    if 'email' in body:
        user.email = body['email']

    if 'about_me' in body:
        user.about_me = body['about_me']

    db.session.add(user)
    db.session.commit()

    return jsonify(user._asdict())


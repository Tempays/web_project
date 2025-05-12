import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Accommodation(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Accommodation'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    cost = sqlalchemy.Column(sqlalchemy.Integer)
    description = sqlalchemy.Column(sqlalchemy.String)
    photo_path = sqlalchemy.Column(sqlalchemy.String, default='')
    address = sqlalchemy.Column(sqlalchemy.String, default='')
    accommodation_owner = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('User.id'))
    rating = sqlalchemy.Column(sqlalchemy.String, default='')
    owner = orm.relationship('User')
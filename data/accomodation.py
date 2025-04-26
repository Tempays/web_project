import datetime

import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class Accomodation(SqlAlchemyBase):

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    cost = sqlalchemy.Column(sqlalchemy.Integer)
    description = sqlalchemy.Column(sqlalchemy.String)
    photo_path = sqlalchemy.Column(sqlalchemy.String)
    accomodation_owner = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('User.id'))
    owner = orm.relationship('User')

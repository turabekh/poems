from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    poems = db.relationship('Poem', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)    


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False) 
    poems = db.relationship('Poem', backref='author', lazy='dynamic')


    def __repr__(self):
        return f"<Category>: {self.name}"

class Poem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))

    def __repr__(self):
        return '<Poem {}>'.format(self.body)

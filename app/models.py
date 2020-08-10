from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask_login import UserMixin, current_user
from app import login
from hashlib import md5
from time import time
import jwt
from flask import current_app
from app.search import add_to_index, remove_from_index, query_index

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(SearchableMixin, UserMixin, db.Model):
    __searchable__ = ["username",]
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    image_file = db.Column(db.String(120), nullable=True, default="default.jpg")
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    is_admin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    poems = db.relationship('Poem', backref='author', lazy='dynamic')
    sent_messages = db.relationship('Message', backref='sent_user', lazy=True, foreign_keys='Message.sent_user_id')
    received_messages = db.relationship('Message', backref='received_user', lazy=True, foreign_keys='Message.received_user_id')
    comments = db.relationship("Comment", backref="author", lazy="dynamic")

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    
    def followed_poems(self):
        followed = Poem.query.join(
            followers, (followers.c.followed_id == Poem.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Poem.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Poem.timestamp.desc())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
    def new_inbox_messages(self):
        return len([m for m in self.received_messages if m.is_read == False])

    def __repr__(self):
        return '<User {}>'.format(self.username)    


class Category(SearchableMixin, db.Model):
    __searchable__ = ["name",]
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False) 
    poems = db.relationship('Poem', backref='category', lazy='dynamic')


    def __repr__(self):
        return f"<Category>: {self.name}"


user_likes = db.Table('user_likes',
    db.Column('poem_id', db.Integer, db.ForeignKey('poem.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Poem(SearchableMixin, db.Model):
    __searchable__ = ["body",]
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(140))
    audio = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    comments = db.relationship("Comment", backref="poem", lazy="dynamic")

    liked = db.relationship(
        'User', secondary = lambda: user_likes, backref="likes")
    
    def already_liked(self, user):
        return user in self.liked
    
    def like(self, user):
        if not self.already_liked(user):
            self.liked.append(user) 
            db.session.commit()
        
    def unlike(self, user):
        if self.already_liked(user):
            self.liked.remove(user) 
            db.session.commit()

    def get_liked_users(self):
        return [u.username for u in self.liked]

    def get_comments(self):
        return self.comments.order_by(Comment.path).all()
    
    def get_short_user_likes(self):
        r = self.get_liked_users()[:2] or []
        if current_user.is_authenticated:
            r = [n for n in self.get_liked_users() if n != current_user.username][:2]
        if len(self.get_liked_users()) > 2:
            r.append(f" and {len(self.get_liked_users()) -2 } others" )
        if current_user in self.liked:
            if len(r) == 1:
                r = ["You"] + r
            elif not r:
                r= ["You"]
            else:
                r[0] = "You"
        return ", ".join(r)

    def __repr__(self):
        return '<Poem {}>'.format(self.id)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    is_read = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    received_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Message>: {self.id}"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Comment(db.Model):
    _N = 6

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    poem_id = db.Column(db.Integer, db.ForeignKey("poem.id"))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    path = db.Column(db.Text, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship(
        'Comment', backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic')

    def save(self):
        db.session.add(self)
        db.session.commit()
        prefix = self.parent.path + '.' if self.parent else ''
        self.path = prefix + '{:0{}d}'.format(self.id, self._N)
        db.session.commit()

    def level(self):
        return len(self.path) // self._N - 1
    
    def get_replies(self):
        return self.replies.all()
    
    def color(self):
        return "green" if self.level() % 2 == 0 else "blue" 
    def margin(self):
        return self.level() * 10
    def width(self):
        return 100 - (self.level() * 10)

    def comment_formatted(self):
        return {
            "id": self.id,
            "body": self.body, 
            "author": self.author.username,
            "parent_id": self.parent.id if self.parent else None,
            "level": self.level(),
            "color": self.color(),
            "width": self.width(),
            "margin": self.margin(),
            "replies_count": len(self.get_replies()),
            "poem_id": self.poem.id,
            "created_at": self.timestamp, 
            "parent_author": self.parent.author.username if self.parent else None,
            "can_delete": False
        }
    @classmethod
    def get_comments_formatted(cls):
        return [c.comment_formatted() for c in cls.query.all()]
    
    @classmethod
    def get_poem_comments_formatted(cls, poem_id):
        return [c.comment_formatted() for c in cls.query.filter(cls.poem_id==poem_id).order_by(cls.path).all()]
    
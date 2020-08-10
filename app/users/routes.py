import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, current_app
from app import db
from app.users import bp
from app.users.forms import EditProfileForm, EmptyForm, MessageForm
from app.main.forms import CommentForm
from flask_login import current_user, login_required
from app.models import User, Poem, Category, Message


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    print(f"Saving Image Here {picture_path}")
    return picture_fn


@bp.route('/user/<username>', methods=["GET", "POST"])
@login_required
def user(username):
    comment_form = CommentForm()
    user = User.query.filter_by(username=username).first_or_404()
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    poems = user.poems.all()
    form = EmptyForm()
    return render_template('users/user.html', user=user, poems=poems, image_file=image_file, form=form, comment_form=comment_form)


@bp.route('/<username>/update', methods=['GET', 'POST'])
@login_required
def update_account(username):
    form = EditProfileForm()
    user = User.query.filter_by(username=username).first_or_404()
    if user != current_user:
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.update_account', username=current_user.username))
    elif request.method == 'GET':
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template('users/update_account.html', form=form, image_file=image_file, user=user) 



@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username), "danger")
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!', "danger")
            return redirect(url_for('users.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username), "success")
        return redirect(url_for('users.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username), "danger")
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!', "danger")
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username), "success")
        return redirect(url_for('users.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route("/<username>/inbox")
def inbox(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        messages = current_user.received_messages
        return render_template("users/inbox.html", messages = messages)
    return redirect(url_for("main.index"))


@bp.route("/<username>/outbox")
def outbox(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        messages = current_user.sent_messages
        return render_template("users/outbox.html", messages = messages)
    return redirect(url_for("main.index"))

@bp.route("/<username>/message", methods=["GET", "POST"])
def send_message(username):
    user = User.query.filter_by(username=username).first()
    users = [(u.id, u.username) for u in user.followed.union(user.followers).all()]
    if user != current_user:
        return redirect(url_for("main.index"))
    form = MessageForm()
    form.user.choices = users
    if form.validate_on_submit():
        sent_user_id = current_user.id 
        received_user_id = form.user.data 
        subject = form.subject.data 
        content = form.content.data 
        message = Message(body=content, sent_user_id=sent_user_id, received_user_id=received_user_id)
        db.session.add(message)
        db.session.commit()
        flash(f"Your message has been sent", "success")
        return redirect(url_for("users.outbox", username=current_user.username))
    else:
        return render_template("users/send_message.html", form=form)


@bp.route("/users/search")
def search():
    form = EmptyForm()
    q = request.args.get("user-search", None) 
    if q is None or (q == ""):
        return redirect(url_for("users.user_list"))
    page = request.args.get('page', 1, type=int)
    users, total = User.search(q, page,
                               current_app.config['USERS_PER_PAGE'])
    next_url = url_for('users.search', q=q, page=page + 1) \
        if total > page * current_app.config['USERS_PER_PAGE'] else None
    prev_url = url_for('users.search', q=q, page=page - 1) \
        if page > 1 else None
    return render_template('users/user_list.html', users=sorted(users.all(), key=lambda u: u.username),
                           next_url=next_url, prev_url=prev_url, form=form)
@bp.route("/users")
def user_list():
    form = EmptyForm()
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.username).paginate(page, current_app.config["USERS_PER_PAGE"], False)
    next_url = url_for('users.user_list', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('users.user_list', page=users.prev_num) \
        if users.has_prev else None
    return render_template('users/user_list.html', users=users.items, next_url=next_url,
                        prev_url=prev_url, form=form)

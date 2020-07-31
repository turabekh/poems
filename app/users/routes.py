import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, current_app
from app import db
from app.users import bp
from app.users.forms import EditProfileForm, EmptyForm
from flask_login import current_user, login_required
from app.models import User, Poem, Category


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    print(f"Saving Image Here {picture_path}")
    return picture_fn


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    image_file = None
    if user.image_file:
        image_file = url_for('static', filename='profile_pics/' + user.image_file)
    
    if user == current_user:
        return render_template("users/dashboard.html")
    poems = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    
    form = EmptyForm()
    return render_template('users/user.html', user=user, poems=poems, image_file=image_file, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template('users/edit_profile.html', form=form) 



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

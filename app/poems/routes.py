from flask import render_template, flash, redirect, url_for, jsonify, request
from app import db
from app.poems import bp
from app.poems.forms import PoemForm, CategoryForm
from app.main.forms import CommentForm
from flask_login import current_user, login_required
from app.models import User, Poem, Category



@bp.route("/poem", methods=["GET", "POST"])
def create_poem():
    categories = [(c.id, c.name) for c in Category.query.all()]
    form = PoemForm()
    form.category.choices = categories
    if form.validate_on_submit():
        poem = Poem(title=form.title.data, body=form.body.data, author=current_user, category_id=form.category.data)
        db.session.add(poem)
        db.session.commit()
        flash('Your poem is now live!', "success")
        return redirect(url_for('poems.create_poem'))
    return render_template("poems/create_poem.html", form=form, title="Create")


@bp.route("/<int:id>", methods=["GET", "POST"])
def update_poem(id):
    categories = [(c.id, c.name) for c in Category.query.all()]
    form = PoemForm()
    form.category.choices = categories
    poem = Poem.query.filter_by(id=id).first_or_404()
    if poem.author != current_user:
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        poem.title = form.title.data
        poem.body = form.body.data 
        poem.category_id = form.category.data
        db.session.commit()
        flash('Your poem is updated!', "success")
        return redirect(url_for('poems.update_poem', id=poem.id))
    else:
        form.title.data = poem.title
        form.body.data = poem.body
        form.category.data = poem.category
    return render_template("poems/create_poem.html", form=form, title="Update")

@bp.route("/<username>", methods=["GET", "POST"])
def poem_list(username):
    comment_form = CommentForm()
    user = User.query.filter_by(username=username).first_or_404()
    if user != current_user:
        return redirect(url_for("main.index"))
    return render_template("poems/poem_list.html", poems=user.poems.all(), user=user, comment_form=comment_form)

@bp.route("/poems/delete/<int:id>", methods=["GET", "POST"])
def delete_poem(id):
    poem = Poem.query.filter_by(id=id).first_or_404()
    if poem.author != current_user:
        return redirect(url_for("main.index"))
    db.session.delete(poem)
    db.session.commit() 
    return redirect(url_for("poems.poem_list", username=poem.author.username))


@bp.route("/like/<int:id>/<int:user_id>", methods=["GET"])
def like(id, user_id):
    poem = Poem.query.filter_by(id=id).first_or_404()
    user = User.query.filter_by(id=user_id).first_or_404()
    poem.like(user)
    print(poem.get_liked_users())
    return jsonify({"id": id, "user_likes": poem.get_short_user_likes()})

@bp.route("/unlike/<int:id>/<int:user_id>", methods=["GET"])
def unlike(id, user_id):
    print(request)
    print("ID: ", id)
    print("I am here")
    poem = Poem.query.filter_by(id=id).first_or_404()
    user = User.query.filter_by(id=user_id).first_or_404()
    poem.unlike(user)
    return jsonify({"id": id, "user_likes": poem.get_short_user_likes()})

@bp.route("/category", methods=["GET", "POST"])
def create_category():
    if not current_user.is_admin:
        return redirect(url_for("main.index"))
    form = CategoryForm()
    if form.validate_on_submit():
        name = Category.query.filter_by(name=form.name.data).first()
        if name is not None:
            flash(f"{form.name.data} has already existed. Please enter a different name", "danger")
            return redirect(url_for(".create_category"))
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Your category is successfully added!', "success")
        return redirect(url_for('poems.create_category'))
    return render_template("poems/create_category.html", form=form, title="Create")

@bp.route("/categories")
def category_list():
    return render_template("poems/category_list.html", categories=Category.query.all())

@bp.route("/categories/<int:id>", methods=["GET", "POST"])
def update_category(id):
    category = Category.query.filter_by(id=id).first_or_404()
    form = CategoryForm()
    if form.validate_on_submit():
        name = Category.query.filter_by(name=form.name.data).first()
        if name != category:
            flash(f"{form.name.data} - already exists. Please enter a different name", "danger")
            return redirect(url_for(".category_list"))
        category.name = form.name.data 
        db.session.commit()
        flash("Category updated successfully!", "success")
        return redirect(url_for("poems.category_list"))
    else:
        form.name.data = category.name
    return render_template("poems/create_category.html", form=form, title="Update")

@bp.route("/categories/delete/<int:id>", methods=["GET", "POST"])
def delete_category(id):
    category = Category.query.filter_by(id=id).first_or_404()
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for("poems.category_list"))
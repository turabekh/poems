from flask import render_template, flash, redirect, url_for
from app import db
from app.poems import bp
from app.poems.forms import PoemForm, CategoryForm
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


@bp.route("/poems/<int:id>", methods=["GET", "POST"])
def update_poem(id):
    categories = [(c.id, c.name) for c in Category.query.all()]
    form = PoemForm()
    form.category.choices = categories
    poem = Poem.query.filter_by(id=id).first_or_404()
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

@bp.route("/poems")
def poem_list():
    return render_template("poems/poem_list.html", poems=Poem.query.all())

@bp.route("/poems/delete/<int:id>", methods=["GET", "POST"])
def delete_poem(id):
    poem = Poem.query.filter_by(id=id).first_or_404() 
    db.session.delete(poem)
    db.session.commit() 
    return redirect(url_for("poems.poem_list"))


@bp.route("/category", methods=["GET", "POST"])
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
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
    category = Category.query.filter_by(id=id).first()
    form = CategoryForm()
    if form.validate_on_submit():
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
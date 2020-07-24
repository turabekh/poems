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
        poem = Poem(body=form.poem.data, author=current_user, category_id=form.category.data)
        db.session.add(poem)
        db.session.commit()
        flash('Your poem is now live!', "success")
        return redirect(url_for('poems.create_poem'))
    return render_template("poems/create_poem.html", form=form)


@bp.route("/category", methods=["GET", "POST"])
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Your category is successfully added!', "success")
        return redirect(url_for('poems.create_category'))
    return render_template("poems/create_category.html", form=form)




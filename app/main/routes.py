from datetime import datetime
from flask import render_template, redirect, url_for, request, current_app, g, flash, jsonify
from flask_login import current_user
from app import db
from app.models import User, Poem, Category, Comment
from app.main import bp
from .forms import ContactUsForm, CommentForm
from app.auth.email import send_message_to_admins



@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        

@bp.route('/', methods=["GET", "POST"])
def index():
    comment_form = CommentForm()
       
        
    page = request.args.get('page', 1, type=int)
    poems = Poem.query.order_by(Poem.created_at.desc()).paginate(page, current_app.config["POEMS_PER_PAGE"], False)
    next_url = url_for('main.index', page=poems.next_num) \
        if poems.has_next else None
    prev_url = url_for('main.index', page=poems.prev_num) \
        if poems.has_prev else None
    return render_template('main/index.html', poems=poems.items, next_url=next_url,
                           prev_url=prev_url, comment_form=comment_form)


@bp.route('/search')
def search():
    comment_form = CommentForm()
    q = request.args.get("q", None)
    if q is None or (q == ""):
        return redirect(url_for("main.index"))
    page = request.args.get('page', 1, type=int)
    poems, total = Poem.search(q, page,
                               current_app.config['POEMS_PER_PAGE'])
    next_url = url_for('main.search', q=q, page=page + 1) \
        if total > page * current_app.config['POEMS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=q, page=page - 1) \
        if page > 1 else None
    return render_template('main/index.html', poems=poems.all(),
                           next_url=next_url, prev_url=prev_url, comment_form=comment_form)


@bp.route("/about")
def about():
    return render_template("main/about.html")

@bp.route("/contact/us", methods=["GET", "POST"])
def contact_us():
    form = ContactUsForm()
    if current_user.is_authenticated:
        form.name.data = current_user.username
        form.email.data = current_user.email
    if form.validate_on_submit():
        send_message_to_admins(form)
        flash("Your message has been sent, Admins will follow your request", "success")
        return redirect(url_for("main.index"))
    return render_template("main/contact_us.html", form=form)


@bp.route("/comment/<int:poem_id>", methods=["POST"])
def comment(poem_id):
    form = CommentForm() 
    if form.validate_on_submit():
        request_body = request.get_json()
        body = request_body.get("body", None)
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        parent_id = request_body.get("parent_id", None)
        if body is None:
            return jsonify({"success": False}), 404
        comment = Comment(body=body, user_id=current_user.id, poem_id=poem_id, parent_id=parent_id)
        comment.save()
        comments = Comment.get_poem_comments_formatted(poem_id)
        form.body.data = ""
        can_delete = None
        if comment.poem.author == current_user:
            can_delete = True
        return jsonify({"success": True, "comments": comments, "poem_id": poem_id, "can_delete": can_delete})
    else:
        return redirect(url_for("main.index"))


@bp.route("/delete/<int:poem_id>/<int:comment_id>", methods=["GET"])
def delete(poem_id, comment_id):
    poem = Poem.query.filter_by(id=poem_id).first_or_404()
    comment = Comment.query.filter_by(id=comment_id).first_or_404() 
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    db.session.delete(comment)
    db.session.commit()
    comments = Comment.get_poem_comments_formatted(poem_id)
    can_delete = None
    if poem.author == current_user:
        can_delete = True
    return jsonify({"success": True, "comments": comments, "poem_id": poem_id, "can_delete": can_delete})
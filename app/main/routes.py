from datetime import datetime
from flask import render_template, redirect, url_for, request, current_app, g, flash
from flask_login import current_user
from app import db
from app.models import User, Poem, Category
from app.main import bp
from .forms import ContactUsForm
from app.auth.email import send_message_to_admins



@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        

@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    poems = Poem.query.order_by(Poem.created_at.desc()).paginate(page, current_app.config["POEMS_PER_PAGE"], False)
    next_url = url_for('main.index', page=poems.next_num) \
        if poems.has_next else None
    prev_url = url_for('main.index', page=poems.prev_num) \
        if poems.has_prev else None
    return render_template('main/index.html', poems=poems.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/search')
def search():
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
                           next_url=next_url, prev_url=prev_url)


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
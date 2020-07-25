from datetime import datetime
from flask import render_template, redirect, url_for, request, current_app, g
from flask_login import current_user
from app import db
from app.models import User, Poem, Category
from app.main import bp
from app.main.forms import SearchForm


@bp.before_request
def before_request():
    g.search_form = SearchForm()
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        

@bp.route('/')
@bp.route('/index')
def index():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    poems = Poem.query.order_by(Poem.created_at.desc()).paginate(page, current_app.config["POEMS_PER_PAGE"], False)
    next_url = url_for('main.index', page=poems.next_num) \
        if poems.has_next else None
    prev_url = url_for('main.index', page=poems.prev_num) \
        if poems.has_prev else None
    return render_template('main/index.html', poems=poems.items, next_url=next_url,
                           prev_url=prev_url, form=form)


@bp.route('/search')
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    poems, total = Poem.search(g.search_form.q.data, page,
                               current_app.config['POEMS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POEMS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('main/search.html', poems=poems,
                           next_url=next_url, prev_url=prev_url)
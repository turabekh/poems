from flask import render_template, redirect, url_for, request, current_app
from app import db
from app.models import User, Poem, Category
from app.main import bp

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

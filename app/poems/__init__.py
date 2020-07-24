from flask import Blueprint

bp = Blueprint('poems', __name__)

from app.poems import routes
"""
首页路由
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.memo import Memo

index_bp = Blueprint('index', __name__)


@index_bp.route('/')
def index():
    """首页"""
    return render_template('index.html', Memo=Memo)

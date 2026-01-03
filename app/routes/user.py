"""
用户信息相关路由
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile')
@login_required
def profile():
    """用户信息展示页面（只读）"""
    return render_template('user/profile.html', user=current_user)

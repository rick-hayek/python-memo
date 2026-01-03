"""
认证相关路由
"""
from flask import Blueprint, redirect, url_for, session, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import gettext as _
from app.services.oauth_service import get_github_oauth, get_github_user_info
from app.services.auth_service import get_or_create_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login():
    """登录页面"""
    # 如果已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    return redirect(url_for('auth.github_login'))


@auth_bp.route('/login/github')
def github_login():
    """GitHub OAuth登录"""
    github = get_github_oauth()
    redirect_uri = url_for('auth.github_callback', _external=True)
    return github.authorize_redirect(redirect_uri)


@auth_bp.route('/github/callback')
def github_callback():
    """GitHub OAuth回调"""
    github = get_github_oauth()
    
    try:
        # 获取访问令牌
        token = github.authorize_access_token()
        access_token = token.get('access_token')
        
        if not access_token:
            flash(_('OAuth authentication failed: Access token not obtained'), 'error')
            return redirect(url_for('auth.login'))
        
        # 获取用户信息
        user_info = get_github_user_info(access_token)
        
        # 获取或创建用户
        user = get_or_create_user(
            oauth_provider=user_info['oauth_provider'],
            oauth_user_id=user_info['oauth_user_id'],
            user_info=user_info
        )
        
        # 登录用户
        login_user(user, remember=True)
        flash(_('Welcome, %(username)s!', username=user.username), 'success')
        
        # 重定向到首页
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('index.index'))
        
    except Exception as e:
        flash(_('OAuth authentication failed: %(error)s', error=str(e)), 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    flash(_('You have successfully logged out'), 'info')
    return redirect(url_for('index.index'))

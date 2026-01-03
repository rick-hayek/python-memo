"""
认证业务逻辑
"""
from app import db
from app.models.user import User
from datetime import datetime


def get_or_create_user(oauth_provider, oauth_user_id, user_info):
    """
    获取或创建用户
    
    Args:
        oauth_provider: OAuth提供商（如'github'）
        oauth_user_id: OAuth平台返回的用户ID
        user_info: 用户信息字典，包含username, email, avatar_url等
    
    Returns:
        User对象
    """
    # 查找用户
    user = User.query.filter_by(
        oauth_provider=oauth_provider,
        oauth_user_id=oauth_user_id
    ).first()
    
    if user:
        # 用户已存在，更新信息（可选，保持信息最新）
        user.username = user_info.get('username') or user.username
        user.email = user_info.get('email') or user.email
        user.avatar_url = user_info.get('avatar_url') or user.avatar_url
        user.updated_at = datetime.utcnow()
    else:
        # 创建新用户
        user = User(
            oauth_provider=oauth_provider,
            oauth_user_id=oauth_user_id,
            username=user_info.get('username'),
            email=user_info.get('email'),
            avatar_url=user_info.get('avatar_url')
        )
        db.session.add(user)
    
    db.session.commit()
    return user


def get_user_by_id(user_id):
    """根据ID获取用户"""
    return User.query.get(user_id)

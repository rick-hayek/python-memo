"""
用户模型
"""
from flask_login import UserMixin
from datetime import datetime
from app import db


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    oauth_provider = db.Column(db.String(50), nullable=False)  # OAuth提供商（github, google等）
    oauth_user_id = db.Column(db.String(100), nullable=False)  # OAuth平台返回的用户ID
    username = db.Column(db.String(100))  # 用户名（从OAuth获取）
    email = db.Column(db.String(255))  # 邮箱（从OAuth获取）
    avatar_url = db.Column(db.Text)  # 头像URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 唯一约束：同一OAuth提供商的用户ID唯一
    __table_args__ = (
        db.UniqueConstraint('oauth_provider', 'oauth_user_id', name='uq_user_oauth'),
        db.Index('idx_user_oauth', 'oauth_provider', 'oauth_user_id'),
        db.Index('idx_user_email', 'email'),
    )
    
    def __repr__(self):
        return f'<User {self.username} ({self.oauth_provider})>'
    
    def to_dict(self):
        """转换为字典，便于JSON序列化"""
        return {
            'id': self.id,
            'oauth_provider': self.oauth_provider,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

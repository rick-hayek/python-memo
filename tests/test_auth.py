"""
认证模块测试
"""
import pytest
from flask import url_for
from app.models.user import User
from app import db


class TestAuth:
    """认证功能测试"""

    def test_login_redirect(self, client):
        """测试登录重定向"""
        response = client.get('/auth/login')
        assert response.status_code == 302
        assert 'github' in response.headers['Location']

    def test_github_login_redirect(self, client):
        """测试GitHub登录重定向"""
        response = client.get('/auth/login/github')
        assert response.status_code == 302
        assert 'github.com' in response.headers['Location']

    def test_logout_requires_login(self, client):
        """测试登出需要登录"""
        response = client.get('/auth/logout')
        assert response.status_code == 302  # 重定向到登录页

    def test_protected_route_requires_login(self, client):
        """测试受保护路由需要登录"""
        response = client.get('/memo/')
        assert response.status_code == 302
        assert 'auth/login' in response.headers['Location']


class TestUserModel:
    """用户模型测试"""

    def test_user_creation(self, app, test_user):
        """测试用户创建"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            assert user.oauth_provider == 'github'
            assert user.oauth_user_id == '12345'
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'

    def test_user_repr(self, test_user):
        """测试用户字符串表示"""
        assert 'testuser' in str(test_user)
        assert 'github' in str(test_user)

    def test_user_to_dict(self, test_user):
        """测试用户字典转换"""
        user_dict = test_user.to_dict()
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['oauth_provider'] == 'github'

    def test_unique_constraint(self, app):
        """测试唯一约束"""
        with app.app_context():
            # 创建第一个用户
            user1 = User(
                oauth_provider='github',
                oauth_user_id='12345',
                username='user1',
                email='user1@example.com'
            )
            db.session.add(user1)
            db.session.commit()

            # 尝试创建具有相同oauth_provider和oauth_user_id的用户
            user2 = User(
                oauth_provider='github',
                oauth_user_id='12345',  # 相同
                username='user2',
                email='user2@example.com'
            )
            db.session.add(user2)

            # 应该抛出IntegrityError
            with pytest.raises(Exception):  # SQLAlchemy会抛出IntegrityError
                db.session.commit()
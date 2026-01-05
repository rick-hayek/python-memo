"""
测试配置和工具函数
"""
import pytest
from app import create_app, db
from app.models import User, Memo
from flask_login import login_user


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app

        # 清理
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI运行器"""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """创建测试用户"""
    with app.app_context():
        user = User(
            oauth_provider='github',
            oauth_user_id='12345',
            username='testuser',
            email='test@example.com',
            avatar_url='https://github.com/images/error/testuser_happy.gif'
        )
        db.session.add(user)
        db.session.commit()
        # 确保对象在返回前仍然绑定到会话
        db.session.refresh(user)
        return user


@pytest.fixture
def authenticated_client(client, test_user):
    """认证后的测试客户端"""
    with client.application.app_context():
        # 模拟登录 - 设置session
        with client.session_transaction() as sess:
            sess['user_id'] = str(test_user.id)  # Flask-Login期望字符串
            sess['_fresh'] = True
            sess['_user_id'] = str(test_user.id)
            sess['_remember'] = False

        # 在应用上下文中设置用户到login_manager
        with client.application.test_request_context():
            login_user(test_user, remember=False)

    return client


@pytest.fixture
def test_memo(app, test_user):
    """创建测试备忘录"""
    with app.app_context():
        memo = Memo(
            title='Test Memo',
            content='This is a test memo content',
            status='pending',
            user_id=test_user.id
        )
        db.session.add(memo)
        db.session.commit()
        # 确保对象在返回前仍然绑定到会话
        db.session.refresh(memo)
        return memo
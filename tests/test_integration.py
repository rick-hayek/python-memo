"""
集成测试
"""
import pytest
from flask import url_for
from app.models.user import User
from app.models.memo import Memo
from app import db


class TestMemoWorkflowIntegration:
    """备忘录工作流集成测试"""

    def test_complete_memo_workflow(self, client, test_user):
        """测试完整的备忘录工作流"""
        # 1. 用户登录
        with client:
            # 模拟登录
            with client.session_transaction() as sess:
                sess['user_id'] = test_user.id
                sess['_fresh'] = True

            # 2. 创建备忘录
            response = client.post(url_for('memo.create'), data={
                'title': 'Integration Test Memo',
                'content': 'This is a test memo for integration testing',
                'status': 'pending',
                'no_expiry': True
            }, follow_redirects=True)

            assert response.status_code == 200
            assert b'Integration Test Memo' in response.data

            # 3. 验证备忘录创建
            memo = Memo.query.filter_by(title='Integration Test Memo').first()
            assert memo is not None
            assert memo.user_id == test_user.id
            assert memo.status == 'pending'

            # 4. 更新备忘录状态
            response = client.post(
                url_for('memo.update_status', memo_id=memo.id),
                data={'new_status': 'in_progress'},
                follow_redirects=True
            )
            assert response.status_code == 200

            # 刷新备忘录对象
            db.session.refresh(memo)
            assert memo.status == 'in_progress'

            # 5. 编辑备忘录
            response = client.post(
                url_for('memo.edit', memo_id=memo.id),
                data={
                    'title': 'Updated Integration Test Memo',
                    'content': 'Updated content for integration testing',
                    'status': 'in_progress',
                    'no_expiry': True
                },
                follow_redirects=True
            )
            assert response.status_code == 200
            assert b'Updated Integration Test Memo' in response.data

            # 6. 完成备忘录
            response = client.post(
                url_for('memo.update_status', memo_id=memo.id),
                data={'new_status': 'completed'},
                follow_redirects=True
            )
            assert response.status_code == 200

            db.session.refresh(memo)
            assert memo.status == 'completed'

            # 7. 删除备忘录
            response = client.post(
                url_for('memo.delete', memo_id=memo.id),
                follow_redirects=True
            )
            assert response.status_code == 200

            # 验证备忘录已删除
            deleted_memo = Memo.query.get(memo.id)
            assert deleted_memo is None

    def test_memo_list_pagination(self, client, test_user):
        """测试备忘录列表分页"""
        with client:
            # 模拟登录
            with client.session_transaction() as sess:
                sess['user_id'] = test_user.id
                sess['_fresh'] = True

            # 创建多个备忘录
            for i in range(15):
                memo = Memo(
                    title=f'Test Memo {i}',
                    content=f'Content for memo {i}',
                    status='pending',
                    user_id=test_user.id
                )
                db.session.add(memo)
            db.session.commit()

            # 测试第一页
            response = client.get(url_for('memo.list'))
            assert response.status_code == 200
            assert b'Test Memo 0' in response.data
            assert b'Test Memo 9' in response.data  # 假设每页10个

            # 测试第二页
            response = client.get(url_for('memo.list', page=2))
            assert response.status_code == 200
            assert b'Test Memo 10' in response.data
            assert b'Test Memo 14' in response.data


class TestAuthenticationIntegration:
    """认证集成测试"""

    def test_oauth_login_flow(self, client, app):
        """测试OAuth登录流程"""
        # 这个测试需要模拟OAuth回调
        # 在实际测试中，可能需要使用测试OAuth服务器或mock
        pass

    def test_session_management(self, client, authenticated_client, test_user):
        """测试会话管理"""
        # 未登录访问受保护页面
        response = client.get(url_for('memo.list'))
        assert response.status_code == 302  # 重定向到登录

        # 登录后访问
        response = authenticated_client.get(url_for('memo.list'))
        assert response.status_code == 200

        # 登出
        response = authenticated_client.get(url_for('auth.logout'), follow_redirects=True)
        assert response.status_code == 200

        # 验证会话已清除 - 再次尝试访问应该重定向
        response = authenticated_client.get(url_for('memo.list'))
        assert response.status_code == 302

    def test_user_profile_management(self, client, test_user):
        """测试用户资料管理"""
        with client:
            # 登录
            with client.session_transaction() as sess:
                sess['user_id'] = test_user.id
                sess['_fresh'] = True

            # 访问资料页面
            response = client.get(url_for('user.profile'))
            assert response.status_code == 200
            assert test_user.username.encode() in response.data


class TestErrorHandlingIntegration:
    """错误处理集成测试"""

    def test_404_error_handling(self, client):
        """测试404错误处理"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404

    def test_403_error_handling(self, client, test_user):
        """测试403错误处理"""
        # 创建其他用户的备忘录
        other_user = User(
            oauth_provider='github',
            oauth_user_id='67890',
            username='other_user',
            email='other@example.com'
        )
        db.session.add(other_user)
        db.session.commit()

        other_memo = Memo(
            title='Other User Memo',
            content='Content',
            status='pending',
            user_id=other_user.id
        )
        db.session.add(other_memo)
        db.session.commit()

        with client:
            # 用test_user登录，尝试访问其他用户的备忘录
            with client.session_transaction() as sess:
                sess['user_id'] = test_user.id
                sess['_fresh'] = True

            response = client.get(url_for('memo.edit', memo_id=other_memo.id))
            assert response.status_code == 403

    def test_500_error_handling(self, client, app):
        """测试500错误处理"""
        # 可以通过模拟异常来测试
        # 这里暂时跳过，因为需要修改代码来触发异常
        pass


class TestSecurityIntegration:
    """安全集成测试"""

    def test_csrf_protection(self, client, test_user):
        """测试CSRF保护"""
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = test_user.id
                sess['_fresh'] = True

            # 尝试POST请求而没有CSRF token
            response = client.post(url_for('memo.create'), data={
                'title': 'Test Memo',
                'content': 'Content',
                'status': 'pending'
            })
            # 应该被CSRF保护阻止
            assert response.status_code == 400 or b'CSRF' in response.data

    def test_xss_prevention(self, client, test_user):
        """测试XSS防护"""
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = test_user.id
                sess['_fresh'] = True

            # 尝试创建包含XSS脚本的备忘录
            response = client.post(url_for('memo.create'), data={
                'title': '<script>alert("xss")</script>',
                'content': 'Normal content',
                'status': 'pending',
                'no_expiry': True
            }, follow_redirects=True)

            # 应该被表单验证阻止
            assert response.status_code == 200
            # 验证脚本标签没有被执行（在HTML中被转义）
            assert b'&lt;script&gt;' in response.data or b'<script>' not in response.data

    def test_sql_injection_prevention(self, client, test_user):
        """测试SQL注入防护"""
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = test_user.id
                sess['_fresh'] = True

            # 尝试SQL注入
            malicious_title = "'; DROP TABLE memos; --"
            response = client.post(url_for('memo.create'), data={
                'title': malicious_title,
                'content': 'Content',
                'status': 'pending',
                'no_expiry': True
            }, follow_redirects=True)

            # 应该正常创建备忘录，而不是执行SQL
            assert response.status_code == 200
            memo = Memo.query.filter_by(title=malicious_title).first()
            assert memo is not None  # 备忘录被创建，说明没有SQL注入
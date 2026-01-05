"""
备忘录模块测试
"""
import pytest
from app.models.memo import Memo, MemoStatus
from app.services.memo_service import MemoService
from app import db
from flask import url_for


class TestMemoModel:
    """备忘录模型测试"""

    def test_memo_creation(self, app, test_user):
        """测试备忘录创建"""
        with app.app_context():
            memo = Memo(
                title='Test Memo',
                content='Test content',
                status='pending',
                user_id=test_user.id
            )
            db.session.add(memo)
            db.session.commit()

            saved_memo = Memo.query.filter_by(title='Test Memo').first()
            assert saved_memo is not None
            assert saved_memo.title == 'Test Memo'
            assert saved_memo.content == 'Test content'
            assert saved_memo.status == 'pending'
            assert saved_memo.user_id == test_user.id

    def test_memo_repr(self, test_memo):
        """测试备忘录字符串表示"""
        assert 'Test Memo' in str(test_memo)
        assert 'pending' in str(test_memo)

    def test_memo_to_dict(self, test_memo):
        """测试备忘录字典转换"""
        memo_dict = test_memo.to_dict()
        assert memo_dict['title'] == 'Test Memo'
        assert memo_dict['content'] == 'This is a test memo content'
        assert memo_dict['status'] == 'pending'

    def test_status_transitions(self):
        """测试状态流转"""
        # pending状态可以流转到in_progress
        assert MemoStatus.can_transition('pending', 'in_progress')

        # pending状态不能直接流转到completed
        assert not MemoStatus.can_transition('pending', 'completed')

        # in_progress可以流转到completed
        assert MemoStatus.can_transition('in_progress', 'completed')

        # completed可以流转到closed
        assert MemoStatus.can_transition('completed', 'closed')

    def test_get_all_statuses(self):
        """测试获取所有状态"""
        statuses = MemoStatus.get_all_statuses()
        expected_statuses = ['pending', 'in_progress', 'completed', 'closed', 'expired']
        assert set(statuses) == set(expected_statuses)


class TestMemoService:
    """备忘录服务测试"""

    def test_create_memo(self, app, test_user):
        """测试创建备忘录服务"""
        with app.app_context():
            memo = MemoService.create_memo(
                title='Service Test Memo',
                content='Service test content',
                status='pending',
                user_id=test_user.id
            )

            assert memo is not None
            assert memo.title == 'Service Test Memo'
            assert memo.user_id == test_user.id

    def test_get_memo_by_id(self, app, test_user, test_memo):
        """测试根据ID获取备忘录"""
        with app.app_context():
            memo = MemoService.get_memo_by_id(test_memo.id)
            assert memo is not None
            assert memo.id == test_memo.id

            # 测试获取不存在的备忘录
            non_existent = MemoService.get_memo_by_id(99999)
            assert non_existent is None

    def test_update_memo(self, app, test_user, test_memo):
        """测试更新备忘录"""
        with app.app_context():
            result = MemoService.update_memo(
                test_memo.id,
                title='Updated Title',
                content='Updated content',
                status='in_progress'
            )

            assert result is not None

            # 重新获取并验证更新
            updated_memo = Memo.query.get(test_memo.id)
            assert updated_memo.title == 'Updated Title'
            assert updated_memo.content == 'Updated content'
            assert updated_memo.status == 'in_progress'

    def test_delete_memo(self, app, test_user, test_memo):
        """测试删除备忘录"""
        with app.app_context():
            result = MemoService.delete_memo(test_memo.id)
            assert result is True

            # 验证已删除
            deleted_memo = Memo.query.get(test_memo.id)
            assert deleted_memo is None

            # 测试删除不存在的备忘录
            result = MemoService.delete_memo(99999)
            assert result is False


class TestMemoRoutes:
    """备忘录路由测试"""

    def test_list_requires_login(self, client):
        """测试备忘录列表需要登录"""
        response = client.get('/memo/')
        assert response.status_code == 302
        assert 'auth/login' in response.headers['Location']

    def test_create_requires_login(self, client):
        """测试创建备忘录需要登录"""
        response = client.get('/memo/create')
        assert response.status_code == 302

    def test_list_authenticated(self, authenticated_client, test_user, test_memo):
        """测试认证用户可以访问备忘录列表"""
        response = authenticated_client.get('/memo/')
        assert response.status_code == 200
        assert b'Test Memo' in response.data

    def test_create_memo_get(self, authenticated_client):
        """测试创建备忘录页面"""
        response = authenticated_client.get('/memo/create')
        assert response.status_code == 200
        assert b'Create New Memo' in response.data

    def test_create_memo_post(self, authenticated_client):
        """测试创建备忘录POST请求"""
        response = authenticated_client.post('/memo/create', data={
            'title': 'New Test Memo',
            'content': 'New test content',
            'status': 'pending'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Memo created successfully' in response.data

    def test_edit_memo_get(self, authenticated_client, test_memo):
        """测试编辑备忘录页面"""
        response = authenticated_client.get(f'/memo/{test_memo.id}/edit')
        assert response.status_code == 200
        assert b'Edit Memo' in response.data

    def test_delete_memo(self, authenticated_client, test_memo):
        """测试删除备忘录"""
        response = authenticated_client.post(
            f'/memo/{test_memo.id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Memo deleted successfully' in response.data
"""
表单测试
"""
import pytest
from app.forms.memo import MemoForm, MemoStatusForm
from flask_wtf.csrf import generate_csrf


class TestMemoForm:
    """备忘录表单测试"""

    def test_memo_form_creation(self, app):
        """测试表单创建"""
        with app.app_context():
            form = MemoForm()
            assert form.title is not None
            assert form.content is not None
            assert form.status is not None
            assert form.expired_at is not None
            assert form.no_expiry is not None

    def test_memo_form_validation_valid(self, app):
        """测试有效表单验证"""
        with app.app_context():
            form = MemoForm()
            # 测试配置中禁用了CSRF，所以不需要csrf_token

            form.title.data = 'Valid Title'
            form.content.data = 'Valid content for testing'
            form.status.data = 'pending'

            assert form.validate() is True

    def test_memo_form_validation_required_fields(self, app):
        """测试必填字段验证"""
        with app.app_context():
            form = MemoForm()
            # 测试配置中禁用了CSRF，所以不需要csrf_token

            # 空标题
            form.title.data = ''
            form.content.data = 'Valid content'
            form.status.data = 'pending'

            assert form.validate() is False
            assert 'title' in form.errors

            # 空内容
            form.title.data = 'Valid Title'
            form.content.data = ''
            form.status.data = 'pending'

            assert form.validate() is False
            assert 'content' in form.errors

    def test_memo_form_validation_length_limits(self, app):
        """测试长度限制验证"""
        with app.app_context():
            form = MemoForm()
            # 测试配置中禁用了CSRF，所以不需要csrf_token

            # 标题过长
            form.title.data = 'A' * 201  # 超过200字符
            form.content.data = 'Valid content'
            form.status.data = 'pending'

            assert form.validate() is False
            assert 'title' in form.errors

            # 内容过长
            form.title.data = 'Valid Title'
            form.content.data = 'A' * 10001  # 超过10000字符
            form.status.data = 'pending'

            assert form.validate() is False
            assert 'content' in form.errors

    def test_memo_form_validation_xss_prevention(self, app):
        """测试XSS防护"""
        with app.app_context():
            form = MemoForm()
            # 测试配置中禁用了CSRF，所以不需要csrf_token

            form.title.data = 'Valid Title'
            form.content.data = '<script>alert("xss")</script>'
            form.status.data = 'pending'

            assert form.validate() is False
            assert 'content' in form.errors

    def test_memo_form_validation_invalid_title_chars(self, app):
        """测试标题字符验证"""
        with app.app_context():
            form = MemoForm()
            # 测试配置中禁用了CSRF，所以不需要csrf_token

            form.title.data = 'Invalid@Title#$%'
            form.content.data = 'Valid content'
            form.status.data = 'pending'

            assert form.validate() is False
            assert 'title' in form.errors


class TestMemoStatusForm:
    """备忘录状态表单测试"""

    def test_status_form_creation(self, app):
        """测试状态表单创建"""
        with app.app_context():
            form = MemoStatusForm()
            assert form.new_status is not None

    def test_status_form_with_current_status(self, app):
        """测试带当前状态的状态表单"""
        with app.app_context():
            # pending状态的表单
            form = MemoStatusForm(current_status='pending')
            choices = [choice[0] for choice in form.new_status.choices]

            # 应该包含pending状态本身和允许的流转状态
            assert 'pending' in choices
            assert 'in_progress' in choices
            assert 'completed' not in choices  # pending不能直接到completed

    def test_status_form_validation(self, app):
        """测试状态表单验证"""
        with app.app_context():
            form = MemoStatusForm()
            # 测试配置中禁用了CSRF，所以不需要csrf_token
            form.new_status.data = 'in_progress'

            assert form.validate() is True
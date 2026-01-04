"""
备忘录表单
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeLocalField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from flask_babel import gettext as _
from app.models.memo import MemoStatus
import re


class MemoForm(FlaskForm):
    """备忘录表单"""
    title = StringField(
        _('Title'),
        validators=[
            DataRequired(message=_('Title is required')),
            Length(min=1, max=200, message=_('Title must be between 1 and 200 characters'))
        ],
        render_kw={"placeholder": _("Enter a descriptive title for your memo")}
    )

    content = TextAreaField(
        _('Content'),
        validators=[
            DataRequired(message=_('Content is required')),
            Length(min=1, max=10000, message=_('Content must be less than 10,000 characters'))
        ],
        render_kw={"placeholder": _("Write your memo content here..."), "rows": 8}
    )

    status = SelectField(
        _('Status'),
        choices=[(status, _(status.replace('_', ' ').title())) for status in MemoStatus.get_all_statuses()],
        default=MemoStatus.PENDING
    )

    expired_at = DateTimeLocalField(
        _('Expiration Date'),
        validators=[Optional()],
        render_kw={"placeholder": _("Select expiration date and time")}
    )

    no_expiry = BooleanField(_('No expiration'), default=True)

    submit = SubmitField(_('Save Memo'))

    def validate_content(self, field):
        """验证内容不包含危险的HTML标签"""
        dangerous_tags = ['<script', '<iframe', '<object', '<embed', '<form', '<input', '<button']
        content_lower = field.data.lower()

        for tag in dangerous_tags:
            if tag in content_lower:
                raise ValidationError(_('Content contains potentially dangerous HTML tags'))

    def validate_title(self, field):
        """验证标题不包含特殊字符"""
        # 允许字母、数字、中文字符、空格和基本标点符号
        if not re.match(r'^[\w\s\u4e00-\u9fff.,!?-]+$', field.data):
            raise ValidationError(_('Title contains invalid characters'))


class MemoStatusForm(FlaskForm):
    """备忘录状态更新表单"""
    new_status = SelectField(_('New Status'), validators=[DataRequired()])
    submit = SubmitField(_('Update Status'))

    def __init__(self, current_status=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if current_status:
            # 只显示允许的状态转换选项
            allowed_transitions = MemoStatus.get_status_transitions().get(current_status, [])
            self.new_status.choices = [
                (status, _(status.replace('_', ' ').title()))
                for status in allowed_transitions
            ]
            # 添加当前状态作为第一个选项
            self.new_status.choices.insert(0, (current_status, _(current_status.replace('_', ' ').title())))
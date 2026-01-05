"""
备忘录模型
"""
from datetime import datetime
from app import db
from flask_login import current_user


class MemoStatus:
    """备忘录状态枚举"""
    PENDING = 'pending'        # 待办
    IN_PROGRESS = 'in_progress' # 进行中
    COMPLETED = 'completed'    # 已完成
    CLOSED = 'closed'          # 关闭（废弃）
    EXPIRED = 'expired'        # 过期

    @classmethod
    def get_all_statuses(cls):
        """获取所有状态"""
        return [cls.PENDING, cls.IN_PROGRESS, cls.COMPLETED, cls.CLOSED, cls.EXPIRED]

    @classmethod
    def get_status_transitions(cls):
        """获取状态流转规则"""
        return {
            cls.PENDING: [cls.IN_PROGRESS, cls.CLOSED],
            cls.IN_PROGRESS: [cls.COMPLETED, cls.CLOSED],
            cls.COMPLETED: [cls.CLOSED],  # 已完成可以关闭
            cls.CLOSED: [],               # 关闭状态不可再流转
            cls.EXPIRED: [cls.CLOSED]     # 过期可以关闭
        }

    @classmethod
    def can_transition(cls, from_status, to_status):
        """检查是否可以从from_status流转到to_status"""
        transitions = cls.get_status_transitions()
        return to_status in transitions.get(from_status, [])


class Memo(db.Model):
    """备忘录模型"""
    __tablename__ = 'memos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default=MemoStatus.PENDING, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)  # 完成时间（状态变为completed时记录）
    expired_at = db.Column(db.DateTime, nullable=True)    # 过期时间（可选）

    # 关联用户
    user = db.relationship('User', backref=db.backref('memos', lazy='dynamic'))

    # 索引
    __table_args__ = (
        db.Index('idx_memo_user_status', 'user_id', 'status'),
        db.Index('idx_memo_user_updated', 'user_id', 'updated_at'),
        db.Index('idx_memo_expired', 'expired_at'),
    )

    def __repr__(self):
        return f'<Memo {self.title[:20]}... ({self.status})>'

    def to_dict(self):
        """转换为字典，便于JSON序列化"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'expired_at': self.expired_at.isoformat() if self.expired_at else None
        }

    def can_change_status(self, new_status):
        """检查是否可以更改为新状态"""
        return MemoStatus.can_transition(self.status, new_status)

    def check_and_update_expiry(self):
        """检查是否过期并自动更新状态"""
        if (self.expired_at and 
            self.status not in [MemoStatus.EXPIRED, MemoStatus.CLOSED] and 
            datetime.utcnow() > self.expired_at):
            self.status = MemoStatus.EXPIRED
            db.session.commit()
            return True
        return False

    @property
    def is_expired(self):
        """检查是否过期"""
        return self.expired_at and datetime.utcnow() > self.expired_at

    @classmethod
    def get_user_memos(cls, user_id, page=1, per_page=10):
        """获取用户的备忘录（分页）- 优化版本"""
        from datetime import datetime

        # 获取分页结果
        pagination = cls.query.filter_by(user_id=user_id)\
                             .order_by(cls.updated_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)

        # 批量检查过期状态（只检查未过期且未关闭的memo）
        now = datetime.utcnow()
        expired_memos = []
        for memo in pagination.items:
            if (memo.expired_at and
                memo.status not in [MemoStatus.EXPIRED, MemoStatus.CLOSED] and
                now > memo.expired_at):
                expired_memos.append(memo)

        # 批量更新过期状态
        if expired_memos:
            for memo in expired_memos:
                memo.status = MemoStatus.EXPIRED
            db.session.commit()

        return pagination


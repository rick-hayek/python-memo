"""
备忘录业务逻辑
"""
from app import db
from app.models.memo import Memo, MemoStatus
from flask_login import current_user


class MemoService:
    """备忘录服务类"""

    @staticmethod
    def create_memo(title, content, status=MemoStatus.PENDING, expired_at=None):
        """创建备忘录"""
        if not current_user.is_authenticated:
            raise ValueError("用户未登录")

        memo = Memo(
            title=title,
            content=content,
            status=status,
            user_id=current_user.id,
            expired_at=expired_at
        )
        db.session.add(memo)
        db.session.commit()
        return memo

    @staticmethod
    def get_memo_by_id(memo_id):
        """根据ID获取备忘录"""
        return Memo.query.filter_by(id=memo_id, user_id=current_user.id).first()

    @staticmethod
    def get_user_memos(page=1, per_page=10):
        """获取当前用户的备忘录（分页）"""
        if not current_user.is_authenticated:
            return None

        return Memo.get_user_memos(current_user.id, page, per_page)

    @staticmethod
    def update_memo(memo_id, title=None, content=None, status=None, expired_at=None):
        """更新备忘录"""
        memo = MemoService.get_memo_by_id(memo_id)
        if not memo:
            return None

        if title is not None:
            memo.title = title
        if content is not None:
            memo.content = content
        if expired_at is not None:
            memo.expired_at = expired_at
        if status is not None:
            if not memo.can_change_status(status):
                raise ValueError(f"无法将状态从 {memo.status} 更改为 {status}")
            # 状态变更时处理特殊逻辑
            old_status = memo.status
            memo.status = status
            
            # 如果状态变为completed，记录完成时间
            if status == MemoStatus.COMPLETED and old_status != MemoStatus.COMPLETED:
                from datetime import datetime
                memo.completed_at = datetime.utcnow()

        db.session.commit()
        return memo

    @staticmethod
    def delete_memo(memo_id):
        """删除备忘录"""
        memo = MemoService.get_memo_by_id(memo_id)
        if not memo:
            return False

        db.session.delete(memo)
        db.session.commit()
        return True

    @staticmethod
    def change_status(memo_id, new_status):
        """更改备忘录状态"""
        return MemoService.update_memo(memo_id, status=new_status)


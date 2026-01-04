"""
备忘录CRUD路由
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_babel import gettext as _
from flask_wtf.csrf import validate_csrf
from app.services.memo_service import MemoService
from app.models.memo import MemoStatus
from app.forms.memo import MemoForm, MemoStatusForm

memo_bp = Blueprint('memo', __name__)


@memo_bp.route('/')
@login_required
def list():
    """备忘录列表页"""
    page = request.args.get('page', 1, type=int)
    pagination = MemoService.get_user_memos(page=page, per_page=10)

    return render_template('memo/list.html',
                         memos=pagination.items,
                         pagination=pagination,
                         MemoStatus=MemoStatus)


@memo_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """创建备忘录"""
    form = MemoForm()
    
    if form.validate_on_submit():
        # 处理过期时间
        expired_at = None
        if form.expired_at.data and not form.no_expiry.data:
            expired_at = form.expired_at.data
        
        try:
            memo = MemoService.create_memo(
                title=form.title.data,
                content=form.content.data,
                status=form.status.data,
                expired_at=expired_at
            )
            flash(_('Memo created successfully'), 'success')
            return redirect(url_for('memo.list'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('memo/create.html', form=form, MemoStatus=MemoStatus)


@memo_bp.route('/<int:memo_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(memo_id):
    """编辑备忘录"""
    memo = MemoService.get_memo_by_id(memo_id)
    if not memo:
        abort(404)

    form = MemoForm(obj=memo)
    # 设置no_expiry复选框的初始状态
    form.no_expiry.data = not bool(memo.expired_at)

    if form.validate_on_submit():
        # 处理过期时间
        expired_at = None
        if form.expired_at.data and not form.no_expiry.data:
            expired_at = form.expired_at.data

        # 只有当状态真正改变时才传递status参数
        status_to_update = None
        if form.status.data != memo.status:
            status_to_update = form.status.data

        try:
            MemoService.update_memo(
                memo_id,
                title=form.title.data,
                content=form.content.data,
                status=status_to_update,
                expired_at=expired_at
            )
            flash(_('Memo updated successfully'), 'success')
            return redirect(url_for('memo.list'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('memo/edit.html', form=form, memo=memo, MemoStatus=MemoStatus)


@memo_bp.route('/<int:memo_id>/delete', methods=['POST'])
@login_required
def delete(memo_id):
    """删除备忘录"""
    # 验证CSRF令牌
    try:
        validate_csrf(request.form.get('csrf_token'))
    except Exception as e:
        flash(_('CSRF token validation failed'), 'error')
        return redirect(url_for('memo.list'))
    
    if MemoService.delete_memo(memo_id):
        flash(_('Memo deleted successfully'), 'success')
    else:
        flash(_('Memo not found'), 'error')

    return redirect(url_for('memo.list'))


@memo_bp.route('/<int:memo_id>/status', methods=['POST'])
@login_required
def change_status(memo_id):
    """更改备忘录状态"""
    # 验证CSRF令牌
    try:
        validate_csrf(request.form.get('csrf_token'))
    except Exception as e:
        flash(_('CSRF token validation failed'), 'error')
        return redirect(url_for('memo.list'))
    
    new_status = request.form.get('new_status')
    
    if not new_status or new_status not in MemoStatus.get_all_statuses():
        flash(_('Invalid status'), 'error')
        return redirect(url_for('memo.list'))

    try:
        MemoService.change_status(memo_id, new_status)
        flash(_('Status updated successfully'), 'success')
    except ValueError as e:
        flash(str(e), 'error')

    return redirect(url_for('memo.list'))


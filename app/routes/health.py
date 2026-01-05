"""
健康检查和监控路由
"""
from flask import Blueprint, jsonify, current_app
from app import db
from app.models.user import User
from app.models.memo import Memo
import time
import psutil
import os


health_bp = Blueprint('health', __name__, url_prefix='/health')


@health_bp.route('/')
def health_check():
    """基础健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'memo-app'
    })


@health_bp.route('/detailed')
def detailed_health_check():
    """详细健康检查"""
    start_time = time.time()

    # 数据库连接检查
    db_healthy = True
    db_error = None
    try:
        # 简单查询测试数据库连接
        db.session.execute(db.text('SELECT 1'))
    except Exception as e:
        db_healthy = False
        db_error = str(e)

    # 基本统计信息
    try:
        user_count = User.query.count()
        memo_count = Memo.query.count()
    except Exception as e:
        user_count = memo_count = 0

    # 系统信息
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1024 / 1024  # MB

    response_time = time.time() - start_time

    health_data = {
        'status': 'healthy' if db_healthy else 'unhealthy',
        'timestamp': time.time(),
        'response_time': round(response_time, 3),
        'service': 'memo-app',
        'version': '1.0.0',
        'checks': {
            'database': {
                'status': 'healthy' if db_healthy else 'unhealthy',
                'error': db_error
            }
        },
        'metrics': {
            'users_count': user_count,
            'memos_count': memo_count,
            'memory_usage_mb': round(memory_usage, 2)
        }
    }

    status_code = 200 if db_healthy else 503
    return jsonify(health_data), status_code


@health_bp.route('/metrics')
def metrics():
    """性能指标"""
    # 数据库查询统计
    try:
        # 各状态备忘录数量
        status_counts = db.session.query(
            Memo.status, db.func.count(Memo.id)
        ).group_by(Memo.status).all()

        status_metrics = {status: count for status, count in status_counts}
    except Exception:
        status_metrics = {}

    # 用户活跃度（最近7天创建的用户）
    try:
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_users = User.query.filter(User.created_at >= week_ago).count()
    except Exception:
        recent_users = 0

    return jsonify({
        'timestamp': time.time(),
        'memo_status_distribution': status_metrics,
        'recent_users_7d': recent_users
    })
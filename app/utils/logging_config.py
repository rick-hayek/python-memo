"""
日志配置
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import current_app


def setup_logging(app):
    """配置应用日志"""

    # 确保日志目录存在
    log_dir = os.path.join(app.root_path, '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # 设置日志级别
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # 文件处理器 - 应用日志
    app_log_file = os.path.join(log_dir, 'app.log')
    file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # 错误日志处理器
    error_log_file = os.path.join(log_dir, 'error.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # 配置应用日志
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(log_level)

    # 配置Werkzeug日志（HTTP请求）
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.addHandler(file_handler)
    werkzeug_logger.setLevel(logging.WARNING)  # 只记录警告和错误

    # 配置SQLAlchemy日志
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.addHandler(file_handler)
    sqlalchemy_logger.setLevel(logging.WARNING)  # 只记录警告和错误

    # 记录启动信息
    app.logger.info('应用启动完成')
    app.logger.info(f'日志级别: {app.config.get("LOG_LEVEL", "INFO")}')
    app.logger.info(f'日志目录: {log_dir}')
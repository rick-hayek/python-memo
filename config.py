"""
应用配置文件
"""
import os
from dotenv import load_dotenv

# 根据环境加载不同的.env文件
env = os.environ.get('FLASK_ENV', 'development')
if env == 'development':
    # 开发环境：优先加载.env.development，如果不存在则加载.env
    if os.path.exists('.env.development'):
        load_dotenv('.env.development')
    else:
        load_dotenv()
else:
    # 生产环境：加载.env
    load_dotenv()


class Config:
    """基础配置类"""
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///memo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OAuth配置 - GitHub
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
    
    # OAuth回调URL
    OAUTH_REDIRECT_URI = os.environ.get('OAUTH_REDIRECT_URI') or 'http://127.0.0.1:5000/auth/github/callback'
    
    # 多语言配置（Flask-Babel）
    BABEL_DEFAULT_LOCALE = os.environ.get('BABEL_DEFAULT_LOCALE', 'zh_CN')
    BABEL_DEFAULT_TIMEZONE = os.environ.get('BABEL_DEFAULT_TIMEZONE', 'Asia/Shanghai')
    LANGUAGES = {
        'zh_CN': '中文',
        'en': 'English'
    }
    
    # CSRF配置（Flask-WTF）
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or SECRET_KEY  # 使用相同的密钥
    WTF_CSRF_TIME_LIMIT = 3600  # CSRF令牌有效期1小时
    
    # 会话安全配置
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # 生产环境建议使用 'Strict'
    
    # HTTPS和安全头配置
    PREFERRED_URL_SCHEME = 'https' if os.environ.get('FORCE_HTTPS', 'False').lower() == 'true' else 'http'
    
    # 安全头配置
    SECURITY_HEADERS = {
        'X-Frame-Options': 'SAMEORIGIN',  # 防止点击劫持
        'X-Content-Type-Options': 'nosniff',  # 防止MIME类型嗅探
        'X-XSS-Protection': '1; mode=block',  # XSS保护
        'Referrer-Policy': 'strict-origin-when-cross-origin',  # 引用策略
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',  # 权限策略
    }
    
    # HSTS配置（仅生产环境）
    HSTS_MAX_AGE = 31536000  # 1年
    HSTS_INCLUDE_SUBDOMAINS = True
    HSTS_PRELOAD = False


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    ENV = 'production'
    # 生产环境必须从环境变量读取密钥
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置SECRET_KEY环境变量")
    
    # 生产环境强制HTTPS
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PREFERRED_URL_SCHEME = 'https'
    
    # 生产环境启用HSTS
    HSTS_MAX_AGE = 31536000
    HSTS_INCLUDE_SUBDOMAINS = True
    HSTS_PRELOAD = True


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    # 测试环境使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # 测试环境禁用WTF CSRF
    WTF_CSRF_ENABLED = False
    # 测试环境简化会话配置
    SESSION_COOKIE_SECURE = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

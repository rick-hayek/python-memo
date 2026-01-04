"""
Flask应用工厂
"""
from flask import Flask, request, session, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from config import config
from flask_babel import get_translations

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()
csrf = CSRFProtect()


def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    print('translation directories:', app.config['BABEL_TRANSLATION_DIRECTORIES'])
    print('get_translations:', get_translations())

     # 配置Flask-Babel语言选择器（Flask-Babel 4.0兼容方式）
    # 在Flask-Babel 4.0中，需要使用Babel.localeselector作为类方法装饰器
    def get_locale():
        print("get_locale called")
        print('language from request:', request.accept_languages.best_match(app.config['LANGUAGES'].keys()))
        print('language from default:', app.config['BABEL_DEFAULT_LOCALE'])
        print('translation directories:', app.config['BABEL_TRANSLATION_DIRECTORIES'])

        # 优先从session获取语言设置
        if 'language' in session:
            print('language in session:', session['language'])
            return session['language']
        # 从请求头获取语言
  
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or app.config['BABEL_DEFAULT_LOCALE']

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    csrf.init_app(app)
    
    # 配置安全中间件
    @app.after_request
    def add_security_headers(response):
        """添加安全头"""
        security_headers = app.config.get('SECURITY_HEADERS', {})
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # 添加HSTS头（仅HTTPS）
        if request.is_secure and app.config.get('HSTS_MAX_AGE', 0) > 0:
            hsts_value = f"max-age={app.config['HSTS_MAX_AGE']}"
            if app.config.get('HSTS_INCLUDE_SUBDOMAINS'):
                hsts_value += "; includeSubDomains"
            if app.config.get('HSTS_PRELOAD'):
                hsts_value += "; preload"
            response.headers['Strict-Transport-Security'] = hsts_value
        
        # 添加CSP头
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.github.com; "
            "frame-ancestors 'none';"
        )
        response.headers['Content-Security-Policy'] = csp_policy
        
        return response
    
    @app.before_request
    def enforce_https():
        """强制HTTPS重定向"""
        if app.config.get('PREFERRED_URL_SCHEME') == 'https' and not request.is_secure:
            if request.url.startswith('http://'):
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)
    
    # 配置Flask-Login
    from flask_babel import gettext as _
    login_manager.login_view = 'auth.login'  # 未登录时重定向到登录页
    login_manager.login_message = _('Please login first')
    login_manager.login_message_category = 'info'
    
  
    # 将get_locale添加到模板上下文
    @app.context_processor
    def inject_locale():
        from flask_wtf.csrf import generate_csrf
        return dict(
            get_locale=get_locale,
            csrf_token=generate_csrf
        )
    
    @login_manager.user_loader
    def load_user(user_id):
        """加载用户"""
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # 初始化OAuth（需要在app context中）
    from app.services.oauth_service import init_oauth
    init_oauth(app)
    
    # 注册蓝图（必须在导入模型之后）
    from app.routes.auth import auth_bp
    from app.routes.index import index_bp
    from app.routes.user import user_bp
    from app.routes.memo import memo_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(index_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(memo_bp, url_prefix='/memo')
    
    # 注册语言切换路由
    @app.route('/set_language/<language>')
    def set_language(language):
        """设置语言"""
        if language in app.config['LANGUAGES']:
            session['language'] = language
        return redirect(request.referrer or url_for('index.index'))
    
    # 导入模型（必须在db初始化之后）
    from app.models import User, Memo
    
    # 创建数据库表（开发环境）
    with app.app_context():
        db.create_all()
    
    return app

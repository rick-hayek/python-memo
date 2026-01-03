"""
OAuth业务逻辑
"""
from authlib.integrations.flask_client import OAuth

# 全局OAuth实例
oauth = None


def init_oauth(app):
    """初始化OAuth客户端"""
    global oauth
    oauth = OAuth(app)
    
    # 注册GitHub OAuth
    github = oauth.register(
        name='github',
        client_id=app.config['GITHUB_CLIENT_ID'],
        client_secret=app.config['GITHUB_CLIENT_SECRET'],
        client_kwargs={
            'scope': 'user:email'
        },
        authorize_url='https://github.com/login/oauth/authorize',
        access_token_url='https://github.com/login/oauth/access_token',
        api_base_url='https://api.github.com/'
    )
    
    return oauth


def get_github_oauth():
    """获取GitHub OAuth客户端"""
    if oauth is None:
        raise RuntimeError("OAuth未初始化，请先调用init_oauth()")
    return oauth.github


def get_github_user_info(access_token):
    """获取GitHub用户信息"""
    from flask import current_app
    import requests
    
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # 获取用户基本信息
    user_response = requests.get('https://api.github.com/user', headers=headers)
    user_response.raise_for_status()
    user_data = user_response.json()
    
    # 获取用户邮箱（如果公开邮箱不可用）
    email = user_data.get('email')
    if not email:
        emails_response = requests.get('https://api.github.com/user/emails', headers=headers)
        if emails_response.status_code == 200:
            emails = emails_response.json()
            # 优先使用主邮箱
            primary_email = next((e for e in emails if e.get('primary')), None)
            if primary_email:
                email = primary_email.get('email')
            elif emails:
                email = emails[0].get('email')
    
    return {
        'oauth_provider': 'github',
        'oauth_user_id': str(user_data['id']),
        'username': user_data.get('login'),
        'email': email,
        'avatar_url': user_data.get('avatar_url')
    }

"""
备忘录网站 - 应用入口文件
"""
from app import create_app
import os

# 从环境变量获取配置名称，默认为development
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True)

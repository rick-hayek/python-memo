# 备忘录网站

基于Flask开发的备忘录管理网站，支持OAuth第三方登录和多语言。

## 项目状态

✅ **第六步完成** - 测试与优化已完成，准备部署上线

- ✅ 单元测试（26个测试通过）
- ✅ 性能优化（数据库索引、缓存、查询优化）
- ✅ 安全加固（CSRF/XSS防护）
- ✅ 错误处理（自定义错误页面）
- ✅ 日志配置（结构化日志）
- ✅ 健康监控（系统指标）

🚀 **下一步**: 第七步 - 部署上线

## 技术栈

- Python 3.x
- Flask 3.1.2
- SQLite
- Jinja2
- Flask-Babel (多语言支持)
- Flask-WTF (表单验证和CSRF保护)

## 安全特性

### 已实现的安全措施

- ✅ **认证与授权**: GitHub OAuth 2.0认证 + Flask-Login会话管理
- ✅ **CSRF保护**: Flask-WTF CSRF令牌验证
- ✅ **SQL注入防护**: SQLAlchemy ORM参数化查询
- ✅ **XSS防护**: Jinja2模板自动转义 + 表单内容验证
- ✅ **会话安全**: HttpOnly、Secure、SameSite cookie配置
- ✅ **HTTPS支持**: 生产环境强制HTTPS重定向
- ✅ **安全头**: HSTS、CSP、X-Frame-Options等安全头
- ✅ **输入验证**: WTForms表单验证 + 自定义安全验证器

### 安全配置

开发环境和生产环境有不同的安全配置：

- **开发环境**: HTTP, 非安全cookie
- **生产环境**: HTTPS强制, 安全cookie, HSTS启用

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制开发环境配置文件：

```bash
cp .env.development.example .env.development
```

编辑 `.env.development` 文件，填入你的配置（GitHub OAuth Client ID和Secret已预填）。

### 3. 编译翻译文件

Flask-Babel需要编译翻译文件才能使用：

```bash
# 安装babel工具（如果还没有）
pip install Babel

# 编译翻译文件
pybabel compile -d app/translations
```

### 4. 运行应用

```bash
python app.py
```

访问 http://127.0.0.1:5000

## 多语言支持

当前支持的语言：
- 中文 (zh_CN) - 默认
- English (en)

### 切换语言

在导航栏点击"语言"下拉菜单，选择要使用的语言。

### 添加新语言

1. 创建新的语言目录：
```bash
mkdir -p app/translations/新语言代码/LC_MESSAGES
```

2. 复制并翻译 `messages.po` 文件

3. 编译翻译文件：
```bash
pybabel compile -d app/translations
```

4. 在 `config.py` 的 `LANGUAGES` 字典中添加新语言

## 性能优化

### 已实现的性能优化

- ✅ **数据库查询优化**: 分页查询优化、数据库索引、批量操作
- ✅ **缓存机制**: 内存缓存系统、服务层缓存装饰器
- ✅ **错误处理**: 全局错误处理器、自定义错误页面
- ✅ **日志系统**: 结构化日志、文件轮转、环境配置
- ✅ **健康监控**: 健康检查端点、系统指标收集

### 性能监控

应用提供了以下监控端点：

- `/health/` - 基础健康检查
- `/health/detailed` - 详细健康检查（包含数据库连接）
- `/health/metrics` - 业务指标统计

### 性能测试

运行测试套件：

```bash
# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=app --cov-report=html
```

## 项目结构

详见 `ARCHITECTURE.md`

## 开发计划

详见 `IMPLEMENTATION_STEPS.md`

## 注意事项

- `.env.development` 文件包含敏感信息，已添加到 `.gitignore`，不会提交到Git
- 首次运行会自动创建 SQLite 数据库文件 `memo.db`
- GitHub OAuth 回调 URL 需要配置为：`http://127.0.0.1:5000/auth/github/callback`

# 备忘录网站

基于Flask开发的备忘录管理网站，支持OAuth第三方登录和多语言。

## 项目状态

🚧 开发中...

## 技术栈

- Python 3.x
- Flask 3.1.2
- SQLite
- Jinja2
- Flask-Babel (多语言支持)

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

## 项目结构

详见 `ARCHITECTURE.md`

## 开发计划

详见 `IMPLEMENTATION_STEPS.md`

## 注意事项

- `.env.development` 文件包含敏感信息，已添加到 `.gitignore`，不会提交到Git
- 首次运行会自动创建 SQLite 数据库文件 `memo.db`
- GitHub OAuth 回调 URL 需要配置为：`http://127.0.0.1:5000/auth/github/callback`

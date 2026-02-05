---
name: flask-modular-project
description: 建立模組化的 Flask Web 專案，遵循關注點分離原則
---

# Flask 模組化專案技能

此技能用於建立結構清晰、遵循最佳實踐的 Flask Web 專案。

## 核心原則

1. **關注點分離 (Separation of Concerns)**
   - CSS 使用外部樣式表 (External Stylesheets)
   - JavaScript 使用外部腳本 (External Scripts)
   - HTML 僅包含結構，不包含樣式和行為邏輯

2. **模板繼承 (Template Inheritance)**
   - 使用 `base.html` 作為基礎模板
   - 共用元件放在 `partials/` 目錄

3. **MVC 架構**
   - 使用 Flask Blueprints 組織路由
   - Model/Service/Route 分層架構

## 專案目錄結構

```
project_name/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── extensions.py         # Flask 擴展 (db, login_manager 等)
│   ├── models/               # 資料模型
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routes/               # Blueprint 路由
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── auth.py
│   ├── services/             # 業務邏輯
│   │   └── mail_service.py
│   ├── utils/                # 工具函數
│   │   ├── decorators.py
│   │   └── helpers.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── common.css    # 共用樣式
│   │   │   └── pages/        # 頁面專屬樣式
│   │   │       ├── index.css
│   │   │       └── login.css
│   │   ├── js/
│   │   │   ├── common.js     # 共用腳本
│   │   │   └── pages/        # 頁面專屬腳本
│   │   │       ├── index.js
│   │   │       └── login.js
│   │   └── images/
│   └── templates/
│       ├── base.html         # 基礎模板
│       ├── partials/         # 可重用元件
│       │   ├── _navbar.html
│       │   ├── _footer.html
│       │   └── _flash_messages.html
│       ├── index.html
│       └── login.html
├── config.py                 # 配置設定
├── run.py                    # 啟動腳本
└── requirements.txt
```

## 基礎模板範例

### templates/base.html

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}網站標題{% endblock %}</title>
    
    <!-- 共用樣式 -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/common.css') }}">
    
    <!-- 頁面專屬樣式 -->
    {% block styles %}{% endblock %}
</head>
<body>
    {% include "partials/_navbar.html" %}
    
    <main class="container">
        {% include "partials/_flash_messages.html" %}
        {% block content %}{% endblock %}
    </main>
    
    {% include "partials/_footer.html" %}
    
    <!-- 共用腳本 -->
    <script src="{{ url_for('static', filename='js/common.js') }}"></script>
    
    <!-- 頁面專屬腳本 -->
    {% block scripts %}{% endblock %}
</body>
</html>
```

### templates/index.html

```html
{% extends "base.html" %}

{% block title %}首頁{% endblock %}

{% block styles %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/index.css') }}">
{% endblock %}

{% block content %}
<h1>歡迎來到首頁</h1>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/pages/index.js') }}"></script>
{% endblock %}
```

## Flask App Factory 範例

### app/__init__.py

```python
import os
from flask import Flask
from app.extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    
    # 初始化擴展
    db.init_app(app)
    login_manager.init_app(app)
    
    # 註冊 Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    return app
```

## CSS 命名規範

建議使用 BEM (Block Element Modifier) 命名規範：

```css
/* Block */
.card { }

/* Element */
.card__title { }
.card__content { }

/* Modifier */
.card--highlighted { }
.card__title--large { }
```

## 使用方式

當使用者要求建立新的 Flask 專案時，請遵循以上結構和原則：

1. 先建立目錄結構
2. 建立 `base.html` 基礎模板
3. CSS 和 JS 一律放在 `static/` 目錄
4. 使用 Blueprint 組織路由
5. 遵循 url_for 的 Blueprint 前綴規則 (如 `main.index`, `auth.login`)

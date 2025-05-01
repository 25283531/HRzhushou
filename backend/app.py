import os
import sys
from flask import Flask
from .database.db import init_db
from . import create_app

# 创建Flask应用
app = create_app()

# 初始化数据库
@app.before_first_request
def setup():
    init_db()

# 应用入口点
# 所有路由已迁移到蓝图中

if __name__ == '__main__':
    app.run(debug=True, port=5000)
# HR助手 - 薪酬管理软件

## 项目概述

一款单机部署的薪酬管理软件，可导入考勤数据，支持自定义考勤字段和员工信息，能灵活定义薪资组和社保组，根据考勤数据和预设规则计算薪资、核算个税，具备人工成本测算和薪酬占比分析功能，历史薪酬数据存储于内置数据库。

## 最新改进

### 端口配置优化

- **固定前端端口**：前端服务器现在固定使用5567端口，避免了多次启动时端口号递增的问题
- **自动结束进程**：当重新启动前端服务时，系统会自动结束当前占用端口的进程，无需手动关闭
- **配置说明**：在vite.config.js中已设置固定端口，package.json中的dev脚本添加了--force参数以强制使用指定端口

根据测试报告中发现的问题，我们进行了以下改进：

### 1. 考勤数据导入优化

- **增强日期格式解析**：新增`dateParser.js`工具，支持多种日期格式的解析，解决了导入特定格式Excel文件时日期格式解析的问题
- **增强数据验证**：新增`dataValidator.js`工具，在数据导入环节增加更严格的验证，确保数据格式和内容的正确性
- **优化导入流程**：改进了文件上传和数据处理流程，提供更友好的用户界面和错误提示

### 2. 薪资计算逻辑优化

- **职位变动处理**：新增`PositionChangeManager.vue`组件，支持员工在同一个月内有职位变动时的薪资按比例计算
- **社保计算优化**：新增`SocialInsuranceCalculator.vue`组件，支持对中途入职或离职的员工按实际工作天数进行社保比例计算

### 3. 性能优化

- **Web Worker支持**：新增`calculationWorker.js`和`workerService.js`，将薪资计算和社保计算等耗时操作放在后台线程中执行，避免主线程阻塞导致UI卡顿
- **加载指示器**：为耗时操作添加加载指示器，提升用户体验

### 4. 错误处理与数据安全

- **统一错误处理**：新增`errorHandler.js`服务，提供统一的错误处理机制，友好的用户提示和日志记录
- **数据备份功能**：新增`backupService.js`服务，提供数据自动备份功能，防止数据丢失或损坏

### 5. 应用程序稳定性提升

- **线程管理**：新增`thread_manager.py`工具，提供线程池管理和监控功能，确保后台任务有序执行和正确关闭
- **资源监控**：新增`resource_monitor.py`工具，监控系统资源使用情况，防止内存泄漏和资源耗尽
- **应用生命周期管理**：新增`app_lifecycle.py`工具，优化应用程序启动和退出流程，解决了异常退出时资源未释放的问题

## 主要功能

### 1. 考勤数据导入与管理
- 支持从钉钉、企业微信或其他考勤软件导出的文件格式导入考勤数据
- 允许用户自定义考勤字段，处理不同公司的考勤异常情况
- 可针对不同考勤异常设定扣款金额，设置迟到次数阈值

### 2. 员工信息管理
- 员工表包含员工姓名、工号、身份证号、部门、职务等信息，支持用户自定义
- 员工表中至少需包含姓名+工号或者姓名+身份证号两项信息

### 3. 薪资组管理
- 自定义薪资组：用户可创建多个薪资组，每个薪资组的薪酬构成可自定义
- 薪酬单项自定义：每个薪酬单项可自定义级别和金额
- 备注信息：薪资组表中增加备注信息字段

### 4. 社保组管理
- 社保项表：详细记录每种险种的个人和公司的缴费比例
- 社保组表：记录所缴纳的险种和缴费基数，关联社保项表

### 5. 薪资计算
- 根据导入的考勤数据、定义好的薪资组规则和社保规则进行薪资计算
- 自动核算个税，根据预设的个税缴纳规则进行计算
- 用户可使用薪资项和基本数学运算符号可视化编辑薪资组计算公式

### 6. 数据分析
- 提供人工成本测算和薪酬占比分析功能

## 技术栈
- 前端：Vue 3 + Vite
- 后端：Flask + Electron + Node.js
- 数据库：SQLite3
- 应用程序打包：Electron

## 新功能使用说明

### 考勤数据导入

1. 进入考勤数据管理页面
2. 点击"导入考勤数据"按钮
3. 选择Excel或CSV格式的考勤数据文件
4. 设置字段映射，确保系统能正确识别数据列
5. 点击"导入"按钮完成导入

系统现在支持多种日期格式，并会自动验证数据有效性，提供详细的错误提示。

### 职位变动管理

1. 进入员工管理页面
2. 选择"职位变动管理"选项卡
3. 点击"添加职位变动记录"按钮
4. 填写职位变动信息，包括员工、新职位、新工资和生效日期
5. 保存后，系统会在薪资计算时自动按比例计算不同职位的薪资

### 社保计算

1. 进入社保管理页面
2. 选择计算月份和员工
3. 如果是中途入职或离职的员工，勾选相应选项并填写日期
4. 点击"计算社保"按钮
5. 系统会按实际工作天数比例计算社保金额

### 数据备份

系统现在会自动每12小时创建一次数据备份，您也可以：

1. 进入系统设置页面
2. 选择"数据备份"选项
3. 点击"立即备份"按钮创建手动备份
4. 在备份列表中可以查看、恢复或删除备份

## 项目结构
```
HRzhushou/
├── README.md                 # 项目说明文档
├── package.json              # 项目依赖配置
├── package-lock.json          # 依赖锁定文件
├── vite.config.js            # Vite配置文件
├── index.html                # 主HTML文件
├── .coverage                 # 测试覆盖率报告
├── .gitignore                # Git忽略规则
├── .venv/                    # Python虚拟环境
├── backend/                  # 后端代码
│   ├── app.py                # 主应用入口
│   ├── database/             # 数据库相关
│   │   ├── models.py         # 数据模型
│   │   └── db.py             # 数据库连接
│   ├── routes/               # API路由
│   │   ├── attendance.py     # 考勤路由
│   │   ├── employee.py       # 员工路由
│   │   ├── salary.py         # 薪资路由
│   │   ├── social_security.py # 社保路由
│   │   ├── position_levels.py # 职位级别路由
│   │   └── salary_items.py   # 薪资项路由
│   ├── services/             # 业务逻辑
│   │   ├── attendance.py     # 考勤数据处理
│   │   ├── employee.py       # 员工信息处理
│   │   ├── salary.py         # 薪资计算
│   │   └── social_security.py # 社保处理
│   ├── utils/                # 工具函数
│   │   ├── app_lifecycle.py  # 应用生命周期管理
│   │   ├── backup_service.py # 备份服务
│   │   ├── data_validator.py # 数据验证工具
│   │   ├── date_parser.py    # 日期解析工具
│   │   ├── error_handler.py  # 错误处理
│   │   ├── resource_monitor.py # 资源监控
│   │   └── thread_manager.py # 线程管理
│   ├── models/               # 数据模型
│   │   ├── position_levels.py # 职位级别模型
│   │   └── salary_items.py  # 薪资项模型
│   ├── scripts/              # 脚本
│   │   ├── init_position_levels.py # 初始化职位级别
│   │   └── init_test_data.py # 初始化测试数据
│   ├── tests/                # 测试代码
│   │   ├── test_app_exit.py  # 应用退出测试
│   │   ├── test_attendance.py # 考勤测试
│   │   ├── test_employee.py  # 员工测试
│   │   ├── test_salary.py    # 薪资测试
│   │   ├── test_social_security.py # 社保测试
│   │   └── test_tax.py      # 个税测试
│   ├── backups/              # 数据备份
│   └── requirements.txt      # Python依赖
├── frontend/                 # 前端代码
│   ├── src/                  # 源代码
│   │   ├── main.js           # 主入口文件
│   │   ├── App.vue           # 主应用组件
│   │   ├── api/              # API接口
│   │   ├── components/       # 公共组件
│   │   ├── views/            # 页面视图
│   │   ├── router/           # 路由配置
│   │   ├── utils/            # 工具函数
│   │   └── tests/           # 前端测试
│   └── .env                  # 环境变量
├── dist/                     # 构建输出
│   ├── assets/               # 静态资源
│   └── index.html            # 构建后的HTML
├── docs/                     # 文档
│   ├── api-path-guidelines.md # API路径指南
│   ├── api-troubleshooting.md # API问题排查
│   ├── edit.md               # 编辑指南
│   ├── help.md               # 帮助文档
│   ├── test.md               # 测试文档
│   ├── test2.md              # 测试文档2
│   └── test3.md              # 测试文档3
├── electron/                 # Electron配置
│   ├── main.js               # 主进程
│   └── preload.js            # 预加载脚本
├── logs/                     # 日志文件
│   └── app.log               # 应用日志
├── scripts/                  # 脚本
│   └── check-api-paths.js    # API路径检查
├── tests/                    # 测试
│   ├── api-attendance.test.js # 考勤API测试
│   ├── api-availability.test.js # 可用性测试
│   ├── api-employee.test.js  # 员工API测试
│   ├── basic-api.test.js     # 基础API测试
└── data/                     # 数据目录
```

## 开发流程
1. 需求分析和设计：明确项目需求，进行数据库设计和代码结构规划
2. 前端开发：使用Vite搭建前端界面，实现各个功能模块的交互
3. 后端开发：使用Flask和Node.js实现数据导入、薪资计算和数据库管理等功能
4. 应用程序打包：使用Electron将前端和后端代码打包成桌面应用程序
5. 测试和优化：对软件进行测试，修复发现的问题，优化性能
6. 部署和发布：将软件部署到目标环境，提供给用户使用

## 安装与运行

### 开发环境
1. 克隆仓库：`git clone [仓库地址]`
2. 安装依赖：`npm install` 和 `pip install -r backend/requirements.txt`
3. 启动前端开发服务器：`npm run dev`
   - 前端服务器将在5567端口启动
   - 如果端口已被占用，系统会自动结束当前进程并重新启动
   - 这是通过package.json中的`--force`参数实现的
4. 启动后端服务：`python backend/app.py` 或 `node backend/src/index.js`

### 生产环境
1. 构建前端：`npm run build`
2. 打包应用：`npm run electron:build`

## 数据库设计
详见项目文档中的数据库设计部分，包含考勤数据表、员工表、薪资组表、薪酬单项表、社保项表、社保组表和薪资记录表等。
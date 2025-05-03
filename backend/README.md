# HR助手后端服务

## 项目说明
这是HR助手系统的后端服务，使用Node.js + Express + Sequelize构建。

## 功能特性
- 员工管理
- 考勤管理
- 薪资管理
- 用户认证
- 角色权限控制

## 技术栈
- Node.js
- Express
- Sequelize
- SQLite
- JWT认证
- Winston日志

## 开发环境设置

1. 安装依赖
```bash
npm install
```

2. 配置环境变量
创建 `.env` 文件并设置以下变量：
```
PORT=3000
NODE_ENV=development
JWT_SECRET=your-secret-key
DATABASE_URL=sqlite:./data/hr.db
```

3. 初始化数据库
```bash
npm run migrate
npm run seed
```

4. 启动开发服务器
```bash
npm run dev
```

## API文档

### 员工管理
- GET /api/employees - 获取所有员工
- GET /api/employees/:id - 获取单个员工
- POST /api/employees - 创建员工
- PUT /api/employees/:id - 更新员工信息
- DELETE /api/employees/:id - 删除员工

### 考勤管理
- GET /api/attendance - 获取考勤记录
- POST /api/attendance - 记录考勤
- PUT /api/attendance/:id - 更新考勤记录
- POST /api/attendance/import - 批量导入考勤数据

## 测试
```bash
npm test
```

## 部署
1. 设置生产环境变量
2. 构建项目
3. 启动服务
```bash
npm start
``` 
# HR助手项目优化与架构说明

## 1. 技术栈与项目结构

### 1.1 后端项目结构（实际）
```text
backend/
├── src/
│   ├── controllers/    # 控制器
│   ├── models/         # 数据模型
│   ├── services/       # 业务逻辑
│   ├── middleware/     # 中间件（含认证、权限、错误处理）
│   ├── utils/          # 工具函数（如日志）
│   ├── config/         # 配置文件
│   ├── routes/         # 路由
│   ├── database/       # 数据库迁移与种子
│   └── migrations/     # 迁移脚本
├── tests/              # 测试文件（含 Python 和 Node.js 测试）
├── backups/            # 数据库备份
├── logs/               # 日志文件
├── scripts/            # 初始化与自动化脚本
├── data/               # 数据文件
├── package.json        # Node.js 配置
└── README.md           # 项目说明
```

### 1.2 依赖配置（实际）
```json
{
  "dependencies": {
    "bcryptjs": "^2.4.3",
    "cors": "^2.8.5",
    "cron": "^3.1.6",
    "express": "^4.18.2",
    "helmet": "^7.1.0",
    "joi": "^17.11.0",
    "jsonwebtoken": "^9.0.2",
    "moment": "^2.29.4",
    "sequelize": "^6.35.1",
    "sqlite3": "^5.1.6",
    "winston": "^3.11.0"
  },
  "devDependencies": {
    "eslint": "^8.56.0",
    "jest": "^29.7.0",
    "nodemon": "^3.0.2",
    "prettier": "^3.2.4",
    "sequelize-cli": "^6.6.2",
    "supertest": "^6.3.3"
  }
}
```

## 2. 性能优化方案

### 2.1 数据分页实现
```javascript
// Sequelize 分页
const getPaginatedData = async (model, page, pageSize) => {
  const offset = (page - 1) * pageSize;
  const { count, rows } = await model.findAndCountAll({
    offset,
    limit: pageSize
  });
  return { total: count, data: rows };
};
```

## 3. 安全性增强方案

### 3.1 用户认证系统
```javascript
// src/middleware/auth.js
const jwt = require('jsonwebtoken');
const { logger } = require('../utils/logger');

const authMiddleware = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ error: '未提供认证令牌' });
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key');
    req.user = decoded;
    next();
  } catch (error) {
    logger.error('认证失败:', error);
    res.status(401).json({ error: '认证失败' });
  }
};
```

### 3.2 角色权限控制
```javascript
// src/middleware/auth.js
const roleMiddleware = (allowedRoles) => {
  return (req, res, next) => {
    if (!req.user || !req.user.role) {
      return res.status(403).json({ error: '未授权访问' });
    }
    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ error: '权限不足' });
    }
    next();
  };
};
```

## 4. 错误处理与日志

### 4.1 统一错误处理
```javascript
// src/middleware/errorHandler.js
const { logger } = require('../utils/logger');
const errorHandler = (err, req, res, next) => {
  logger.error('ECONNREFUSED 错误:', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method
  });
  const status = err.status || 500;
  const message = err.message || '服务器内部错误';
  res.status(status).json({
    error: {
      status,
      message,
      timestamp: new Date().toISOString()
    }
  });
};
```

### 4.2 日志服务
```javascript
// src/utils/logger.js
const winston = require('winston');
const path = require('path');
const logDir = path.join(__dirname, '../../logs');
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json(),
    winston.format.prettyPrint()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({ filename: path.join(logDir, 'error.log'), level: 'error' }),
    new winston.transports.File({ filename: path.join(logDir, 'combined.log') })
  ]
});
```

## 5. 数据验证

### 5.1 Joi 数据验证
```javascript
const Joi = require('joi');
const validateData = (schema) => {
  return (req, res, next) => {
    const { error } = schema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: '数据校验失败', details: error.details });
    }
    next();
  };
};
```

## 6. 备份与自动化脚本

### 6.1 数据库自动备份
- 备份文件存储于 `backend/backups/` 目录。
- 可通过 Node.js 脚本或定时任务实现自动备份与清理。

## 7. 测试与质量保障

- Python 测试文件位于 `backend/tests/`，Node.js 可用 jest/supertest 进行单元与接口测试。
- 推荐测试命令：
```bash
npm test
```

## 8. 部署与环境

- 推荐使用 Docker 部署，或直接通过 `npm start` 启动。
- 环境变量通过 `.env` 文件配置。

## 9. 监控与运维

- 日志文件存储于 `backend/logs/`，支持 error/combined/resource 等多种日志。
- 可扩展性能监控与错误通知。

## 10. 实施计划与注意事项

1. **第一阶段（1-2周）**
   - 技术栈迁移与结构重组
   - 基础框架搭建
2. **第二阶段（2-3周）**
   - 安全性增强、错误处理、数据验证
3. **第三阶段（2-3周）**
   - 性能优化、测试覆盖率提升、文档完善
4. **第四阶段（1-2周）**
   - 部署、监控、备份机制

### 注意事项
- 实施过程中需保持现有系统正常运行
- 每阶段后需充分测试
- 建议渐进式迁移，定期代码审查与沟通
- 建立完善的回滚与备份机制 
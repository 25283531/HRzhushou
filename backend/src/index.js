const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { errorHandler } = require('./middleware/errorHandler');
const { logger } = require('./utils/logger');
const routes = require('./routes');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 根路由
app.get('/', (req, res) => {
  res.json({
    message: 'HR助手API服务',
    version: '1.0.0',
    endpoints: '/api'
  });
});

// API路由
app.use('/api', routes);

// 错误处理
app.use(errorHandler);

// 启动服务器
app.listen(PORT, () => {
  logger.info(`服务器运行在端口 ${PORT}`);
});

module.exports = app; 
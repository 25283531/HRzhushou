const { logger } = require('../utils/logger');

const errorHandler = (err, req, res, next) => {
  logger.error('错误处理中间件捕获到错误:', {
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

module.exports = { errorHandler }; 
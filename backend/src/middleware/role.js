const { logger } = require('../utils/logger');

const checkRole = (roles) => {
  return (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({ error: '未认证' });
      }

      if (!roles.includes(req.user.role)) {
        return res.status(403).json({ error: '权限不足' });
      }

      next();
    } catch (error) {
      logger.error('角色检查失败:', error);
      res.status(500).json({ error: '服务器错误' });
    }
  };
};

module.exports = { checkRole }; 
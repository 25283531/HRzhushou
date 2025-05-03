const { sequelize, syncModels } = require('../models');
const { logger } = require('../utils/logger');

const migrate = async () => {
  try {
    // 同步所有模型到数据库
    await syncModels();
    logger.info('数据库迁移成功');
  } catch (error) {
    logger.error('数据库迁移失败:', error);
    process.exit(1);
  }
};

migrate(); 
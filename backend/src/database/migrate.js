const { sequelize } = require('../config/database');
const fs = require('fs').promises;
const path = require('path');

async function migrate() {
  try {
    // 确保数据目录存在
    const dataDir = path.join(__dirname, '../../data');
    try {
      await fs.access(dataDir);
    } catch (error) {
      await fs.mkdir(dataDir, { recursive: true });
    }

    // 运行迁移
    const employeeMigrations = require('./migrations/001_create_employees');
    const salaryGroupMigrations = require('./migrations/002_create_salary_groups');

    await employeeMigrations.up(sequelize.getQueryInterface(), sequelize);
    await salaryGroupMigrations.up(sequelize.getQueryInterface(), sequelize);
    
    console.log('数据库迁移完成。');
    process.exit(0);
  } catch (error) {
    console.error('数据库迁移失败:', error);
    process.exit(1);
  }
}

migrate(); 
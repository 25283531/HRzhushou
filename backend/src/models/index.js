const { sequelize } = require('../config/database');
const Employee = require('./employee');
const Attendance = require('./attendance');
const Salary = require('./salary');

// 同步所有模型
const syncModels = async () => {
  try {
    // 使用force: true来重新创建表
    await sequelize.sync({ force: true });
    console.log('所有模型同步成功');
  } catch (error) {
    console.error('模型同步失败:', error);
    process.exit(1);
  }
};

module.exports = {
  sequelize,
  Employee,
  Attendance,
  Salary,
  syncModels
}; 
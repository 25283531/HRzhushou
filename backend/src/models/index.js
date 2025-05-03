const { sequelize } = require('../config/database');
const Employee = require('./employee');
const Attendance = require('./attendance');
const Salary = require('./salary');

// 同步所有模型
const syncModels = async () => {
  try {
    await sequelize.sync();
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
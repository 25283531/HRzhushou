const { Sequelize } = require('sequelize');
const path = require('path');

// 创建 Sequelize 实例
const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: path.join(__dirname, '../../data/hr.db'),
  logging: false, // 开发环境可以设置为 console.log
  define: {
    timestamps: true,
    underscored: true,
    underscoredAll: true,
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
});

// 测试数据库连接
const testConnection = async () => {
  try {
    await sequelize.authenticate();
    console.log('数据库连接成功。');
  } catch (error) {
    console.error('数据库连接失败:', error);
  }
};

// 导出
module.exports = {
  sequelize,
  testConnection
}; 
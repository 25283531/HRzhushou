const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');
const Employee = require('./employee');

const Salary = sequelize.define('Salary', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  employeeId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: Employee,
      key: 'id'
    }
  },
  month: {
    type: DataTypes.DATEONLY,
    allowNull: false
  },
  baseSalary: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false
  },
  bonus: {
    type: DataTypes.DECIMAL(10, 2),
    defaultValue: 0
  },
  deduction: {
    type: DataTypes.DECIMAL(10, 2),
    defaultValue: 0
  },
  tax: {
    type: DataTypes.DECIMAL(10, 2),
    defaultValue: 0
  },
  netSalary: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false
  },
  status: {
    type: DataTypes.ENUM('待发放', '已发放', '已取消'),
    defaultValue: '待发放'
  },
  remark: {
    type: DataTypes.STRING
  }
});

// 建立关联关系
Salary.belongsTo(Employee, { foreignKey: 'employeeId' });
Employee.hasMany(Salary, { foreignKey: 'employeeId' });

module.exports = Salary; 
const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');
const Employee = require('./employee');

const Attendance = sequelize.define('Attendance', {
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
  date: {
    type: DataTypes.DATEONLY,
    allowNull: false
  },
  checkIn: {
    type: DataTypes.TIME,
    allowNull: true
  },
  checkOut: {
    type: DataTypes.TIME,
    allowNull: true
  },
  status: {
    type: DataTypes.ENUM('正常', '迟到', '早退', '缺勤', '请假'),
    defaultValue: '正常'
  },
  remark: {
    type: DataTypes.STRING,
    allowNull: true
  }
}, {
  timestamps: true,
  tableName: 'attendance'
});

// 建立关联关系
Attendance.belongsTo(Employee, { foreignKey: 'employeeId' });
Employee.hasMany(Attendance, { foreignKey: 'employeeId' });

module.exports = Attendance; 
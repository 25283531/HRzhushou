const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Employee = sequelize.define('Employee', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  employee_number: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true
  },
  id_card_number: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true
  },
  department_level1: {
    type: DataTypes.STRING,
    allowNull: false
  },
  department_level2: {
    type: DataTypes.STRING,
    allowNull: true,
    defaultValue: ''
  },
  position: {
    type: DataTypes.STRING,
    allowNull: true,
    defaultValue: ''
  },
  entry_date: {
    type: DataTypes.DATEONLY,
    allowNull: false
  },
  leave_date: {
    type: DataTypes.DATEONLY,
    allowNull: true
  },
  status: {
    type: DataTypes.ENUM('在职', '离职', '试用期'),
    defaultValue: '在职'
  },
  salary_group: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: null
  },
  social_security_group: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: null
  },
  bank_account: {
    type: DataTypes.STRING,
    allowNull: true,
    defaultValue: ''
  },
  phone: {
    type: DataTypes.STRING,
    allowNull: true,
    defaultValue: ''
  },
  remarks: {
    type: DataTypes.TEXT,
    allowNull: true,
    defaultValue: ''
  }
}, {
  tableName: 'employees',
  timestamps: true,
  underscored: true,
  createdAt: 'created_at',
  updatedAt: 'updated_at'
});

module.exports = Employee; 
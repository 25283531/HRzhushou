const { DataTypes } = require('sequelize');

module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.createTable('employees', {
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
        allowNull: true
      },
      position: {
        type: DataTypes.STRING,
        allowNull: false
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
        type: DataTypes.STRING,
        allowNull: true
      },
      social_security_group: {
        type: DataTypes.STRING,
        allowNull: true
      },
      bank_account: {
        type: DataTypes.STRING,
        allowNull: true
      },
      phone: {
        type: DataTypes.STRING,
        allowNull: true
      },
      remarks: {
        type: DataTypes.TEXT,
        allowNull: true
      },
      created_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP')
      },
      updated_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP')
      }
    }, {
      indexes: [
        {
          unique: true,
          fields: ['employee_number'],
          name: 'employees_employee_number_unique'
        },
        {
          unique: true,
          fields: ['id_card_number'],
          name: 'employees_id_card_number_unique'
        }
      ]
    });
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.dropTable('employees');
  }
}; 
'use strict';

module.exports = {
  up: async (queryInterface, Sequelize) => {
    // 先检查表是否存在，如果不存在则创建
    await queryInterface.createTable('employees', {
      id: {
        type: Sequelize.INTEGER,
        primaryKey: true,
        autoIncrement: true
      },
      name: {
        type: Sequelize.STRING,
        allowNull: false
      },
      employee_number: {
        type: Sequelize.STRING,
        allowNull: false,
        unique: true
      },
      id_card_number: {
        type: Sequelize.STRING,
        allowNull: false,
        unique: true
      },
      department_level1: {
        type: Sequelize.STRING,
        allowNull: false
      },
      department_level2: {
        type: Sequelize.STRING,
        allowNull: true
      },
      position: {
        type: Sequelize.STRING,
        allowNull: false
      },
      entry_date: {
        type: Sequelize.DATEONLY,
        allowNull: false
      },
      leave_date: {
        type: Sequelize.DATEONLY,
        allowNull: true
      },
      status: {
        type: Sequelize.ENUM('在职', '离职', '试用期'),
        defaultValue: '在职'
      },
      salary_group: {
        type: Sequelize.INTEGER,
        allowNull: true
      },
      social_security_group: {
        type: Sequelize.INTEGER,
        allowNull: true
      },
      bank_account: {
        type: Sequelize.STRING,
        allowNull: true
      },
      phone: {
        type: Sequelize.STRING,
        allowNull: true
      },
      remarks: {
        type: Sequelize.TEXT,
        allowNull: true
      },
      created_at: {
        type: Sequelize.DATE,
        allowNull: false
      },
      updated_at: {
        type: Sequelize.DATE,
        allowNull: false
      }
    }).catch(error => {
      if (error.name === 'SequelizeUniqueConstraintError') {
        console.log('Table already exists, continuing with migration...');
      } else {
        throw error;
      }
    });

    // 修改salary_group和social_security_group字段类型为INTEGER
    await queryInterface.changeColumn('employees', 'salary_group', {
      type: Sequelize.INTEGER,
      allowNull: true
    });

    await queryInterface.changeColumn('employees', 'social_security_group', {
      type: Sequelize.INTEGER,
      allowNull: true
    });

    // 更新现有数据，将字符串转换为整数
    await queryInterface.sequelize.query(`
      UPDATE employees 
      SET salary_group = CAST(salary_group AS INTEGER)
      WHERE salary_group IS NOT NULL AND salary_group != '';
    `);

    await queryInterface.sequelize.query(`
      UPDATE employees 
      SET social_security_group = CAST(social_security_group AS INTEGER)
      WHERE social_security_group IS NOT NULL AND social_security_group != '';
    `);
  },

  down: async (queryInterface, Sequelize) => {
    // 回滚时将字段类型改回STRING
    await queryInterface.changeColumn('employees', 'salary_group', {
      type: Sequelize.STRING,
      allowNull: true
    });

    await queryInterface.changeColumn('employees', 'social_security_group', {
      type: Sequelize.STRING,
      allowNull: true
    });
  }
}; 
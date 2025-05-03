const { DataTypes } = require('sequelize');

module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.createTable('salary_items', {
      id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
      },
      group_id: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
          model: 'salary_groups',
          key: 'id'
        },
        onUpdate: 'CASCADE',
        onDelete: 'CASCADE'
      },
      name: {
        type: DataTypes.STRING,
        allowNull: false
      },
      amount: {
        type: DataTypes.DECIMAL(10, 2),
        allowNull: false,
        defaultValue: 0
      },
      type: {
        type: DataTypes.ENUM('收入', '支出'),
        defaultValue: '收入'
      },
      description: {
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
    });

    // 添加联合唯一索引
    await queryInterface.addIndex('salary_items', ['group_id', 'name'], {
      unique: true,
      name: 'salary_items_group_id_name_unique'
    });
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.dropTable('salary_items');
  }
}; 
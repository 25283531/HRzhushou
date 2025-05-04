const path = require('path');
const { sequelize } = require('./database');

module.exports = {
  development: {
    username: sequelize.config.username,
    password: sequelize.config.password,
    database: sequelize.config.database,
    host: sequelize.config.host,
    dialect: 'sqlite',
    storage: sequelize.config.storage,
    migrationStorageTableName: 'sequelize_meta',
    migrations: {
      directory: path.join(__dirname, '../migrations')
    }
  }
}; 
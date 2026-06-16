const { config } = require('dotenv');
config();
const path = require('path');

const {
  DB_DIALECT,
  DB_STORAGE
} = process.env;

module.exports = {
  dialect: DB_DIALECT || 'sqlite',
  storage: path.resolve(__dirname, DB_STORAGE || '../../../sv-fs.sqlite'),
  migrationStorageTableName: 'sequelize_migrations',
  seederStorageTableName: 'sequelize_seeds',
};

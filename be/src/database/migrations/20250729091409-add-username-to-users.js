'use strict';

module.exports = {
  async up(queryInterface, Sequelize) {
    await queryInterface.addColumn('users', 'username', {
      type: Sequelize.STRING,
      allowNull: true, 
    });

    await queryInterface.sequelize.query(`
      CREATE UNIQUE INDEX IF NOT EXISTS users_username_unique ON users (username)
    `);
  },

  async down(queryInterface, Sequelize) {
    await queryInterface.removeColumn('users', 'username');
  }
};

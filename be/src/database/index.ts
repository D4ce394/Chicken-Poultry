import { Sequelize } from 'sequelize';
import logger from '@/utils/logger';
import userModel from './models/user.model';
import roleModel from './models/role.model';
import monitoringModel from './models/monitoring.model';
import alertModel from './models/alert.model';
import recordingModel from './models/recording.model';
import { NODE_ENV } from '@/config';
import path from 'path';

const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: process.env.SQLITE_PATH || path.resolve(__dirname, '../../../sv-fs.sqlite'),
        logging: NODE_ENV === 'development'
        ? (query, time) => logger.info(`${time}ms ${query}`)
        : false,
    benchmark: true,
    define: {
        charset: 'utf8mb4',
        collate: 'utf8mb4_general_ci',
        underscored: true,
        freezeTableName: true,
    },
});

export const DB = {
    Users: userModel(sequelize),
    Roles: roleModel(sequelize),
    Monitoring: monitoringModel(sequelize),
    Alerts: alertModel(sequelize),
    Recordings: recordingModel(sequelize),
    sequelize,
    Sequelize,
};

DB.Users.belongsTo(DB.Roles, { foreignKey: 'role_id', as: 'role' });
DB.Recordings.belongsTo(DB.Monitoring, { foreignKey: 'camera_id', as: 'camera' });

(async () => {
    try {
        await sequelize.authenticate();
        logger.info('SQLite database connected ✅');

        await sequelize.sync({ alter: true });
        logger.info('Tables synced ✅');

        await seedDefaultData();
    } catch (error) {
        logger.error('Database init failed ❌', error);
    }
})();

async function seedDefaultData() {
    const bcrypt = await import('bcrypt');

    // Seed role admin
    const [adminRole] = await DB.Roles.findOrCreate({
        where: { name: 'admin' },
        defaults: {
            name: 'admin',
            description: 'Administrator with full access',
            permissions: JSON.stringify(['all']),
        } as any,
    });

    // Seed user admin default
    const existing = await DB.Users.findOne({ where: { email: 'admin@admin.com' } });
    if (!existing) {
        const hashed = await bcrypt.hash('Admin123!', 10);
        await DB.Users.create({
            name: 'Admin',
            email: 'admin@admin.com',
            username: 'admin',
            password: hashed,
            role_id: adminRole.get('id'),
            isApproved: true,
            department: 'IT',
            isOnline: false,
        } as any);
        logger.info('Default admin user created ✅ (admin@admin.com / Admin123!)');
    }
}

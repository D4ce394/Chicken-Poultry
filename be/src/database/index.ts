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
    storage: path.resolve(__dirname, '../../../sv-fs.sqlite'),
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

(async () => {
    try {
        await sequelize.authenticate();
        logger.info('SQLite database connected ✅');
    } catch (error) {
        logger.error('Unable to connect to SQLite ❌', error);
    }
})();

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

import { DataTypes, Sequelize, Model, Optional } from 'sequelize';

export interface MonitoringAttributes {
    id: number;
    name: string;
    isOnline: boolean;
    streamUrl: string;
    location: string;
    ipAddress: string;  
    lastUpdated: Date;  
    createdAt?: Date;
    updatedAt?: Date;
}

export type MonitoringCreationAttributes = Optional<MonitoringAttributes, 'id' | 'createdAt' | 'updatedAt' | 'lastUpdated'>;

export default (sequelize: Sequelize) => {
    class Monitoring extends Model<MonitoringAttributes, MonitoringCreationAttributes>
        implements MonitoringAttributes {
        public id!: number;
        public name!: string;
        public isOnline!: boolean;
        public streamUrl!: string;
        public location!: string;
        public ipAddress!: string;
        public lastUpdated!: Date;
        public createdAt?: Date;
        public updatedAt?: Date;
    }

    Monitoring.init(
        {
            id: {
                type: DataTypes.INTEGER,
                autoIncrement: true,
                primaryKey: true,
            },
            name: {
                type: DataTypes.STRING,
                allowNull: false,
            },
            isOnline: {
                type: DataTypes.BOOLEAN,
                field: 'is_online',
                allowNull: false,
            },
            streamUrl: {
                type: DataTypes.STRING,
                field: 'stream_url',
                allowNull: false,
            },
            location: {
                type: DataTypes.STRING,
                allowNull: true,
            },
            ipAddress: { 
                type: DataTypes.STRING,
                field: 'ip_address',
                allowNull: true,
            },
            lastUpdated: { 
                type: DataTypes.DATE,
                field: 'last_updated',
                allowNull: true,
            },
        },
        {
            sequelize,
            tableName: 'monitoring_feeds',
            timestamps: true,
            createdAt: 'created_at',
            updatedAt: 'updated_at',
        }
    );

    return Monitoring;
};

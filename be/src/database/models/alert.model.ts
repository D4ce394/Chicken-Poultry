import { DataTypes, Sequelize, Model, Optional } from 'sequelize';

export interface AlertAttributes {
    id: number;
    title: string;
    createdAt: Date; 
    location: string;
    type: string;
    isResolved: boolean;
    
}

export type AlertCreationAttributes = Optional<AlertAttributes, 'id' | 'createdAt' | 'isResolved'>;

export default (sequelize: Sequelize) => {
    class Alert extends Model<AlertAttributes, AlertCreationAttributes>
        implements AlertAttributes {
        public id!: number;
        public title!: string;
        public createdAt!: Date;
        public location!: string;
        public type!: string;
        public isResolved!: boolean;
    }

    Alert.init(
        {
            id: {
                type: DataTypes.INTEGER,
                autoIncrement: true,
                primaryKey: true,
            },
            title: {
                type: DataTypes.STRING,
                allowNull: false,
            },
            createdAt: {
                type: DataTypes.DATE,
                field: 'timestamp', 
                allowNull: false,
            },
            location: {
                type: DataTypes.STRING,
                allowNull: false,
            },
            type: {
                type: DataTypes.STRING,
                allowNull: false,
            },
            isResolved: { 
                type: DataTypes.BOOLEAN,
                field: 'is_resolved', 
                allowNull: false,
                defaultValue: false,
            },
        },
        {
            sequelize,
            tableName: 'alerts', 
            timestamps: true, 
            createdAt: 'created_at', 
            updatedAt: 'updated_at', 
        }
    );

    return Alert;
};
import { DataTypes, Sequelize, Model, Optional } from 'sequelize';
import type { MonitoringFeed } from '$../../interfaces/monitoring.interfaces';

export interface RecordingAttributes {
    id: number;
    camera_id: number;
    eventType: string;
    filePath: string;
    startTime: Date;
    endTime: Date;
    duration: string;
    personName?: string;
    camera?: MonitoringFeed;
}


export type RecordingCreationAttributes = Optional<RecordingAttributes, 'id'>;

export default (sequelize: Sequelize) => {
    class Recording extends Model<RecordingAttributes, RecordingCreationAttributes>
        implements RecordingAttributes {
        public id!: number;
        public camera_id!: number;
        public eventType!: string;
        public filePath!: string;
        public startTime!: Date;
        public endTime!: Date;
        public duration!: string;
        public personName?: string;
    }

    Recording.init(
        {
            id: {
                type: DataTypes.INTEGER,
                autoIncrement: true,
                primaryKey: true,
            },
            camera_id: {
                type: DataTypes.INTEGER,
                allowNull: false,
            },
            eventType: {
                type: DataTypes.STRING,
                field: 'event_type',
                allowNull: false,
            },
            filePath: {
                type: DataTypes.STRING,
                field: 'file_path',
                allowNull: false,
            },
            startTime: {
                type: DataTypes.DATE,
                field: 'start_time',
                allowNull: false,
            },
            endTime: {
                type: DataTypes.DATE,
                field: 'end_time',
                allowNull: false,
            },
            duration: {
                type: DataTypes.STRING,
                allowNull: false,
            },
            personName: {
                type: DataTypes.STRING,
                field: 'person_name',
                allowNull: true,
            },
        },
        {
            sequelize,
            tableName: 'recordings',
            timestamps: true,
            createdAt: 'created_at',
            updatedAt: false, 
        }
    );

    return Recording;
};

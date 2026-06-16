import { DB } from '@/database';
import { Op } from 'sequelize';
import type { MonitoringAttributes } from '@/database/models/monitoring.model';
import type { RecordingAttributes } from '@/database/models/recording.model';

export const getMonitoringFeedsFromDB = async () => {
    return DB.Monitoring.findAll();
};

export const getStreamsFromDB = async () => {
    const rows = await DB.Monitoring.findAll({ attributes: ['streamUrl'] });
    return rows.map((r: { streamUrl: string }) => r.streamUrl);
};

export const getLiveAlertsFromDB = async () => {
    return DB.Alerts.findAll({
        where: { isResolved: false },
        order: [['createdAt', 'DESC']],
        limit: 10
    });
};

export const getRecordingListFromDB = async (
    personName: string = '',
    cameraName: string = '',
    date: Date | null = null
): Promise<RecordingAttributes[]> => {
    let whereCondition: any = {};
    let includeOptions: any[] = [];

    if (personName && personName.trim() !== '') {
        whereCondition.personName = { [Op.iLike]: `%${personName.trim()}%` };
    }

    const monitoringIncludeOption: any = {
        model: DB.Monitoring,
        as: 'camera',
        attributes: ['name', 'streamUrl'],
    };

    if (cameraName && cameraName.trim() !== '') {
        monitoringIncludeOption.where = { name: { [Op.iLike]: `%${cameraName.trim()}%` } };
        monitoringIncludeOption.required = true;
    }
    includeOptions.push(monitoringIncludeOption);

    if (date) {
        const startOfDay = new Date(date);
        startOfDay.setHours(0, 0, 0, 0);
        const endOfDay = new Date(date);
        endOfDay.setHours(23, 59, 59, 999);

        whereCondition.startTime = {
            [Op.between]: [startOfDay, endOfDay]
        };
    }

    const recordings = await DB.Recordings.findAll({
        where: whereCondition,
        include: includeOptions,
        order: [['startTime', 'DESC']],
    });

    return recordings.map(rec => rec.toJSON() as RecordingAttributes);
};

export const getCameraStatusForDashboard = async () => {
    const totalCameras = await DB.Monitoring.count();
    const onlineCameras = await DB.Monitoring.count({ where: { isOnline: true } });
    const offlineCameras = await DB.Monitoring.count({ where: { isOnline: false } });

    return { totalCameras, onlineCameras, offlineCameras };
};
import { DB } from '@/database';
import { Op } from 'sequelize'; 

export const getLiveAlertsFromDB = async () => {
    return DB.Alerts.findAll({
        where: { isResolved: false },
        order: [['createdAt', 'DESC']],
        limit: 10
    });
};

export const getAlertHistoryFromDB = async (
    typeFilter: string = '',
    locationFilter: string = '',
    dateRangeFilter: string = ''
) => {
    let whereCondition: any = {};

    if (typeFilter && typeFilter.trim() !== '') {
        whereCondition.type = typeFilter.trim();
    }

    if (locationFilter && locationFilter.trim() !== '') {
        whereCondition.location = locationFilter.trim();
    }

    if (dateRangeFilter) {
        const now = new Date();
        let startDate: Date;

        switch (dateRangeFilter) {
            case 'Yesterday':
                startDate = new Date(now);
                startDate.setDate(now.getDate() - 1);
                startDate.setHours(0, 0, 0, 0); 
                whereCondition.createdAt = { [Op.gte]: startDate };
                break;
            case 'Last 7 Days':
                startDate = new Date(now);
                startDate.setDate(now.getDate() - 7);
                whereCondition.createdAt = { [Op.gte]: startDate };
                break;
            case 'Last 30 Days':
                startDate = new Date(now);
                startDate.setDate(now.getDate() - 30);
                whereCondition.createdAt = { [Op.gte]: startDate };
                break;
        }
    }

    return DB.Alerts.findAll({
        where: whereCondition,
        order: [['createdAt', 'DESC']] 
    });
};

export const getAlertsTodayCount = async () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const count = await DB.Alerts.count({
        where: {
            createdAt: { [Op.gte]: today }
        }
    });

    return count;
};

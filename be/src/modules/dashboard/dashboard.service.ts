import { DB } from '@/database';
import { Op, literal } from 'sequelize';
import type { SystemHealthData } from '@/interfaces/dashboard.interfaces';


export const getSecurityIncidentsData = async () => {
    try {
        const incidentsByType = await DB.Alerts.findAll({
            attributes: [
                ['type', 'name'],
                [literal('COUNT("type")'), 'data'],
            ],
            where: {
                createdAt: {
                    [Op.gte]: literal(`DATE('now', '-30 days')`)
                }
            },
            group: ['type'],
            raw: true
        });

        const series = incidentsByType.map((incident: any) => ({
            name: incident.name,
            data: [incident.data] 
        }));
        const labels = incidentsByType.map((incident: any) => incident.name);

        return {
            options: {
                chart: { type: 'bar' as const },
                series: series,
                xaxis: { categories: labels },
                legend: {
                    position: 'top' as 'top',
                    horizontalAlign: 'left' as 'left',
                },
            }
        };
    } catch (error) {
        console.error('Failed to get security incidents data:', error);
        return null;
    }
};

export const getIncidentsByLocationData = async () => {
    try {
        const incidentsByLocation = await DB.Alerts.findAll({
            attributes: [
                ['location', 'label'],
                [literal('COUNT("location")'), 'value'],
            ],
            group: ['location'],
            raw: true
        });

        const series = incidentsByLocation.map((item: any) => item.value);
        const labels = incidentsByLocation.map((item: any) => item.label);
        
        return {
            options: {
                chart: { type: 'pie' as const },
                series: series,
                labels: labels,
                legend: {
                    position: 'bottom' as 'bottom',
                    horizontalAlign: 'center' as 'center',
                },
            },
        };
    } catch (error) {
        console.error('Failed to get incidents by location data:', error);
        return null;
    }
};

export const getSystemHealthData = async (): Promise<SystemHealthData[]> => {
    return [
        { label: "CPU Usage", color: 'success', percentage: 45 },
        { label: "Memory Usage", color: 'brand', percentage: 60 },
        { label: "Storage Space", color: 'success', percentage: 75 },
        { label: "Network Traffic", color: 'brand', percentage: 30 }
    ];
};

export const getCameraStatusForDashboard = async () => {
    try {
        const totalCameras = await DB.Monitoring.count();
        const onlineCameras = await DB.Monitoring.count({ where: { isOnline: true } });
        const offlineCameras = await DB.Monitoring.count({ where: { isOnline: false } });

        return { totalCameras, onlineCameras, offlineCameras };
    } catch (error) {
        console.error('Failed to get camera status data:', error);
        return { totalCameras: 0, onlineCameras: 0, offlineCameras: 0 };
    }
};

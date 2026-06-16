import { api } from "$lib/axios";
import type { DashboardResponse, DashboardStats, SystemHealthData  } from '$lib/interfaces/dashboard.interfaces';
import type { MonitoringFeed } from '$lib/interfaces/monitoring.interfaces';
import type { LiveAlert } from '$lib/interfaces/alert.interfaces';

export const fetchDashboardData = async (): Promise<DashboardResponse> => {
    try {
        const [
            monitoringFeedsRes,
            recentAlertsRes
        ] = await Promise.all([
            api.get('/monitoring/feeds'), 
            api.get('/alerts/live')
        ]);

        const allCameras: MonitoringFeed[] = monitoringFeedsRes.data.data;
        const recentAlerts: LiveAlert[] = recentAlertsRes.data.data;

        const totalCameras = allCameras.length;
        const onlineCameras = allCameras.filter(cam => cam.isOnline).length;
        const offlineCameras = totalCameras - onlineCameras;

        // masih data dummy untuk Attendance dan Blacklist 
        const attendancesToday = 30; 
        const alertsToday = recentAlerts.length; 
        const blacklistDetections = 0; 

        const cameraStatusChartData = {
            options: {
                chart: { type: 'donut' as const },
                series: [onlineCameras, offlineCameras, totalCameras - onlineCameras - offlineCameras],
                labels: ['Online', 'Offline', 'Maintenance'],
                legend: {
                    position: 'bottom' as 'bottom',
                    horizontalAlign: 'center' as 'center',
                },
            }
        };

        const incidentsChartData = {
            options: {
                chart: { type: 'pie' as const },
                series: [44, 55, 13, 43, 22],
                labels: ['Front Gate', 'Lobby', 'Parking Lot', 'Warehouse', 'Server Room'],
                legend: {
                    position: 'bottom' as 'bottom',
                    horizontalAlign: 'center' as 'center',
                },
            },
        };

        const activityTimelineChartData = {
            options: {
                chart: { type: 'line' as const },
                series: [{ name: 'Events', data: [10, 20, 15, 30, 25, 40] }],
                xaxis: { categories: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] },
                legend: {
                    position: 'top' as 'top',
                    horizontalAlign: 'left' as 'left',
                },
            }
        };
        
        // Data dummy untuk system health
        const systemHealthData: SystemHealthData[] = [
            { label: "CPU Usage", color: 'success', percentage: 45 },
            { label: "Memory Usage", color: 'brand', percentage: 60 },
            { label: "Storage Space", color: 'success', percentage: 75 },
            { label: "Network Traffic", color: 'brand', percentage: 30 }
        ];

        const stats: DashboardStats = {
            totalCameras: totalCameras,
            attendancesToday: attendancesToday,
            alertsToday: alertsToday,
            blacklistDetections: blacklistDetections,
            onlineCameras: onlineCameras,
            offlineCameras: offlineCameras
        };

        return {
            stats,
            recentAlerts: recentAlerts,
            charts: {
                cameraStatus: cameraStatusChartData,
                incidentsByLocation: incidentsChartData,
                securityIncidents: activityTimelineChartData
            },
            locations: allCameras, 
            systemHealth: systemHealthData 
        };
    } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        return {
            stats: {
                totalCameras: 0,
                attendancesToday: 0,
                alertsToday: 0,
                blacklistDetections: 0,
                onlineCameras: 0,
                offlineCameras: 0
            },
            recentAlerts: [],
            charts: {
                cameraStatus: null,
                incidentsByLocation: null,
                securityIncidents: null
            },
            locations: [],
            systemHealth: []
        };
    }
};

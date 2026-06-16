import { Router } from 'express';
import { getMonitoringFeedsFromDB } from '@/modules/monitoring/monitoring.service';
import { getLiveAlertsFromDB } from '@/modules/alert/alert.service';
import { getAttendancesTodayCount, getBlacklistDetectionCount } from '@/modules/user/user.service';
import { getIncidentsByLocationData, getSecurityIncidentsData, getSystemHealthData } from './dashboard.service';

const router = Router();

router.get('/', async (req, res) => {
    try {
        const monitoringFeeds = await getMonitoringFeedsFromDB();
        const recentAlerts = await getLiveAlertsFromDB();
        const attendanceData = await getAttendancesTodayCount();
        const blacklistCount = await getBlacklistDetectionCount();

        const cameraStatusChartData = {
            options: {
                chart: { type: 'donut' as const },
                series: [
                    monitoringFeeds.filter(cam => cam.isOnline).length,
                    monitoringFeeds.filter(cam => !cam.isOnline).length,
                    0, // Asumsi 0 kamera dalam maintenance untuk saat ini
                ],
                labels: ['Online', 'Offline', 'Maintenance'],
                legend: {
                    position: 'bottom' as 'bottom',
                    horizontalAlign: 'center' as 'center',
                },
            }
        };

        const incidentsByLocationData = {
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

        const securityIncidentsData = {
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
        
        const systemHealthData = [
            { label: "CPU Usage", color: 'success', percentage: 45 },
            { label: "Memory Usage", color: 'brand', percentage: 60 },
            { label: "Storage Space", color: 'success', percentage: 75 },
            { label: "Network Traffic", color: 'brand', percentage: 30 }
        ];

        const dashboardData = {
            stats: {
                totalCameras: monitoringFeeds.length,
                attendancesToday: attendanceData,
                alertsToday: recentAlerts.length,
                blacklistDetections: blacklistCount,
                onlineCameras: monitoringFeeds.filter(cam => cam.isOnline).length,
                offlineCameras: monitoringFeeds.filter(cam => !cam.isOnline).length,
            },
            recentAlerts: recentAlerts,
            charts: {
                cameraStatus: cameraStatusChartData,
                incidentsByLocation: incidentsByLocationData,
                securityIncidents: securityIncidentsData
            },
            locations: monitoringFeeds,
            systemHealth: systemHealthData
        };

        res.json({ data: dashboardData });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

export default router;

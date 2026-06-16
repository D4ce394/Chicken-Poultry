import type { LiveAlert } from './alert.interfaces';
import type { MonitoringFeed } from './monitoring.interfaces';

export interface DashboardStats {
    totalCameras: number;
    attendancesToday: number;
    alertsToday: number;
    blacklistDetections: number;
    onlineCameras: number;
    offlineCameras: number;
}

export interface DashboardResponse {
    stats: DashboardStats;
    recentAlerts: LiveAlert[];
    charts: {
        cameraStatus: any;
        incidentsByLocation: any;
        securityIncidents: any;
    };
    locations: MonitoringFeed[];
    systemHealth: SystemHealthData[];
}

export interface SystemHealthData {
    label: string;
    color: string;
    percentage: number;
}

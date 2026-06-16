import type { MonitoringFeed } from '$lib/interfaces/monitoring.interfaces';

export interface RecordingData {
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
import { api } from "$lib/axios";
import type { RecordingData } from '$lib/interfaces/recording.interfaces';
import type { MonitoringFeed } from '$lib/interfaces/monitoring.interfaces';

export const getRecordingList = async (
    personName: string = '',
    cameraName: string = '',
    date: Date | null = null
): Promise<RecordingData[]> => {
    try {
        const params = new URLSearchParams();
        if (personName) params.append('personName', personName);
        if (cameraName) params.append('cameraName', cameraName);
        if (date) params.append('date', date.toISOString());

        const queryString = params.toString();
        const url = `/monitoring/recordings${queryString ? `?${queryString}` : ''}`;

        const res = await api.get(url);
        return res.data.data;
    } catch (error) {
        console.error('Failed to fetch recording list:', error);
        return [];
    }
};

export const getCamerasForPlayback = async (): Promise<MonitoringFeed[]> => {
    try {
        const res = await api.get('/monitoring/feeds'); 
        return res.data.data;
    } catch (error) {
        console.error('Failed to fetch cameras for playback:', error);
        return [];
    }
};

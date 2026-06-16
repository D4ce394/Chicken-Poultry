import { api } from "$lib/axios";
import type { LiveAlert } from '$lib/interfaces/alert.interfaces'; 
import type { MonitoringFeed } from '$lib/interfaces/monitoring.interfaces'; 

export const getAlertHistory = async (
    typeFilter: string = '',
    locationFilter: string = '',
    dateRangeFilter: string = ''
): Promise<LiveAlert[]> => {
    try {
        const params = new URLSearchParams();
        if (typeFilter) params.append('typeFilter', typeFilter);
        if (locationFilter) params.append('locationFilter', locationFilter);
        if (dateRangeFilter) params.append('dateRangeFilter', dateRangeFilter);

        const queryString = params.toString();
        const url = `/alerts/history${queryString ? `?${queryString}` : ''}`; 

        const res = await api.get(url);
        return res.data.data; 
    } catch (error) {
        console.error('Failed to fetch alert history:', error);
        return [];
    }
};

export const getMonitoringLocations = async (): Promise<MonitoringFeed[]> => {
    try {
        const res = await api.get('/monitoring'); 
        return res.data.data;
    } catch (error) {
        console.error('Failed to fetch monitoring locations:', error);
        return [];
    }
};

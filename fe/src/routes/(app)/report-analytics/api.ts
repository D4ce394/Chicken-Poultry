import { api } from "$lib/axios";
import type { AttendanceReportData } from '$lib/interfaces/report.interfaces';
import type { MonitoringFeed } from '$lib/interfaces/monitoring.interfaces'; 

// Fungsi untuk mengambil laporan kehadiran dengan filter
export const getAttendanceReport = async (
    locationFilter: string = '',
    dateRangeFilter: string = ''
): Promise<AttendanceReportData[]> => {
    try {
        const params = new URLSearchParams();
        if (locationFilter) params.append('locationFilter', locationFilter);
        if (dateRangeFilter) params.append('dateRangeFilter', dateRangeFilter);

        const queryString = params.toString();
        const url = `/users/attendance-report${queryString ? `?${queryString}` : ''}`;

        const res = await api.get(url);
        return res.data.data; 
    } catch (error) {
        console.error('Failed to fetch attendance report:', error);
        return [];
    }
};

// Fungsi untuk mendapatkan semua lokasi monitoring (untuk dropdown lokasi)
export const getMonitoringLocationsForReports = async (): Promise<MonitoringFeed[]> => {
    try {
        const res = await api.get('/monitoring'); 
        return res.data.data;
    } catch (error) {
        console.error('Failed to fetch monitoring locations for reports:', error);
        return [];
    }
};

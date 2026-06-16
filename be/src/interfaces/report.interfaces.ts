export interface AttendanceReportData {
    id: string; 
    name: string;
    department: string;
    checkIn: string; 
    checkOut: string; 
    duration: string; 
    status: string; // Status kehadiran (e.g., "Present", "Late", "Absent")
}

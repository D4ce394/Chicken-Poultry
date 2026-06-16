import { repo } from './user.repo';
import { CustomError } from '@/utils/custom-error';
import { verifyJWT } from '@/middlewares/jwt.service';
import { JWT_ACCESS_TOKEN_SECRET } from '@/config';
import type { User } from '@/interfaces/user.interfaces';
import type { AttendanceReportData } from '@/interfaces/report.interfaces'; 
import { DB } from '@/database'; 


export const getUserProfileService = async (accessToken: string): Promise<User> => {
    const decodeToken = await verifyJWT(
        accessToken,
        JWT_ACCESS_TOKEN_SECRET as string,
    );

    const userId = decodeToken.userId;

    const user = await repo.getUserProfile(userId);
    if (!user) {
        throw new CustomError('User not found', 404);
    }

    return user;
};

export const getAllUsersService = async (
    accessToken: string,
    search: string = '',
    roleFilter: string = '',
    statusFilter: 'Online' | 'Offline' | '' = '',
    approvalFilter: 'Approved' | 'Pending' | '' = ''
): Promise<User[]> => {
    await verifyJWT(
        accessToken,
        JWT_ACCESS_TOKEN_SECRET as string,
    );

    const users = await repo.getAllUsers(search, roleFilter, statusFilter, approvalFilter);
    return users;
};

export const getAttendanceReportFromDB = async (
    locationFilter: string = '',
    dateRangeFilter: string = ''
): Promise<AttendanceReportData[]> => {

    const users = await repo.getUsersForAttendanceReport(locationFilter, dateRangeFilter);

    return users.map(user => {
        const checkInTime = '08:55 AM';
        const checkOutTime = '05:00 PM';
        const duration = '9hrs 10mins';
        const status = user.isOnline ? 'Present' : 'Absent'; 

        return {
            id: user.id,
            name: user.name || 'N/A',
            department: user.department || 'N/A',
            checkIn: checkInTime,
            checkOut: checkOutTime,
            duration: duration,
            status: status
        };
    });
};

export const getAttendancesTodayCount = async () => {
    const count = await DB.Users.count({ where: { isOnline: true } });
    return count;
};

export const getBlacklistDetectionCount = async () => {
    return 3;
};
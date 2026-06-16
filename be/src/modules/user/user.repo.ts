import { DB } from '@/database';
import { Op } from 'sequelize';
import type { User, UserCreationData } from '@/interfaces/user.interfaces'; 

export const repo = {
    getUserProfile: async (userId: string | undefined): Promise<User | null> => {
        if (!userId) return null;
        const user = await DB.Users.findByPk(userId, {
            include: [{ model: DB.Roles, as: 'role' }],
        });

        if (!user) return null;

        return user.toJSON() as User;
    },

    getAllUsers: async (
        search: string = '',
        roleFilter: string = '',
        statusFilter: 'Online' | 'Offline' | '' = '',
        approvalFilter: 'Approved' | 'Pending' | '' = ''
    ): Promise<User[]> => {
        let whereCondition: any = {};
        let includeOptions: any[] = [];

        const roleIncludeOption: any = {
            model: DB.Roles,
            as: 'role',
        };

        if (roleFilter && roleFilter.trim() !== '') {
            roleIncludeOption.where = {
                name: roleFilter.trim()
            };
            roleIncludeOption.required = true;
        }
        includeOptions.push(roleIncludeOption);

        if (search && search.trim() !== '') {
            whereCondition[Op.or] = [
                { name: { [Op.like]: `%${search.trim()}%` } },
                { email: { [Op.like]: `%${search.trim()}%` } },
                { username: { [Op.like]: `%${search.trim()}%` } },
                { department: { [Op.like]: `%${search.trim()}%` } },
            ];
        }

        if (statusFilter) {
            whereCondition.isOnline = statusFilter === 'Online';
        }

        if (approvalFilter) {
            whereCondition.isApproved = approvalFilter === 'Approved';
        }

        const users = await DB.Users.findAll({
            where: whereCondition,
            include: includeOptions,
            order: [['created_at', 'DESC']]
        });

        return users.map(user => user.toJSON() as User);
    },

    getUsersForAttendanceReport: async (
        locationFilter: string = '',
        dateRangeFilter: string = ''
    ): Promise<User[]> => {
        let whereCondition: any = {};
        let startDate: Date | undefined; 


        if (locationFilter && locationFilter.trim() !== '') {
            whereCondition.location = locationFilter.trim(); 
        }

        if (dateRangeFilter) {
            const now = new Date();
            switch (dateRangeFilter) {
                case 'Last 7 Days':
                    startDate = new Date(now);
                    startDate.setDate(now.getDate() - 7);
                    break;
                case 'Last 14 Days':
                    startDate = new Date(now);
                    startDate.setDate(now.getDate() - 14);
                    break;
                case 'Last 30 Days':
                    startDate = new Date(now);
                    startDate.setDate(now.getDate() - 30);
                    break;
                default:
                    break;
            }
            if (startDate) {
                whereCondition.createdAt = { [Op.gte]: startDate };
            }
        }

        const users = await DB.Users.findAll({
            where: whereCondition,
            include: [{ model: DB.Roles, as: 'role' }], 
            order: [['name', 'ASC']] 
        });

        return users.map(user => user.toJSON() as User);
    },

    approveUser: async (userId: string): Promise<[number]> => {
        return await DB.Users.update(
            { isApproved: true, updated_at: new Date() },
            { where: { id: userId } }
        );
    },

    rejectUser: async (userId: string): Promise<number> => {
        return await DB.Users.destroy({ where: { id: userId } });
    },

    createUser: async (userData: any): Promise<User> => {
        const dataToCreate = {
            ...userData,
            isApproved: userData.isApproved ?? false,
            isOnline: userData.isOnline ?? false,
            lastLogin: userData.lastLogin || null,
            department: userData.department || null,
        };
        const createdUser = await DB.Users.create(dataToCreate);
        const userWithRole = await DB.Users.findByPk(createdUser.id, {
            include: [{ model: DB.Roles, as: 'role' }],
        });
        if (!userWithRole) {
            throw new Error('Failed to retrieve newly created user with role data.');
        }
        return userWithRole.toJSON();
    },

    updateUser: async (userId: string, userData: Partial<UserCreationData>): Promise<[number]> => {
        return await DB.Users.update(
            { ...userData, updated_at: new Date() },
            { where: { id: userId } }
        );
    },

    deleteUser: async (userId: string): Promise<number> => {
        return await DB.Users.destroy({ where: { id: userId } });
    },
};

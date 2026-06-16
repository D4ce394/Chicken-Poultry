import { DB } from '@/database';
import type { User, UserCreationData } from '@/interfaces/user.interfaces';

const repo = {
    findUserByEmail: async (email: string): Promise<User | null> => {
        return await DB.Users.findOne({ where: { email } });
    },
      
    createUser: async (userData: UserCreationData): Promise<User> => {
        return await DB.Users.create({
            ...userData,
            isApproved: false 
        } as any);
    }
     
};

export default repo;

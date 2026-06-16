export interface UserDummy {
    name: string;
    email: string;
    role: string;
    department: string;
    isOnline: boolean;
    isApproved: boolean;
    lastLogin: string;
}

export interface RoleDummy {
    name: string;
    description: string;
    users: number;
    permissions: string[];
}
import type { Role } from './role.interfaces'; 

export interface User {
    id: string;
    email: string;
    name: string | null;
    username: string | null;
    password: string;
    isApproved: boolean;
    created_at: Date;
    updated_at: Date;
    roleId: number | null; 
    role?: Role; 
    department: string | null; 
    isOnline: boolean;
    lastLogin: Date | null; 
}

export type UserCreationData = {
    email: string;
    name?: string | null;
    username?: string | null; 
    password: string;
    isApproved?: boolean;
    roleId?: number | null;
    department?: string | null; 
    isOnline?: boolean; 
    lastLogin?: Date | null; 
};




// export interface User {
//     id: string;
//     email: string;
//     name: string | null;
//     username: string | null;
//     password: string;
//     isApproved: boolean;
//     created_at: Date;
//     updated_at: Date;
//     roleId?: number; // ID peran
//     role?: {
//         id: number;
//         name: string;
//     };
//     department?: string;
//     isOnline?: boolean;
//     lastLogin?: Date; 
//   }
  
//   export type UserCreationData = {
//     email: string;
//     name?: string | null;
//     username: string;
//     password: string;
//     isApproved?: boolean;
//   };
  

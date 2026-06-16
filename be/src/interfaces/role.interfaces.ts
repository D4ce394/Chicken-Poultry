  export interface Role {
    id: number;
    name: string;
    description: string;
    permissions: string[];
    created_at: Date;
    updated_at: Date;
}

export type RoleCreationData = {
    name: string;
    description: string;
};
export interface CameraData {
    id: number;
    name: string;
    location: string;
    ipAddress: string; 
    isOnline: boolean; 
    lastUpdated: Date; 
    streamUrl: string; 
    createdAt?: Date;
    updatedAt?: Date;
}

export interface MonitoringFeed {
    id: number;
    name: string;
    isOnline: boolean; 
    streamUrl: string; 
    location: string; 
    createdAt?: Date;
    updatedAt?: Date;
}
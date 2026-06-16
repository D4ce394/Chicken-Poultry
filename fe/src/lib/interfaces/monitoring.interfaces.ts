export interface MonitoringFeed {
            id: number;
            name: string;
            isOnline: boolean;
            streamUrl: string;
            location: string;
            ipAddress: string;  // Ditambahkan
            lastUpdated: Date;  // Ditambahkan
            createdAt?: Date;
            updatedAt?: Date;
        }
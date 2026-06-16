export interface LiveAlert {
    id: number;
    title: string;
    createdAt: Date; 
    location: string;
    type: 'motion' | 'intrusion' | 'camera' | string;
    isResolved: boolean; 
    timeFormatted?: string; 
    icon?: any;
}
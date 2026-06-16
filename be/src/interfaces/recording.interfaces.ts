export interface RecordingAttributes {
    id: number;
    camera_id: number;
    eventType: string;
    filePath: string;
    startTime: Date;
    endTime: Date;
    duration: string;
    personName?: string;
}


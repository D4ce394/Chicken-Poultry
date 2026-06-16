export interface MonitoringDummy {
    name: string;
    isOnline: boolean;
}

export interface FeedGridTab {
    label: string;
    value: number;
    icon: typeof SvelteComponent;
}

export interface CameraControl {
    label: string;
    icon: typeof SvelteComponent;
}
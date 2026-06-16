import type { LiveAlertDummy } from "../alert-notification/types";
import type { CameraControl, FeedGridTab, MonitoringDummy } from "./types";
import { Grid2X2, ArrowDown, ArrowLeft, ArrowRight, ArrowUp, Circle, ZoomIn, ZoomOut, Camera, Info, Footprints, UserRound, Grid3X3 } from '@lucide/svelte';

export const feedGridTabs: FeedGridTab[] = [
    {
        label: '2x2',
        value: 2,
        icon: Grid2X2
    },
    {
        label: '3x3',
        value: 3,
        icon: Grid3X3
    },
    {
        label: '4x4',
        value: 4,
        icon: Grid3X3
    },
];

export const gridClassMap: Record<number, string> = {
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4'
};

export const monitoringDummy: MonitoringDummy[] = [
    {
        name: 'Front Gate',
        isOnline: true
    },
    {
        name: 'Lobby',
        isOnline: true
    },
    {
        name: 'Parking Lot',
        isOnline: true
    },
    {
        name: 'Warehouse',
        isOnline: false
    },
    {
        name: 'Loading Dock',
        isOnline: true
    },
    {
        name: 'Server Room',
        isOnline: true
    },
    {
        name: 'Hallway 1',
        isOnline: true
    },
    {
        name: 'Hallway 2',
        isOnline: true
    },
    {
        name: 'Executive Office',
        isOnline: true
    },
    {
        name: 'Conference Room',
        isOnline: true
    },
];

export const panTiltControls: CameraControl[] = [
    {
        label: 'Stop',
        icon: Circle
    },
    {
        label: 'Pan Up',
        icon: ArrowUp
    },
    {
        label: 'Pan Down',
        icon: ArrowDown
    },
    {
        label: 'Pan Left',
        icon: ArrowLeft
    },
    {
        label: 'Pan Right',
        icon: ArrowRight
    }
];

export const zoomControls: CameraControl[] = [
    {
        label: 'Zoom In',
        icon: ZoomIn
    },
    {
        label: 'Zoom Out',
        icon: ZoomOut
    },
];

export const quickActions: CameraControl[] = [
    {
        label: 'Take Snapshot',
        icon: Camera
    },
    {
        label: 'Trigger Alert',
        icon: Info
    }
];

export const liveAlertDummy: LiveAlertDummy[] = [
    {
        title: 'Motion Detected',
        time: 'Just now',
        location: 'Parking Lot',
        icon: Footprints
    },
    {
        title: 'Unknown Person',
        time: '2 minutes ago',
        location: 'Front Gate',
        icon: UserRound
    },
    {
        title: 'Door Forced Open',
        time: '5 minutes ago',
        location: 'Warehouse',
        icon: Info
    },
    {
        title: 'Camera Offline',
        time: '10 minutes ago',
        location: 'Server Room',
        icon: Camera
    },
    {
        title: 'Suspicious Activity',
        time: '15 minutes ago',
        location: 'Lobby',
        icon: Footprints
    },
    {
        title: 'Fire Alarm',
        time: '20 minutes ago',
        location: 'Loading Dock',
        icon: Info
    },
    {
        title: 'Unauthorized Access',
        time: '25 minutes ago',
        location: 'Executive Office',
        icon: UserRound
    },
    {
        title: 'Glass Break Detected',
        time: '30 minutes ago',
        location: 'Conference Room',
        icon: Info
    },
    {
        title: 'Motion Detected',
        time: '35 minutes ago',
        location: 'Hallway 1',
        icon: Footprints
    },
    {
        title: 'Camera Tampering',
        time: '40 minutes ago',
        location: 'Hallway 2',
        icon: Camera
    }
]

export const presetPositions: string[] = ['Default', 'Entrance', 'Wide Angle', 'Zoom In'];
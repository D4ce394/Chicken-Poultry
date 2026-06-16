import { Bell, ChartBarIncreasing, ClipboardList, Drumstick, LayoutDashboard, Play, Radio, Settings, User, Video } from "@lucide/svelte";
import type { MenuItem } from "./types";

export const singleMenuItems: MenuItem[] = [
    {
        label: 'Dashboard',
        icon: LayoutDashboard,
        link: '/dashboard'
    }
];

export const mainMenuItems: MenuItem[] = [
    {
        label: 'Live Monitoring',
        icon: Radio,
        link: '/live-monitoring'
    },
    {
        label: 'Alert & Notification',
        icon: Bell,
        link: '/alert-notification'
    },
    {
        label: 'Video Playback',
        icon: Play,
        link: '/video-playback'
    },
    {
        label: 'Report & Analytics',
        icon: ChartBarIncreasing,
        link: '/report-analytics'
    },
];

export const masterMenuItems: MenuItem[] = [
    {
        label: 'User',
        icon: User,
        link: '/user'
    },
    {
        label: 'Camera',
        icon: Video,
        link: '/camera'
    },
];

export const poultryMenuItems: MenuItem[] = [
    {
        label: 'Dashboard Ayam',
        icon: Drumstick,
        link: '/chicken-counting'
    },
    {
        label: 'Rekap Counting',
        icon: ClipboardList,
        link: '/chicken-counting/rekap'
    },
    {
        label: 'Konfigurasi',
        icon: Settings,
        link: '/chicken-counting/config'
    },
];

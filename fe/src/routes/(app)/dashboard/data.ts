import type { EventDummy, SystemHealthDummy } from "./types";

export const eventDummy : EventDummy[] = [
    {
        name: "Team Meeting",
        location: "Conference Room A",
        time: "10:00 AM",
        status: "Pending"
    },
    {
        name: "Intrusion Alert",
        location: "Front Gate",
        time: "10:00 AM",
        status: "Alert"
    },
    {
        name: "Face Recognition",
        location: "Lobby",
        time: "10:00 AM",
        status: "Resolved"
    },
    {
        name: "Face Recognition",
        location: "Lobby",
        time: "10:00 AM",
        status: "Resolved"
    },
    {
        name: "Face Recognition",
        location: "Lobby",
        time: "10:00 AM",
        status: "Resolved"
    },
];

export const systemHealthDummy: SystemHealthDummy[] = [
    {
        label: "CPU Usage",
        color: 'success',
        percentage: 45
    },
    {
        label: "Memory Usage",
        color: 'brand',
        percentage: 60
    },
    {
        label: "Storage Space",
        color: 'success',
        percentage: 75
    },
    {
        label: "Network Traffic",
        color: 'brand',
        percentage: 30
    }
];
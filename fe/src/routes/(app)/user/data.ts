import type { RoleDummy, UserDummy } from "./types";

export const userDummy: UserDummy[] = [
    {
        name: "John Doe",
        email: "k2xH0@example.com",
        role: "Admin",
        department: "HR",
        isOnline: true,
        isApproved: true,
        lastLogin: "2 days ago"
    },
    {
        name: "Jane Smith",
        email: "jane.smith@example.com",
        role: "User",
        department: "Finance",
        isOnline: false,
        isApproved: true,
        lastLogin: "5 hours ago"
    },
    {
        name: "Michael Brown",
        email: "michael.brown@example.com",
        role: "Manager",
        department: "IT",
        isOnline: true,
        isApproved: false,
        lastLogin: "1 hour ago"
    },
    {
        name: "Emily Davis",
        email: "emily.davis@example.com",
        role: "User",
        department: "Marketing",
        isOnline: false,
        isApproved: true,
        lastLogin: "3 days ago"
    },
    {
        name: "William Wilson",
        email: "william.wilson@example.com",
        role: "Admin",
        department: "Operations",
        isOnline: true,
        isApproved: true,
        lastLogin: "10 minutes ago"
    },
    {
        name: "Olivia Martinez",
        email: "olivia.martinez@example.com",
        role: "User",
        department: "Sales",
        isOnline: false,
        isApproved: false,
        lastLogin: "7 days ago"
    },
    {
        name: "James Anderson",
        email: "james.anderson@example.com",
        role: "Manager",
        department: "HR",
        isOnline: true,
        isApproved: true,
        lastLogin: "30 minutes ago"
    },
    {
        name: "Sophia Thomas",
        email: "sophia.thomas@example.com",
        role: "User",
        department: "Finance",
        isOnline: false,
        isApproved: true,
        lastLogin: "12 hours ago"
    },
    {
        name: "Benjamin Lee",
        email: "benjamin.lee@example.com",
        role: "Admin",
        department: "IT",
        isOnline: true,
        isApproved: false,
        lastLogin: "4 hours ago"
    },
    {
        name: "Ava Harris",
        email: "ava.harris@example.com",
        role: "User",
        department: "Marketing",
        isOnline: false,
        isApproved: true,
        lastLogin: "6 days ago"
    }
];

export const roleDummy: RoleDummy[] = [
    {
        name: "Admin",
        description: "Full access to all features and settings.",
        users: 5,
        permissions: ["Create", "Read", "Update", "Delete"]
    },
    {
        name: "User",
        description: "Limited access to features.",
        users: 20,
        permissions: ["Read"]
    },
    {
        name: "Manager",
        description: "Access to management features.",
        users: 10,
        permissions: ["Create", "Read", "Update"]
    },
];
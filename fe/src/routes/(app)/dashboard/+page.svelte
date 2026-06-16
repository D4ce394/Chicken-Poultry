<script lang="ts">
    import { onMount } from 'svelte';
    import { createQuery } from '@tanstack/svelte-query';
    import { AlertCircle, Camera, UserCheck, UserX } from '@lucide/svelte';
    import Breadcrumb from '../../../components/breadcrumb/Breadcrumb.svelte';
    import { renderChart } from 'svelte-chart-apex';
    import { fetchDashboardData } from './api';
    import type { DashboardResponse, SystemHealthData } from '$lib/interfaces/dashboard.interfaces';
    import { formatDistanceToNow } from 'date-fns';

    let dashboardData = $state<DashboardResponse | null>(null);

    const dashboardQuery = createQuery({
        queryKey: ['dashboardData'],
        queryFn: async () => {
            return await fetchDashboardData();
        }
    });

    const isLoading = $derived($dashboardQuery.isFetching);

    $effect(() => {
        if ($dashboardQuery.data) {
            dashboardData = $dashboardQuery.data;
        } else if ($dashboardQuery.error) {
            console.error("Failed to fetch dashboard data:", $dashboardQuery.error);
            dashboardData = null;
        }
    });

    const cameraStatusChartData = $derived(
        dashboardData?.charts?.cameraStatus || {
            options: {
                chart: { type: 'donut' as const },
                series: [0, 0, 0],
                labels: ['Online', 'Offline', 'Maintenance'],
                legend: {
                    position: 'bottom' as 'bottom',
                    horizontalAlign: 'center' as 'center',
                },
            }
        }
    );

    const activityTimelineChartData = $derived(
        dashboardData?.charts?.securityIncidents || {
            options: {
                chart: { type: 'line' as const },
                series: [{ name: 'Events', data: [0] }],
                xaxis: { categories: ['N/A'] },
                legend: {
                    position: 'top' as 'top',
                    horizontalAlign: 'left' as 'left',
                },
            }
        }
    );

    onMount(() => {
    });
</script>

<div class="flex flex-col gap-y-6">
    <Breadcrumb pageName="Dashboard" />
    <!-- Dashboard Stats -->
    <div class="grid grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-4 lg:gap-4">
        {#if isLoading}
            <div class="col-span-full text-center py-4">Loading stats...</div>
        {:else if dashboardData}
            <div class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
                <div class="flex items-center gap-x-4">
                    <div class="bg-brand-500 flex h-14 w-14 items-center justify-center rounded-lg">
                        <Camera class="h-6 w-6 text-white" />
                    </div>
                    <div class="flex flex-col">
                        <p class="text-theme-lg font-semibold text-gray-800 dark:text-white/90">{dashboardData.stats.totalCameras}</p>
                        <p class="text-theme-sm text-gray-500 dark:text-white/70">Total Cameras</p>
                    </div>
                </div>
            </div>
            <div class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
                <div class="flex items-center gap-x-4">
                    <div class="bg-success-500 flex h-14 w-14 items-center justify-center rounded-lg">
                        <UserCheck class="h-6 w-6 text-white" />
                    </div>
                    <div class="flex flex-col">
                        <p class="text-theme-lg font-semibold text-gray-800 dark:text-white/90">{dashboardData.stats.attendancesToday}</p>
                        <p class="text-theme-sm text-gray-500 dark:text-white/70">Attendances Today</p>
                    </div>
                </div>
            </div>
            <div class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
                <div class="flex items-center gap-x-4">
                    <div class="bg-error-500 flex h-14 w-14 items-center justify-center rounded-lg">
                        <AlertCircle class="h-6 w-6 text-white" />
                    </div>
                    <div class="flex flex-col">
                        <p class="text-theme-lg font-semibold text-gray-800 dark:text-white/90">{dashboardData.stats.alertsToday}</p>
                        <p class="text-theme-sm text-gray-500 dark:text-white/70">Alerts Today</p>
                    </div>
                </div>
            </div>
            <div class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
                <div class="flex items-center gap-x-4">
                    <div class="bg-brand-500 flex h-14 w-14 items-center justify-center rounded-lg">
                        <UserX class="h-6 w-6 text-white" />
                    </div>
                    <div class="flex flex-col">
                        <p class="text-theme-lg font-semibold text-gray-800 dark:text-white/90">{dashboardData.stats.blacklistDetections}</p>
                        <p class="text-theme-sm text-gray-500 dark:text-white/70">Blacklist Detection</p>
                    </div>
                </div>
            </div>
        {:else}
            <div class="col-span-full text-center py-4 text-gray-500">Failed to load dashboard data.</div>
        {/if}
    </div>
    <!-- Chart -->
    <div class="grid grid-cols-12 gap-4">
        <!-- Chart Security Incidents -->
        <div
            class="col-span-full rounded-2xl border border-gray-200 bg-white md:col-span-6 lg:col-span-7 dark:border-gray-800 dark:bg-white/[0.03]"
        >
            <div
                class="flex flex-col gap-y-4 border-b border-gray-100 px-6 py-3 lg:flex-row lg:items-center lg:justify-between dark:border-gray-800"
            >
                <h3 class="text-base font-medium text-gray-800 dark:text-white/90">
                    Activity Timeline
                </h3>
                <div class="flex flex-wrap items-center gap-x-2 gap-y-2">
                    <button class="btn-secondary-outline-md" aria-label="tabButton"> Today </button>
                    <button class="btn-secondary-outline-md" aria-label="tabButton"> Weekly </button>
                    <button class="btn-secondary-outline-md" aria-label="tabButton"> Monthly </button>
                </div>
            </div>
            <div use:renderChart={activityTimelineChartData}></div>
        </div>
        <!-- Chart Incidents -->
        <div
            class="col-span-full rounded-2xl border border-gray-200 bg-white md:col-span-6 lg:col-span-5 dark:border-gray-800 dark:bg-white/[0.03]"
        >
            <div
                class="flex flex-col gap-y-4 border-b border-gray-100 px-6 py-5 lg:flex-row lg:items-center lg:justify-between dark:border-gray-800"
            >
                <h3 class="text-base font-medium text-gray-800 dark:text-white/90">
                    Camera Status
                </h3>
            </div>
            <div use:renderChart={cameraStatusChartData}></div>
        </div>
    </div>
    <!-- Event & System -->
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <!-- Event -->
        <div
            class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
        >
            <div
                class="flex flex-col gap-y-4 border-b border-gray-100 px-6 py-3 lg:flex-row lg:items-center lg:justify-between dark:border-gray-800"
            >
                <h3 class="text-base font-medium text-gray-800 dark:text-white/90">Recent Events</h3>
                <div class="flex flex-wrap items-center gap-x-2 gap-y-2">
                    <a href="/alert-notification" class="btn-secondary-outline-md" aria-label="tabButton">
                        View All
                    </a>
                </div>
            </div>
            <!-- Table -->
            <div class="max-w-full overflow-x-auto px-6 py-5">
                <table class="min-w-full">
                    <!-- Table Header -->
                    <thead class="border-b border-gray-100 dark:border-white/[0.05]">
                        <tr>
                            <th class="px-5 py-3 sm:px-6">
                                <div class="flex items-center">
                                    <p class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">#</p>
                                </div>
                            </th>
                            <th class="px-5 py-3 sm:px-6">
                                <div class="flex items-center">
                                    <p class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">Name</p>
                                </div>
                            </th>
                            <th class="px-5 py-3 sm:px-6">
                                <div class="flex items-center">
                                    <p class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">Location</p>
                                </div>
                            </th>
                            <th class="px-5 py-3 sm:px-6">
                                <div class="flex items-center">
                                    <p class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">Time</p>
                                </div>
                            </th>
                            <th class="px-5 py-3 sm:px-6">
                                <div class="flex items-center">
                                    <p class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">Status</p>
                                </div>
                            </th>
                        </tr>
                    </thead>
                    <!-- Table Header -->
                    <!-- Table Body -->
                    <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                        {#if dashboardData && dashboardData.recentAlerts.length > 0}
                            {#each dashboardData.recentAlerts.slice(0, 5) as event, index}
                                <tr>
                                    <td class="px-5 py-4 sm:px-6">
                                        <div class="flex items-center">
                                            <p class="text-theme-sm text-gray-500 dark:text-gray-400">
                                                {index + 1}
                                            </p>
                                        </div>
                                    </td>
                                    <td class="px-5 py-4 sm:px-6">
                                        <div class="flex items-center">
                                            <p class="text-theme-sm text-gray-500 dark:text-gray-400">
                                                {event.title}
                                            </p>
                                        </div>
                                    </td>
                                    <td class="px-5 py-4 sm:px-6">
                                        <div class="flex items-center">
                                            <p class="text-theme-sm text-gray-500 dark:text-gray-400">
                                                {event.location}
                                            </p>
                                        </div>
                                    </td>
                                    <td class="px-5 py-4 sm:px-6">
                                        <div class="flex items-center">
                                            <p class="text-theme-sm text-gray-500 dark:text-gray-400">
                                                {formatDistanceToNow(new Date(event.createdAt), { addSuffix: true })}
                                            </p>
                                        </div>
                                    </td>
                                    <td class="px-5 py-4 sm:px-6">
                                        <div class="flex items-center">
                                            <p class={`text-theme-sm ${event.isResolved ? 'text-success-500' : 'text-error-500'}`}>
                                                {event.isResolved ? 'Resolved' : 'Pending'}
                                            </p>
                                        </div>
                                    </td>
                                </tr>
                            {/each}
                        {:else}
                            <tr>
                                <td colspan="5" class="px-6 py-4 text-gray-500 text-center">
                                    No recent events found.
                                </td>
                            </tr>
                        {/if}
                    </tbody>
                    <!-- Table Body -->
                </table>
            </div>
        </div>
        <!-- System -->
        <div
            class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
        >
            <div
                class="flex flex-col gap-y-4 border-b border-gray-100 px-6 py-5 lg:flex-row lg:items-center lg:justify-between dark:border-gray-800"
            >
                <h3 class="text-base font-medium text-gray-800 dark:text-white/90">System Health</h3>
            </div>
            <div class="px-6 py-5">
                <div class="flex flex-col gap-y-4">
                    {#if dashboardData?.systemHealth}
                        {#each dashboardData.systemHealth as health}
                            <div class="flex flex-col gap-y-3">
                                <div class="flex items-center justify-between">
                                    <p class="text-theme-md font-medium text-gray-800">{health.label}</p>
                                    <p class="text-theme-sm text-gray-800">{health.percentage}%</p>
                                </div>
                                <div class="relative h-3 w-full rounded-full bg-gray-200 dark:bg-gray-800">
                                    <div
                                        class={`bg-${health.color}-500 absolute left-0 h-full rounded-full`}
                                        style="width: {health.percentage}%"
                                    ></div>
                                </div>
                            </div>
                        {/each}
                    {:else}
                        <div class="py-4 text-center text-gray-500">Failed to load system health data.</div>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div>

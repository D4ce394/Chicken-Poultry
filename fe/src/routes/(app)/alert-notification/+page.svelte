<script lang="ts">
    import { onMount } from 'svelte';
    import { Check, ChevronDown, ChevronLeft, ChevronRight, Clock, Download, Filter, MapPin, Maximize, RefreshCcw, Save } from '@lucide/svelte';
    import Breadcrumb from '../../../components/breadcrumb/Breadcrumb.svelte';
    import { getAlertHistory, getMonitoringLocations } from './api';
    import type { LiveAlert } from '$lib/interfaces/alert.interfaces';
    import type { MonitoringFeed } from '$lib/interfaces/monitoring.interfaces';
    import { queryClient } from '$lib/queryClient'; 
    import { AlertCircle } from 'lucide-svelte';
    import { slide } from 'svelte/transition'; 


    let openAlertFilters = $state(false);
    let selectedAlertType: string = $state('');
    let selectedLocationFilter: string = $state('');
    let selectedDateRange: string = $state('');

    let alertHistoryData: LiveAlert[] = $state([]);
    let monitoringLocations: MonitoringFeed[] = $state([]); 

    let isLoadingHistory = $state(false);

    let checkboxMotion = $state(false);
    let checkboxFace = $state(false);
    let checkboxIntrusion = $state(false);
    let checkboxUnattended = $state(false);
    let checkboxInApp = $state(false);
    let checkboxEmail = $state(false);
    let checkboxSMS = $state(false);
    let checkboxSound = $state(false);


    function formatAlertTime(date: Date): string {
        const d = new Date(date);
        return `${d.toLocaleDateString()} ${d.toLocaleTimeString()}`;
    }

    async function loadAlertHistory() {
        isLoadingHistory = true;
        try {
            const history = await getAlertHistory(
                selectedAlertType,
                selectedLocationFilter,
                selectedDateRange
            );
            alertHistoryData = history.map(alert => ({
                ...alert,
                timeFormatted: formatAlertTime(new Date(alert.createdAt))
            }));
        } catch (error) {
            console.error('Failed to load alert history:', error);
            alertHistoryData = []; 
        } finally {
            isLoadingHistory = false;
        }
    }

    async function loadMonitoringLocations() {
        try {
            const locations = await getMonitoringLocations();
            const uniqueLocations = Array.from(new Set(locations.map(loc => loc.location)))
                                        .map(location => ({ location: location } as MonitoringFeed)); 
            monitoringLocations = uniqueLocations;
        } catch (error) {
            console.error('Failed to load monitoring locations:', error);
            monitoringLocations = [];
        }
    }

    async function applyFilters() {
        openAlertFilters = false;
        await loadAlertHistory(); 
    }

    async function resetFilters() {
        selectedAlertType = '';
        selectedLocationFilter = '';
        selectedDateRange = '';
        openAlertFilters = false;
        await loadAlertHistory(); 
    }

    async function refreshAlerts() {
        await loadAlertHistory();
    }

    onMount(async () => {
        await loadMonitoringLocations(); 
        await loadAlertHistory(); 
    });
</script>

<div class="flex flex-col gap-y-6">
    <Breadcrumb pageName="Alert & Notification" />
    <!-- Alert History -->
    <div
        class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
    >
        <div
            class="flex flex-col gap-y-2 border-b border-gray-100 px-6 py-4 md:flex-row md:items-center md:justify-between dark:border-gray-800"
        >
            <h3 class="text-base font-medium text-gray-800 dark:text-white/90">Alert History</h3>
            <div class="flex items-center gap-x-2">
                <button aria-label="exportButton" class="btn-primary-sm">
                    <Download class="h-4 w-4" />
                    Export
                </button>
                <button aria-label="refreshButton" class="btn-primary-sm" onclick={refreshAlerts}>
                    <RefreshCcw class="h-4 w-4" />
                    Refresh
                </button>
                <div class="relative inline-block">
                    <button
                        onclick={() => (openAlertFilters = !openAlertFilters)}
                        aria-label="filterButton"
                        class="btn-primary-outline-sm"
                    >
                        <Filter class="h-4 w-4" />
                        Filters
                    </button>
                    {#if openAlertFilters}
                        <div class="dropdown" transition:slide>
                            <ul class="flex flex-col gap-y-2">
                                <!-- Alert Types -->
                                <li class="form-groups">
                                    <span class="form-label">Alert Type</span>
                                    <div class="relative z-20 bg-transparent">
                                        <select bind:value={selectedAlertType} class="select-input">
                                            <option value="" class="text-gray-700 dark:bg-gray-900 dark:text-gray-400">Select option</option>
                                            {#each ['motion', 'intrusion', 'camera'] as option} 
                                                <option
                                                    value={option}
                                                    class="text-gray-700 dark:bg-gray-900 dark:text-gray-400"
                                                >
                                                    {option}
                                                </option>
                                            {/each}
                                        </select>
                                        <span
                                            class="pointer-events-none absolute top-1/2 right-4 z-30 -translate-y-1/2 text-gray-500 dark:text-gray-400"
                                        >
                                            <ChevronDown class="h-5 w-5" />
                                        </span>
                                    </div>
                                </li>
                                <!-- Location -->
                                <li class="form-groups">
                                    <span class="form-label">Location</span>
                                    <div class="relative z-20 bg-transparent">
                                        <select bind:value={selectedLocationFilter} class="select-input">
                                            <option value="" class="text-gray-700 dark:bg-gray-900 dark:text-gray-400">Select option</option>
                                            {#each monitoringLocations as locationOption}
                                                <option
                                                    value={locationOption.location}
                                                    class="text-gray-700 dark:bg-gray-900 dark:text-gray-400"
                                                >
                                                    {locationOption.location}
                                                </option>
                                            {/each}
                                        </select>
                                        <span
                                            class="pointer-events-none absolute top-1/2 right-4 z-30 -translate-y-1/2 text-gray-500 dark:text-gray-400"
                                        >
                                            <ChevronDown class="h-5 w-5" />
                                        </span>
                                    </div>
                                </li>
                                <!-- Date Range -->
                                <li class="form-groups">
                                    <span class="form-label">Date Range</span>
                                    <div class="relative z-20 bg-transparent">
                                        <select bind:value={selectedDateRange} class="select-input">
                                            <option value="" class="text-gray-700 dark:bg-gray-900 dark:text-gray-400">Select option</option>
                                            {#each ['Yesterday', 'Last 7 Days', 'Last 30 Days'] as option}
                                                <option
                                                    value={option}
                                                    class="text-gray-700 dark:bg-gray-900 dark:text-gray-400"
                                                >
                                                    {option}
                                                </option>
                                            {/each}
                                        </select>
                                        <span
                                            class="pointer-events-none absolute top-1/2 right-4 z-30 -translate-y-1/2 text-gray-500 dark:text-gray-400"
                                        >
                                            <ChevronDown class="h-5 w-5" />
                                        </span>
                                    </div>
                                </li>
                                <!-- Apply & Reset Buttons -->
                                <li class="mt-4 flex flex-col justify-end lg:flex-row gap-x-2">
                                    <button class="btn-secondary-md" onclick={resetFilters}>
                                        Reset
                                    </button>
                                    <button class="btn-primary-md" onclick={applyFilters}>
                                        <Filter class="h-4 w-4" />
                                        Apply Filters
                                    </button>
                                </li>
                            </ul>
                        </div>
                    {/if}
                </div>
            </div>
        </div>
        <div class="flex flex-col gap-y-4 px-6 py-5 lg:gap-y-6">
            <!-- Data -->
            <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
                {#if isLoadingHistory}
                    <div class="col-span-full py-4 text-center text-gray-500">Loading alert history...</div>
                {:else if alertHistoryData.length === 0}
                    <div class="col-span-full py-4 text-center text-gray-500">No alert history found.</div>
                {:else}
                    {#each alertHistoryData as liveAlert}
                        <div
                            class="hover:bg-brand-50 w-full rounded-lg bg-gray-100/70 px-6 py-5 transition duration-300"
                        >
                            <div class="flex flex-col gap-y-4 lg:flex-row lg:items-center lg:justify-between">
                                <div class="flex items-center gap-x-3">
                                    <div class="bg-brand-500 flex h-11 w-11 items-center justify-center rounded-full">
                                        <!-- Pastikan liveAlert.icon sudah ada dan merupakan komponen Svelte -->
                                        {#if liveAlert.icon}
                                            <svelte:component this={liveAlert.icon} class="h-6 w-6 text-white" />
                                        {:else}
                                            <AlertCircle class="h-6 w-6 text-white" /> <!-- Fallback icon -->
                                        {/if}
                                    </div>
                                    <div class="flex flex-col gap-y-1">
                                        <p class="text-theme-md font-medium text-gray-800">{liveAlert.title}</p>
                                        <div class="flex items-center gap-x-4">
                                            <div class="flex items-center gap-x-1">
                                                <Clock class="h-4 w-4 text-gray-400" />
                                                <span class="text-theme-sm text-gray-400">{liveAlert.timeFormatted}</span>
                                            </div>
                                            <div class="flex items-center gap-x-1">
                                                <MapPin class="h-4 w-4 text-gray-400" />
                                                <span class="text-theme-sm text-gray-400">{liveAlert.location}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="flex items-center gap-x-2">
                                    <button
                                        aria-label="checkButton"
                                        class="btn-secondary-icon"
                                    >
                                        <Check class="h-4 w-4" />
                                    </button>
                                    <button
                                        aria-label="maximizeButton"
                                        class="btn-secondary-icon"
                                    >
                                        <Maximize class="h-4 w-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    {/each}
                {/if}
            </div>
            <!-- Pagination -->
            <div class="flex flex-col items-center gap-y-4 lg:flex-row lg:justify-between">
                <span class="text-theme-sm text-gray-400">Showing 10 to 10 of {alertHistoryData.length} entries</span>
                <div class="flex items-center gap-x-3">
                    <button aria-label="previousButton" class="btn-secondary-icon">
                        <ChevronLeft class="h-5 w-5" />
                    </button>
                    <div class="flex items-center gap-x-1">
                        <button
                            aria-label="pageButton"
                            class="pagination-page text-brand-500 bg-blue-500/[0.08]">1</button
                        >
                        <button aria-label="pageButton" class="pagination-page">2</button>
                    </div>
                    <button aria-label="nextButton" class="btn-secondary-icon">
                        <ChevronRight class="h-5 w-5" />
                    </button>
                </div>
                <div class="flex items-center gap-x-2">
                    <span class="text-theme-sm text-gray-400">rows per page</span>
                    <div class="relative z-20 bg-transparent">
                        <select class="select-input">
                            {#each [10, 20, 30, 40, 50] as perRows}
                                <option value={perRows} class="text-gray-700 dark:bg-gray-900 dark:text-gray-400">
                                    {perRows}
                                </option>
                            {/each}
                        </select>
                        <span
                            class="pointer-events-none absolute top-1/2 right-4 z-30 -translate-y-1/2 text-gray-500 dark:text-gray-400"
                        >
                            <ChevronDown class="h-5 w-5" />
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Notification Settings -->
    <div
        class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
    >
        <div
            class="flex flex-col gap-y-2 border-b border-gray-100 px-6 py-5 md:flex-row md:items-center md:justify-between dark:border-gray-800"
        >
            <h3 class="text-base font-medium text-gray-800 dark:text-white/90">Notification Settings</h3>
        </div>
        <div class="flex flex-col gap-y-6 px-6 py-5">
            <div class="grid grid-cols-1 gap-y-4 lg:grid-cols-2 lg:gap-x-8">
                <!-- Alert Types -->
                <div class="flex flex-col gap-y-4">
                    <p class="text-theme-md font-medium text-gray-800">Alert Types</p>
                    <div class="flex flex-col gap-y-4">
                        <!-- Motion Detection -->
                        <div class="flex items-center justify-between">
                            <label
                                for="checkboxMotion"
                                class="flex cursor-pointer items-center text-sm font-medium text-gray-700 select-none dark:text-gray-400"
                            >
                                <div class="relative">
                                    <input
                                        type="checkbox"
                                        id="checkboxMotion"
                                        class="sr-only"
                                        bind:checked={checkboxMotion}
                                    />
                                    <div
                                        class={`hover:border-brand-500 dark:hover:border-brand-500 mr-3 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] ${checkboxMotion ? 'border-brand-500 bg-brand-500' : 'border-gray-300 bg-transparent dark:border-gray-700'}`}
                                    >
                                        <span class={checkboxMotion ? '' : 'opacity-0'}>
                                            <Check class="h-4 w-4 text-white" />
                                        </span>
                                    </div>
                                </div>
                                Motion Detection
                            </label>
                            <div class="relative z-20 bg-transparent">
                                <select class="select-input">
                                    <option value="" class="text-gray-700 dark:bg-gray-900 dark:text-gray-400">Select option</option>
                                    {#each ['Medium', 'Low', 'High'] as option}
                                        <option
                                            value={option}
                                            class="text-gray-700 dark:bg-gray-900 dark:text-gray-400"
                                        >
                                            {option}
                                        </option>
                                    {/each}
                                </select>
                                <span
                                    class="pointer-events-none absolute top-1/2 right-4 z-30 -translate-y-1/2 text-gray-500 dark:text-gray-400"
                                >
                                    <ChevronDown class="h-5 w-5" />
                                </span>
                            </div>
                        </div>
                        <!-- Face Recognition -->
                        <div class="flex items-center justify-between">
                            <label
                                for="checkboxFace"
                                class="flex cursor-pointer items-center text-sm font-medium text-gray-700 select-none dark:text-gray-400"
                            >
                                <div class="relative">
                                    <input
                                        type="checkbox"
                                        id="checkboxFace"
                                        class="sr-only"
                                        bind:checked={checkboxFace}
                                    />
                                    <div
                                        class={`hover:border-brand-500 dark:hover:border-brand-500 mr-3 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] ${checkboxFace ? 'border-brand-500 bg-brand-500' : 'border-gray-300 bg-transparent dark:border-gray-700'}`}
                                    >
                                        <span class={checkboxFace ? '' : 'opacity-0'}>
                                            <Check class="h-4 w-4 text-white" />
                                        </span>
                                    </div>
                                </div>
                                Face Recognition
                            </label>
                            <div class="relative z-20 bg-transparent">
                                <select class="select-input">
                                    <option value="" class="text-gray-700 dark:bg-gray-900 dark:text-gray-400">Select option</option>
                                    {#each ['Medium', 'Low', 'High'] as option}
                                        <option
                                            value={option}
                                            class="text-gray-700 dark:bg-gray-900 dark:text-gray-400"
                                        >
                                            {option}
                                        </option>
                                    {/each}
                                </select>
                                <span
                                    class="pointer-events-none absolute top-1/2 right-4 z-30 -translate-y-1/2 text-gray-500 dark:text-gray-400"
                                >
                                    <ChevronDown class="h-5 w-5" />
                                </span>
                            </div>
                        </div>
                        <!-- Intrusion Detection -->
                        <div class="flex items-center justify-between">
                            <label
                                for="checkboxIntrusion"
                                class="flex cursor-pointer items-center text-sm font-medium text-gray-700 select-none dark:text-gray-400"
                            >
                                <div class="relative">
                                    <input
                                        type="checkbox"
                                        id="checkboxIntrusion"
                                        class="sr-only"
                                        bind:checked={checkboxIntrusion}
                                    />
                                    <div
                                        class={`hover:border-brand-500 dark:hover:border-brand-500 mr-3 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] ${checkboxIntrusion ? 'border-brand-500 bg-brand-500' : 'border-gray-300 bg-transparent dark:border-gray-700'}`}
                                    >
                                        <span class={checkboxIntrusion ? '' : 'opacity-0'}>
                                            <Check class="h-4 w-4 text-white" />
                                        </span>
                                    </div>
                                </div>
                                Intrusion Detection
                            </label>
                            <div class="relative z-20 bg-transparent">
                                <select class="select-input">
                                    <option value="" class="text-gray-700 dark:bg-gray-900 dark:text-gray-400">Select option</option>
                                    {#each ['Medium', 'Low', 'High'] as option}
                                        <option
                                            value={option}
                                            class="text-gray-700 dark:bg-gray-900 dark:text-gray-400"
                                        >
                                            {option}
                                        </option>
                                    {/each}
                                </select>
                                <span
                                    class="pointer-events-none absolute top-1/2 right-4 z-30 -translate-y-1/2 text-gray-500 dark:text-gray-400"
                                >
                                    <ChevronDown class="h-5 w-5" />
                                </span>
                            </div>
                        </div>
                        <!-- Unattended Object -->
                        <div class="flex items-center justify-between">
                            <label
                                for="checkboxUnattended"
                                class="flex cursor-pointer items-center text-sm font-medium text-gray-700 select-none dark:text-gray-400"
                            >
                                <div class="relative">
                                    <input
                                        type="checkbox"
                                        id="checkboxUnattended"
                                        class="sr-only"
                                        bind:checked={checkboxUnattended}
                                    />
                                    <div
                                        class={`hover:border-brand-500 dark:hover:border-brand-500 mr-3 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] ${checkboxUnattended ? 'border-brand-500 bg-brand-500' : 'border-gray-300 bg-transparent dark:border-gray-700'}`}
                                    >
                                        <span class={checkboxUnattended ? '' : 'opacity-0'}>
                                            <Check class="h-4 w-4 text-white" />
                                        </span>
                                    </div>
                                </div>
                                Unattended Object
                            </label>
                            <div class="relative z-20 bg-transparent">
                                <select class="select-input">
                                    <option value="" class="text-gray-700 dark:bg-gray-900 dark:text-gray-400">Select option</option>
                                    {#each ['Medium', 'Low', 'High'] as option}
                                        <option
                                            value={option}
                                            class="text-gray-700 dark:bg-gray-900 dark:text-gray-400"
                                        >
                                            {option}
                                        </option>
                                    {/each}
                                </select>
                                <span
                                    class="pointer-events-none absolute top-1/2 right-4 z-30 -translate-y-1/2 text-gray-500 dark:text-gray-400"
                                >
                                    <ChevronDown class="h-5 w-5" />
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- Notification Methods -->
                <div class="flex flex-col gap-y-4">
                    <p class="text-theme-md font-medium text-gray-800">Notification Methods</p>
                    <div class="flex flex-col gap-y-4">
                        <!-- In-App Notifications -->
                        <label
                            for="checkboxInApp"
                            class="flex cursor-pointer items-center text-sm font-medium text-gray-700 select-none dark:text-gray-400"
                        >
                            <div class="relative">
                                <input
                                    type="checkbox"
                                    id="checkboxInApp"
                                    class="sr-only"
                                    bind:checked={checkboxInApp}
                                />
                                <div
                                    class={`hover:border-brand-500 dark:hover:border-brand-500 mr-3 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] ${checkboxInApp ? 'border-brand-500 bg-brand-500' : 'border-gray-300 bg-transparent dark:border-gray-700'}`}
                                >
                                    <span class={checkboxInApp ? '' : 'opacity-0'}>
                                        <Check class="h-4 w-4 text-white" />
                                    </span>
                                </div>
                            </div>
                            In-App Notifications
                        </label>
                        <!-- Email Notifications -->
                        <label
                            for="checkboxEmail"
                            class="flex cursor-pointer items-center text-sm font-medium text-gray-700 select-none dark:text-gray-400"
                        >
                            <div class="relative">
                                <input
                                    type="checkbox"
                                    id="checkboxEmail"
                                    class="sr-only"
                                    bind:checked={checkboxEmail}
                                />
                                <div
                                    class={`hover:border-brand-500 dark:hover:border-brand-500 mr-3 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] ${checkboxEmail ? 'border-brand-500 bg-brand-500' : 'border-gray-300 bg-transparent dark:border-gray-700'}`}
                                >
                                    <span class={checkboxEmail ? '' : 'opacity-0'}>
                                        <Check class="h-4 w-4 text-white" />
                                    </span>
                                </div>
                            </div>
                            Email Notifications
                        </label>
                        <!-- SMS Notifications -->
                        <label
                            for="checkboxSMS"
                            class="flex cursor-pointer items-center text-sm font-medium text-gray-700 select-none dark:text-gray-400"
                        >
                            <div class="relative">
                                <input
                                    type="checkbox"
                                    id="checkboxSMS"
                                    class="sr-only"
                                    bind:checked={checkboxSMS}
                                />
                                <div
                                    class={`hover:border-brand-500 dark:hover:border-brand-500 mr-3 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] ${checkboxSMS ? 'border-brand-500 bg-brand-500' : 'border-gray-300 bg-transparent dark:border-gray-700'}`}
                                >
                                    <span class={checkboxSMS ? '' : 'opacity-0'}>
                                        <Check class="h-4 w-4 text-white" />
                                    </span>
                                </div>
                            </div>
                            SMS Notifications
                        </label>
                        <!-- Sound Alerts -->
                        <label
                            for="checkboxSound"
                            class="flex cursor-pointer items-center text-sm font-medium text-gray-700 select-none dark:text-gray-400"
                        >
                            <div class="relative">
                                <input
                                    type="checkbox"
                                    id="checkboxSound"
                                    class="sr-only"
                                    bind:checked={checkboxSound}
                                />
                                <div
                                    class={`hover:border-brand-500 dark:hover:border-brand-500 mr-3 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] ${checkboxSound ? 'border-brand-500 bg-brand-500' : 'border-gray-300 bg-transparent dark:border-gray-700'}`}
                                >
                                    <span class={checkboxSound ? '' : 'opacity-0'}>
                                        <Check class="h-4 w-4 text-white" />
                                    </span>
                                </div>
                            </div>
                            Sound Alerts
                        </label>
                    </div>
                </div>
            </div>
            <div class="flex justify-end">
                <button class="btn-primary-md">
                    <Save class="h-5 w-5" />
                    Save Settings
                </button>
            </div>
        </div>
    </div>
</div>

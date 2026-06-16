<script lang="ts">
    import { onMount } from 'svelte';
    import { createQuery } from '@tanstack/svelte-query';
    import {
        AlertTriangle,
        Camera,
        ChevronDown,
        ChevronFirst,
        ChevronLast,
        ChevronLeft,
        ChevronRight,
        Download,
        Filter,
        Footprints,
        Maximize,
        Play,
        RefreshCcw,
        User,
        Volume2
    } from '@lucide/svelte';
    import Breadcrumb from '../../../components/breadcrumb/Breadcrumb.svelte';
    import { slide } from 'svelte/transition';
    import { getRecordingList, getCamerasForPlayback } from './api';
	import type { RecordingData } from '$lib/interfaces/recording.interfaces';
    import type { MonitoringFeed } from '$lib/interfaces/monitoring.interfaces';
    import { formatDistanceToNow, parseISO } from 'date-fns';

    let openRecordingFilters = $state(false);
    let searchPerson = $state('');
    let selectedCamera = $state('');
    let selectedDate = $state<string | null>(null);

    let recordingData: RecordingData[] = $state([]);
    let cameras: MonitoringFeed[] = $state([]);
    let isLoading = $state(false);

    let activeRecording = $state<RecordingData | null>(null);
    let videoPlayer: HTMLVideoElement;

    function formatDate(date: Date): string {
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    }

    function formatTime(date: Date): string {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
        });
    }

    async function loadRecordingList() {
        isLoading = true;
        try {
            const dateObj = selectedDate ? new Date(selectedDate) : null;
            const recordings = await getRecordingList(searchPerson, selectedCamera, dateObj);
            recordingData = recordings.map(rec => ({
                ...rec,
                startTime: new Date(rec.startTime),
                endTime: new Date(rec.endTime)
            }));
            
            if (recordingData.length > 0) {
                activeRecording = recordingData[0];
            } else {
                activeRecording = null;
            }
        } catch (error) {
            console.error('Failed to load recording list:', error);
            recordingData = [];
        } finally {
            isLoading = false;
        }
    }

    async function loadCameras() {
        try {
            const cameraFeeds = await getCamerasForPlayback();
            cameras = cameraFeeds;
        } catch (error) {
            console.error('Failed to load cameras for playback:', error);
            cameras = [];
        }
    }
    
    function playRecording(recording: RecordingData) {
        activeRecording = recording;
    }

    function applyFilters() {
        openRecordingFilters = false;
        loadRecordingList();
    }

    function resetFilters() {
        searchPerson = '';
        selectedCamera = '';
        selectedDate = null;
        openRecordingFilters = false;
        loadRecordingList();
    }
    
    function handleVideoAction(action: 'play' | 'pause' | 'first' | 'last' | 'next' | 'prev') {
        if (!videoPlayer) return;
        switch (action) {
            case 'play':
                videoPlayer.play();
                break;
            case 'pause':
                videoPlayer.pause();
                break;
        }
    }

    onMount(async () => {
        await loadCameras();
        await loadRecordingList();
    });
</script>

<div class="flex flex-col gap-y-6">
    <Breadcrumb pageName="Video Playback" />
    <!-- Video Playback -->
    <div
        class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
    >
        <div
            class="flex flex-col gap-y-4 border-b border-gray-100 px-6 py-3 dark:border-gray-800 lg:flex-row lg:justify-between lg:items-center"
        >
            <h3 class="text-base font-medium text-gray-800 dark:text-white/90">Video Playback</h3>
            <div class="flex flex-wrap items-center gap-y-2 gap-x-2">
                <button class="btn-secondary-outline-md" aria-label="downloadButton">
                    <Download class="h-4 w-4" />
                    Download
                </button>
                <button class="btn-secondary-outline-md" aria-label="snapshotButton">
                    <Camera class="h-4 w-4" />
                    Snapshot
                </button>
                <button class="btn-secondary-outline-md" aria-label="fullscreenButton">
                    <Maximize class="h-4 w-4" />
                    Fullscreen
                </button>
            </div>
        </div>
        <div class="flex flex-col gap-y-8 px-6 py-5">
            <div class="relative h-96 w-full overflow-hidden rounded-lg">
                {#if activeRecording}
                    <video
                        bind:this={videoPlayer}
                        src={activeRecording.camera?.streamUrl || activeRecording.filePath}
                        controls
                        autoplay
                        muted
                        playsinline
                        class="relative h-full w-full object-cover"
                    ></video>
                    <div class="absolute top-0 left-0 h-full w-full bg-gray-800/70"></div>
                    <div class="absolute bottom-0 px-4 pb-4 w-full">
                        <div class="flex flex-col gap-y-4">
                            <p class="text-theme-lg font-medium text-white">
                                {activeRecording.camera?.name || 'Unknown Camera'} - {formatDate(activeRecording.startTime)} {formatTime(activeRecording.startTime)}
                            </p>
                            <div class="flex items-center gap-x-4">
                                <div class="flex items-center gap-x-2">
                                    <button aria-label="videoButton" class="btn-secondary-icon text-white hover:text-gray-800">
                                        <ChevronFirst class="h-4 w-4" />
                                    </button>
                                    <button aria-label="videoButton" class="btn-secondary-icon text-white hover:text-gray-800">
                                        <ChevronLeft class="h-4 w-4" />
                                    </button>
                                    <button aria-label="videoButton" class="btn-secondary-icon text-white hover:text-gray-800">
                                        <Play class="h-4 w-4" />
                                    </button>
                                    <button aria-label="videoButton" class="btn-secondary-icon text-white hover:text-gray-800">
                                        <ChevronRight class="h-4 w-4" />
                                    </button>
                                    <button aria-label="videoButton" class="btn-secondary-icon text-white hover:text-gray-800">
                                        <ChevronLast class="h-4 w-4" />
                                    </button>
                                </div>
                                <div class="flex flex-1 items-center gap-x-2">
                                    <span class="text-theme-sm text-white">10:30:15</span>
                                    <div class="h-1.5 w-full rounded bg-brand-500"></div>
                                    <span class="text-theme-sm text-white">10:45:15</span>
                                </div>
                                <button aria-label="videoButton" class="btn-secondary-icon text-white hover:text-gray-800">
                                    <Volume2 class="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                {:else}
                    <div class="absolute inset-0 flex items-center justify-center bg-gray-800/70 text-white/50 text-xl font-medium">
                        No video selected.
                    </div>
                {/if}
            </div>
            <div class="flex flex-col gap-y-2">
                <div class="flex justify-between items-center">
                    <span class="text-theme-sm text-gray-800">05:00</span>
                    <span class="text-theme-sm text-gray-800">07:30</span>
                    <span class="text-theme-sm text-gray-800">10:46</span>
                </div>
                <div class="w-full h-4 rounded bg-gray-100"></div>
                <div class="flex items-center gap-x-4">
                    <div class="flex items-center gap-x-2">
                        <div class="w-3 h-3 rounded-full bg-success-500"></div>
                        <span class="text-theme-sm text-gray-800">Motion</span>
                    </div>
                    <div class="flex items-center gap-x-2">
                        <div class="w-3 h-3 rounded-full bg-brand-500"></div>
                        <span class="text-theme-sm text-gray-800">Face</span>
                    </div>
                    <div class="flex items-center gap-x-2">
                        <div class="w-3 h-3 rounded-full bg-error-500"></div>
                        <span class="text-theme-sm text-gray-800">Intrusion</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Recording List -->
    <div
        class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
    >
        <div
            class="flex flex-col gap-y-4 border-b border-gray-100 px-6 py-3 dark:border-gray-800 lg:flex-row lg:items-center lg:justify-between"
        >
            <h3 class="text-base font-medium text-gray-800 dark:text-white/90">Recording List</h3>
            <div class="flex items-center gap-x-2">
                <input
                    type="text"
                    placeholder="Search by person name"
                    bind:value={searchPerson}
                    class="text-input"
                />
                <div class="relative inline-block">
                    <button
                        on:click={() => (openRecordingFilters = !openRecordingFilters)}
                        aria-label="filterButton"
                        class="btn-primary-outline-sm"
                    >
                        <Filter class="h-4 w-4" />
                        Filters
                    </button>
                    {#if openRecordingFilters}
                        <div class="dropdown" transition:slide>
                            <ul class="flex flex-col gap-y-2">
                                <li class="grid grid-cols-1 gap-2 lg:grid-cols-2">
                                    <div class="form-groups">
                                        <span class="form-label">Camera</span>
                                        <div class="relative z-20 bg-transparent">
                                            <select bind:value={selectedCamera} class="select-input">
                                                <option value="" class="text-gray-700 dark:bg-gray-900 dark:text-gray-400">Select option</option>
                                                {#each cameras as camera}
                                                <option
                                                    value={camera.name}
                                                    class="text-gray-700 dark:bg-gray-900 dark:text-gray-400"
                                                >
                                                    {camera.name}
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
                                    <div class="form-groups">
                                        <span class="form-label">Date</span>
                                        <input bind:value={selectedDate} type="date" class="text-input" />
                                    </div>
                                </li>
                                <li class="grid grid-cols-1 gap-2 lg:grid-cols-2">
                                    <div class="form-groups">
                                        <span class="form-label">Time From</span>
                                        <input type="time" class="text-input" />
                                    </div>
                                    <div class="form-groups">
                                        <span class="form-label">Time To</span>
                                        <input type="time" class="text-input" />
                                    </div>
                                </li>
                                <li class="grid grid-cols-1 gap-2 lg:grid-cols-2">
                                    <div class="form-groups col-span-full">
                                        <span class="form-label">Event Types</span>
                                        <div class="relative z-20 bg-transparent">
                                            <select class="select-input">
                                                <option value="" class="text-gray-700 dark:bg-gray-900 dark:text-gray-400">Select option</option>
                                                {#each ['Face Recognition', 'Unattended Object', 'Motion Detection', 'Intrusion Alert'] as option}
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
                                </li>
                                <li class="mt-4 flex items-center justify-end gap-x-2">
                                    <button class="btn-secondary-md" on:click={resetFilters}>
                                        Reset Filters
                                    </button>
                                    <button class="btn-primary-md" on:click={applyFilters}>
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
            <div class="max-w-full overflow-x-auto">
                <table class="min-w-full">
                    <thead class="border-b border-gray-100 dark:border-white/[0.05]">
                        <tr>
                            <th class="px-5 py-3 sm:px-6">
                                <div class="flex items-center">
                                    <p class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">#</p>
                                </div>
                            </th>
                            <th class="px-5 py-3 sm:px-6">
                                <div class="flex items-center">
                                    <p class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">Camera</p>
                                </div>
                            </th>
                            <th class="px-5 py-3 sm:px-6">
                                <div class="flex items-center">
                                    <p class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">
                                        Date & Time
                                    </p>
                                </div>
                            </th>
                            <th class="px-5 py-3 sm:px-6">
                                <div class="flex items-center">
                                    <p class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">Duration</p>
                                </div>
                            </th>
                            <th class="px-5 py-3 sm:px-6">
                                <div class="flex items-center">
                                    <p class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">
                                        Event Type
                                    </p>
                                </div>
                            </th>
                            <th class="px-5 py-3 sm:px-6">
                                <div class="flex items-center">
                                    <p class="text-theme-xs font-medium text-gray-500 dark:text-gray-400">Actions</p>
                                </div>
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                        {#if isLoading}
                            <tr>
                                <td colspan="6" class="p-4 text-center">Loading recordings...</td>
                            </tr>
                        {:else if recordingData.length === 0}
                            <tr>
                                <td colspan="6" class="p-4 text-center">No recordings found.</td>
                            </tr>
                        {:else}
                            {#each recordingData as recording, index}
                                <tr on:click={() => playRecording(recording)}>
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
                                                {recording.camera?.name || 'N/A'}
                                            </p>
                                        </div>
                                    </td>
                                    <td class="px-5 py-4 sm:px-6">
                                        <div class="flex items-center">
                                            <p class="text-theme-sm text-gray-500 dark:text-gray-400">
                                                {formatDate(recording.startTime)} {formatTime(recording.startTime)}
                                            </p>
                                        </div>
                                    </td>
                                    <td class="px-5 py-4 sm:px-6">
                                        <div class="flex items-center">
                                            <p class="text-theme-sm text-gray-500 dark:text-gray-400">
                                                {recording.duration}
                                            </p>
                                        </div>
                                    </td>
                                    <td class="px-5 py-4 sm:px-6">
                                        <div class="flex items-center gap-x-2">
                                            {#if recording.eventType === 'Face Recognition'}
                                                <User class="h-4 w-4" />
                                            {:else if recording.eventType === 'Intrusion Alert'}
                                                <AlertTriangle class="h-4 w-4" />
                                            {:else if recording.eventType === 'Motion Detection'}
                                                <Footprints class="h-4 w-4" />
                                            {/if}
                                            <p class="text-theme-sm text-gray-500 dark:text-gray-400">
                                                {recording.eventType}
                                            </p>
                                        </div>
                                    </td>
                                    <td class="px-5 py-4 sm:px-6">
                                        <div class="flex items-center gap-x-2">
                                            <button aria-label="playButton" class="btn-secondary-icon">
                                                <Play class="h-4 w-4" />
                                            </button>
                                            <button aria-label="downloadButton" class="btn-secondary-icon">
                                                <Download class="h-4 w-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            {/each}
                        {/if}
                    </tbody>
                </table>
            </div>
            <div class="flex flex-col items-center gap-y-4 lg:flex-row lg:justify-between">
                <span class="text-theme-sm text-gray-400">Showing 10 to 10 of {recordingData.length} entries</span>
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
</div>

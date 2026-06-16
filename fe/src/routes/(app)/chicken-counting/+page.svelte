<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { renderChart } from 'svelte-chart-apex';
    import {
        Activity, CalendarDays, Circle, ClipboardList, Clock,
        Drumstick, Hash, Maximize2, Pause, Play, RefreshCcw, Settings,
        Square, TrendingUp, Video, WifiOff
    } from '@lucide/svelte';
    import Breadcrumb from '../../../components/breadcrumb/Breadcrumb.svelte';
    import {
        getLatestCount, getSessions,
        getCountingStatus, startCounting, pauseCounting, resumeCounting, stopCounting,
        getChickenModels, getUploadedVideos,
        getVideoPreviewUrl, getVideoInfo,
        PROCESSED_VIDEO_URL, BE2_BASE,
    } from './api';
    import type { CountingStatus, ChickenModel, UploadedVideo, VideoInfo } from './api';

    const LIVE_STREAM_URL = `${BE2_BASE}/api/mobile/v1/chicken/process/live-stream`;
    import type { ChickenSession, ChickenLatest } from '$lib/interfaces/chicken.interfaces';

    // ── Firebase state ────────────────────────────────────────────────────────
    let latest: ChickenLatest | null = $state(null);
    let sessions: ChickenSession[] = $state([]);
    let selectedDate: string = $state(todayString());
    let isLoading: boolean = $state(false);

    // ── View mode ─────────────────────────────────────────────────────────────
    let viewMode: 'cctv' | 'processing' = $state('cctv');

    // ── CCTV Live state ───────────────────────────────────────────────────────
    let streamUrl: string = $state('');
    let imgSrc: string = $state('');
    let autoRefresh: boolean = $state(false);
    let countRefreshInterval: ReturnType<typeof setInterval> | null = null;
    let streamError: boolean = $state(false);
    let isFullscreen: boolean = $state(false);
    let liveViewRef: HTMLDivElement | undefined = $state(undefined);

    // ── Processing mode state ─────────────────────────────────────────────────
    let countingStatus: CountingStatus | null = $state(null);
    let availableModels: ChickenModel[] = $state([]);
    let availableVideos: UploadedVideo[] = $state([]);
    let selectedVideo: string = $state('');
    let selectedModel: string = $state('');
    let lineX: number = $state(400);
    let isStarting: boolean = $state(false);
    let isStopping: boolean = $state(false);
    let actionMessage: string = $state('');
    let statusPollInterval: ReturnType<typeof setInterval> | null = null;
    let videoInfo: VideoInfo | null = $state(null);
    let previewDebounce: ReturnType<typeof setTimeout> | null = null;
    let bufferWidth: number = $state(100);

    // Preview URL — reaktif terhadap slider, debounced 400ms agar tidak spam API
    let previewUrl: string = $state('');

    function schedulePreviewUpdate() {
        if (previewDebounce) clearTimeout(previewDebounce);
        previewDebounce = setTimeout(() => {
            if (selectedVideo) {
                previewUrl = getVideoPreviewUrl(selectedVideo, lineX, bufferWidth);
            }
        }, 400);
    }

    function todayString(): string {
        return new Date().toISOString().slice(0, 10);
    }

    const isMjpeg = $derived(
        streamUrl.toLowerCase().includes('mjpg') ||
        streamUrl.toLowerCase().includes('mjpeg') ||
        streamUrl.toLowerCase().includes('/video') ||
        streamUrl.toLowerCase().startsWith('http')
    );

    // Active count: from processing session or Firebase depending on mode
    const activeCount = $derived(
        viewMode === 'processing' && countingStatus
            ? countingStatus.total_count
            : (latest?.chicken_total ?? 0)
    );

    const isCountingRunning = $derived(countingStatus?.running === true);
    const isPaused          = $derived(countingStatus?.status === 'paused');
    const isTranscoding     = $derived(countingStatus?.status === 'transcoding');
    const csInfo            = $derived(countingStatusInfo(countingStatus?.status ?? null));

    // ── CCTV helpers ──────────────────────────────────────────────────────────
    function startCountRefresh() {
        stopCountRefresh();
        countRefreshInterval = setInterval(async () => {
            const l = await getLatestCount(selectedDate);
            if (l) latest = l;
        }, 10_000);
    }

    function stopCountRefresh() {
        if (countRefreshInterval) { clearInterval(countRefreshInterval); countRefreshInterval = null; }
    }

    function toggleAutoRefresh() {
        autoRefresh = !autoRefresh;
        if (autoRefresh) startCountRefresh();
        else stopCountRefresh();
    }

    function toggleFullscreen() {
        if (!liveViewRef) return;
        if (!document.fullscreenElement) {
            liveViewRef.requestFullscreen();
            isFullscreen = true;
        } else {
            document.exitFullscreen();
            isFullscreen = false;
        }
    }

    // ── Processing mode helpers ───────────────────────────────────────────────
    let _pollBusy = false;
    function startStatusPoll() {
        stopStatusPoll();
        statusPollInterval = setInterval(async () => {
            if (_pollBusy) return;
            _pollBusy = true;
            try {
                const s = await getCountingStatus();
                if (s) {
                    countingStatus = s;
                    if (!s.running && s.output_file) {
                        stopStatusPoll();
                    }
                }
            } finally {
                _pollBusy = false;
            }
        }, 300);
    }

    function stopStatusPoll() {
        if (statusPollInterval) { clearInterval(statusPollInterval); statusPollInterval = null; }
    }

    async function switchToProcessing() {
        viewMode = 'processing';
        const [s, m, v] = await Promise.all([
            getCountingStatus(),
            getChickenModels(),
            getUploadedVideos(),
        ]);
        if (s) countingStatus = s;
        availableModels = m;
        availableVideos = v;
        if (m.length > 0 && !selectedModel) selectedModel = m[0].filename;
        if (v.length > 0 && !selectedVideo) {
            selectedVideo = v[0].name;
            await loadVideoInfo(selectedVideo);
        }
        startStatusPoll();
    }

    async function loadVideoInfo(filename: string) {
        videoInfo = null;
        const info = await getVideoInfo(filename);
        if (info) {
            videoInfo = info;
            // Auto-set suggested values if user hasn't changed from default
            if (lineX === 400) lineX = info.suggested_line_x;
            if (bufferWidth === 100) bufferWidth = info.suggested_buffer_width;
        }
        previewUrl = getVideoPreviewUrl(filename, lineX, bufferWidth);
    }

    async function switchToCctv() {
        viewMode = 'cctv';
        stopStatusPoll();
    }

    async function handleStart() {
        if (!selectedVideo && viewMode === 'processing') {
            actionMessage = 'Pilih file video terlebih dahulu';
            return;
        }
        isStarting = true;
        actionMessage = '';
        const result = await startCounting({
            sourceType: 'video',
            sourceName: selectedVideo,
            modelFilename: selectedModel || undefined,
            lineX,
            bufferWidth,
        });
        isStarting = false;
        actionMessage = result.message;
        if (result.success) {
            // Immediately fetch status
            const s = await getCountingStatus();
            if (s) countingStatus = s;
        }
    }

    async function handlePause() {
        const result = await pauseCounting();
        actionMessage = result.message ?? '';
        const s = await getCountingStatus();
        if (s) countingStatus = s;
    }

    async function handleResume() {
        const result = await resumeCounting();
        actionMessage = result.message ?? '';
        const s = await getCountingStatus();
        if (s) countingStatus = s;
    }

    async function handleStop() {
        isStopping = true;
        actionMessage = '';
        const result = await stopCounting();
        isStopping = false;
        actionMessage = result.success ? `Menyelesaikan video... (${result.total_count ?? 0} ekor)` : 'Gagal menghentikan';
        // Thread may still be transcoding; keep polling until output_file appears
        if (!statusPollInterval) startStatusPoll();
        const s = await getCountingStatus();
        if (s) {
            countingStatus = s;
            if (!s.running && s.output_file) {
                stopStatusPoll();
                actionMessage = `Selesai. Total: ${s.total_count} ekor`;
            }
        }
    }

    async function handleStartFromStream() {
        if (!streamUrl) return;
        isStarting = true;
        actionMessage = '';
        const result = await startCounting({
            sourceType: 'stream',
            sourceName: streamUrl,
            modelFilename: selectedModel || undefined,
            lineX,
        });
        isStarting = false;
        actionMessage = result.message;
        if (result.success) {
            viewMode = 'processing';
            startStatusPoll();
            const s = await getCountingStatus();
            if (s) countingStatus = s;
        }
    }

    // ── Derived stats ─────────────────────────────────────────────────────────
    const totalToday = $derived(
        sessions.reduce((max, s) => Math.max(max, s.chicken_total), 0)
    );
    const avgPerSession = $derived(
        sessions.length > 0
            ? Math.round(sessions.reduce((sum, s) => sum + s.chicken_total, 0) / sessions.length)
            : 0
    );
    const totalSessions = $derived(sessions.length);


    // ── Status helpers ────────────────────────────────────────────────────────
    type StatusInfo = { label: string; textClass: string; badgeClass: string; dotClass: string; pulse: boolean };

    function countingStatusInfo(status: CountingStatus['status'] | null): StatusInfo {
        switch (status) {
            case 'running':
                return { label: 'Sedang Berjalan', textClass: 'text-success-500', badgeClass: 'bg-success-500/10 text-success-600', dotClass: 'bg-success-500', pulse: true };
            case 'paused':
                return { label: 'Dijeda', textClass: 'text-warning-500', badgeClass: 'bg-warning-500/10 text-warning-600', dotClass: 'bg-warning-500', pulse: false };
            case 'transcoding':
                return { label: 'Mengompresi...', textClass: 'text-blue-400', badgeClass: 'bg-blue-500/10 text-blue-400', dotClass: 'bg-blue-400', pulse: true };
            case 'finished':
                return { label: 'Selesai', textClass: 'text-success-500', badgeClass: 'bg-success-500/10 text-success-600', dotClass: 'bg-success-500', pulse: false };
            case 'stopped':
                return { label: 'Dihentikan', textClass: 'text-warning-500', badgeClass: 'bg-warning-500/10 text-warning-600', dotClass: 'bg-warning-500', pulse: false };
            case 'error':
                return { label: 'Error', textClass: 'text-error-500', badgeClass: 'bg-error-500/10 text-error-600', dotClass: 'bg-error-500', pulse: false };
            default:
                return { label: 'Idle', textClass: 'text-gray-400', badgeClass: 'bg-gray-100 text-gray-500 dark:bg-gray-800', dotClass: 'bg-gray-400', pulse: false };
        }
    }

    // Legacy helpers for Firebase session statuses (CCTV mode)
    function statusClass(status: string | null): string {
        if (!status) return 'text-gray-400';
        const s = status.toLowerCase();
        if (s.includes('running') || s.includes('active')) return 'text-success-500';
        if (s.includes('stopped') || s.includes('offline') || s.includes('error')) return 'text-error-500';
        return 'text-warning-500';
    }
    function statusBadgeClass(status: string | null): string {
        if (!status) return 'bg-gray-100 text-gray-500 dark:bg-gray-800';
        const s = status.toLowerCase();
        if (s.includes('running') || s.includes('active')) return 'bg-success-500/10 text-success-600';
        if (s.includes('stopped') || s.includes('offline') || s.includes('error')) return 'bg-error-500/10 text-error-600';
        return 'bg-warning-500/10 text-warning-600';
    }
    function isSystemRunning(status: string | null): boolean {
        return !!status && (status.toLowerCase().includes('running') || status.toLowerCase().includes('active'));
    }

    function calcDuration(start: string | null, stop: string | null): string {
        if (!start) return '—';
        const end = stop ? new Date(stop) : new Date();
        const diff = Math.abs(end.getTime() - new Date(start).getTime());
        const mins = Math.floor(diff / 60000);
        const secs = Math.floor((diff % 60000) / 1000);
        return `${mins}m ${secs}s`;
    }


    // ── Data loading ──────────────────────────────────────────────────────────
    async function loadAll() {
        isLoading = true;
        try {
            const [l, s] = await Promise.all([
                getLatestCount(selectedDate),
                getSessions(selectedDate),
            ]);
            latest = l;
            sessions = s;
        } finally {
            isLoading = false;
        }
    }

    onMount(async () => {
        streamUrl = localStorage.getItem('chicken_stream_url') ?? '';
        if (streamUrl && isMjpeg) imgSrc = streamUrl;
        await loadAll();
        // Check if counting is already running on be2
        const s = await getCountingStatus();
        if (s) countingStatus = s;
        if (s?.running) {
            viewMode = 'processing';
            startStatusPoll();
        }
    });

    onDestroy(() => {
        stopCountRefresh();
        stopStatusPoll();
    });
</script>

<div class="flex flex-col gap-y-6">
    <Breadcrumb pageName="Dashboard Ayam" />

    <!-- Header row -->
    <div class="flex flex-col gap-y-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-x-2">
            <CalendarDays class="h-4 w-4 text-gray-400" />
            <input
                type="date"
                bind:value={selectedDate}
                onchange={loadAll}
                class="select-input pr-4"
            />
        </div>
        <button
            aria-label="refreshButton"
            class="btn-primary-outline-md"
            onclick={loadAll}
            disabled={isLoading}
        >
            <RefreshCcw class={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh Data
        </button>
    </div>

    <!-- ── LIVE VIEW SECTION ────────────────────────────────────────────────── -->
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">

        <!-- Video Feed (2/3 width) -->
        <div
            bind:this={liveViewRef}
            class="lg:col-span-2 rounded-2xl border border-gray-200 bg-black dark:border-gray-800 overflow-hidden relative"
            style="min-height: 340px;"
        >
            <!-- View mode toggle top-bar -->
            <div class="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-4 py-3 bg-gradient-to-b from-black/80 to-transparent">
                <div class="flex items-center gap-x-1 rounded-full bg-black/50 p-1">
                    <button
                        aria-label="modeCctv"
                        class={`flex items-center gap-x-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-all
                            ${viewMode === 'cctv' ? 'bg-white text-gray-900' : 'text-white/70 hover:text-white'}`}
                        onclick={switchToCctv}
                    >
                        <Video class="h-3 w-3" />
                        CCTV Live
                    </button>
                    <button
                        aria-label="modeProcessing"
                        class={`flex items-center gap-x-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-all
                            ${viewMode === 'processing' ? 'bg-brand-500 text-white' : 'text-white/70 hover:text-white'}`}
                        onclick={switchToProcessing}
                    >
                        <Drumstick class="h-3 w-3" />
                        Video Diproses
                    </button>
                </div>

                <div class="flex items-center gap-x-2">
                    {#if viewMode === 'cctv'}
                        <span class="flex items-center gap-x-1.5 rounded bg-error-500 px-2 py-0.5 text-xs font-bold text-white">
                            <Circle class="h-2 w-2 fill-white" />
                            REC
                        </span>
                        <button
                            aria-label="autoRefreshToggle"
                            class={`flex items-center gap-x-1 rounded-full px-3 py-1 text-xs font-medium transition-colors
                                ${autoRefresh ? 'bg-success-500 text-white' : 'bg-white/20 text-white hover:bg-white/30'}`}
                            onclick={toggleAutoRefresh}
                        >
                            <RefreshCcw class={`h-3 w-3 ${autoRefresh ? 'animate-spin' : ''}`} />
                            {autoRefresh ? 'Live' : 'Auto'}
                        </button>
                    {:else}
                        {#if isCountingRunning}
                            <span class="flex items-center gap-x-1.5 rounded bg-brand-500 px-2 py-0.5 text-xs font-bold text-white animate-pulse">
                                <Circle class="h-2 w-2 fill-white" />
                                PROSES
                            </span>
                        {/if}
                    {/if}
                    <button
                        aria-label="fullscreen"
                        class="rounded-full bg-white/20 p-1.5 text-white hover:bg-white/30 transition-colors"
                        onclick={toggleFullscreen}
                    >
                        <Maximize2 class="h-3.5 w-3.5" />
                    </button>
                    <a
                        href="/chicken-counting/config"
                        class="rounded-full bg-white/20 p-1.5 text-white hover:bg-white/30 transition-colors"
                        aria-label="configLink"
                    >
                        <Settings class="h-3.5 w-3.5" />
                    </a>
                </div>
            </div>

            <!-- ── CCTV MODE ───────────────────────────────────────────────── -->
            {#if viewMode === 'cctv'}
                {#if streamUrl && isMjpeg && imgSrc && !streamError}
                    <img
                        src={imgSrc}
                        alt="Live stream"
                        class="h-full w-full object-cover"
                        style="min-height: 340px;"
                        onerror={() => { streamError = true; }}
                    />
                {:else if streamUrl && isMjpeg && streamError}
                    <div class="absolute inset-0 flex flex-col items-center justify-center gap-y-2 bg-gray-900 pt-14">
                        <WifiOff class="h-10 w-10 text-gray-500" />
                        <p class="text-sm text-gray-400">Gagal memuat stream</p>
                        <button
                            aria-label="retryStream"
                            class="mt-1 rounded-lg bg-white/10 px-4 py-1.5 text-xs text-white hover:bg-white/20"
                            onclick={() => { imgSrc = `${streamUrl}?_t=${Date.now()}`; streamError = false; }}
                        >
                            Coba Lagi
                        </button>
                    </div>
                {:else if streamUrl && !isMjpeg}
                    <div class="absolute inset-0 flex flex-col items-center justify-center gap-y-3 bg-gray-900 pt-14">
                        <Video class="h-12 w-12 text-gray-600" />
                        <p class="text-sm font-medium text-gray-300">Stream RTSP terdeteksi</p>
                        <p class="max-w-xs text-center text-xs text-gray-500">
                            Browser tidak bisa memutar RTSP langsung. Gunakan MJPEG/HTTP stream
                            atau tambahkan media server (mis. MediaMTX).
                        </p>
                        <a href="/chicken-counting/config" class="mt-1 rounded-lg bg-brand-500 px-4 py-2 text-xs font-medium text-white hover:bg-brand-600">
                            Ubah Stream URL
                        </a>
                    </div>
                {:else}
                    <div class="absolute inset-0 flex flex-col items-center justify-center gap-y-3 bg-gray-900 pt-14">
                        <div class="flex h-16 w-16 items-center justify-center rounded-full bg-gray-800">
                            <Video class="h-8 w-8 text-gray-500" />
                        </div>
                        <p class="text-sm font-medium text-gray-300">Stream belum dikonfigurasi</p>
                        <p class="text-xs text-gray-500">Tambahkan URL CCTV di halaman konfigurasi</p>
                        <a href="/chicken-counting/config" class="mt-1 rounded-lg bg-brand-500 px-4 py-2 text-xs font-medium text-white hover:bg-brand-600">
                            Konfigurasi Sekarang
                        </a>
                    </div>
                {/if}

            <!-- ── PROCESSING MODE ─────────────────────────────────────────── -->
            {:else}
                {#if isCountingRunning}
                    <!-- Live MJPEG: processed frames with detection overlays in real-time -->
                    <img
                        src={LIVE_STREAM_URL}
                        alt="Live counting stream"
                        class="h-full w-full object-contain bg-black"
                        style="min-height: 340px;"
                    />

                    <!-- Progress overlay on top of live stream -->
                    <div class="absolute inset-0 flex flex-col items-end justify-end bg-gradient-to-t from-black/90 via-black/40 to-black/20 pt-14 px-5 pb-5">
                        <!-- Top-center: status badge -->
                        <div class="absolute top-16 left-1/2 -translate-x-1/2 flex items-center gap-x-2 rounded-full bg-black/70 px-4 py-1.5">
                            <span class={`h-2 w-2 rounded-full ${csInfo.dotClass} ${csInfo.pulse ? 'animate-pulse' : ''}`}></span>
                            <span class="text-xs font-semibold text-white">{csInfo.label}</span>
                            {#if countingStatus?.device && countingStatus.status === 'running'}
                                <span class={`text-xs font-medium ${countingStatus.device === 'cuda' ? 'text-success-400' : 'text-gray-400'}`}>
                                    · {countingStatus.device === 'cuda' ? 'GPU' : 'CPU'}
                                </span>
                            {/if}
                        </div>

                        <!-- Bottom: frame info + progress bar (hidden while transcoding/paused) -->
                        <div class="w-full">
                            {#if isTranscoding}
                                <p class="text-xs text-white/60 text-center mb-2 animate-pulse">
                                    Mengompresi video ke H.264, harap tunggu...
                                </p>
                            {:else}
                                <div class="flex items-center justify-between mb-1.5">
                                    <span class="text-xs text-white/60">
                                        Frame {(countingStatus?.current_frame ?? 0).toLocaleString()} / {(countingStatus?.total_frames ?? 0).toLocaleString()}
                                        {#if !isPaused}&nbsp;·&nbsp; {countingStatus?.fps ?? 0} fps{/if}
                                    </span>
                                    <span class="text-xs font-bold text-success-400">
                                        {countingStatus?.total_count ?? 0} ekor
                                    </span>
                                </div>
                                <div class="h-2.5 w-full rounded-full bg-white/10 overflow-hidden">
                                    <div
                                        class={`h-full rounded-full transition-all duration-500 ${isPaused ? 'bg-warning-500' : 'bg-brand-500'}`}
                                        style="width: {countingStatus?.progress ?? 0}%"
                                    ></div>
                                </div>
                                <p class="mt-1 text-xs text-white/50 text-right">
                                    {countingStatus?.progress ?? 0}% {isPaused ? '· dijeda' : 'selesai'}
                                </p>
                            {/if}
                        </div>
                    </div>

                {:else if countingStatus?.output_file}
                    <!-- Done: play the H.264 result video -->
                    {#key countingStatus.output_file}
                    <video
                        src={PROCESSED_VIDEO_URL}
                        class="h-full w-full bg-black"
                        style="min-height: 340px; object-fit: contain;"
                        controls
                        autoplay
                        muted
                    >
                        <p class="text-white p-4 text-sm">
                            Browser tidak dapat memutar video.
                            <a href={PROCESSED_VIDEO_URL} download class="text-brand-400 underline ml-1">Download video</a>
                        </p>
                    </video>
                    <!-- Label & download button overlay -->
                    <div class="absolute top-14 right-3 z-20 flex items-center gap-x-2">
                        <span class="rounded-full bg-success-500/20 px-2.5 py-1 text-xs font-medium text-success-400">
                            ✓ {countingStatus.total_count} ekor · Video siap
                        </span>
                        <a
                            href={PROCESSED_VIDEO_URL}
                            download="hasil_counting.mp4"
                            class="rounded-full bg-black/60 px-2.5 py-1 text-xs font-medium text-white hover:bg-black/80"
                        >
                            Download
                        </a>
                    </div>
                    {/key}

                {:else if countingStatus?.status === 'error'}
                    <div class="absolute inset-0 flex flex-col items-center justify-center gap-y-3 bg-gray-900 pt-14">
                        <WifiOff class="h-12 w-12 text-error-500" />
                        <p class="text-sm font-medium text-error-400">Error Counting</p>
                        <p class="max-w-xs text-center text-xs text-gray-500">{countingStatus?.error_message}</p>
                    </div>

                {:else}
                    <!-- Idle: show static preview if a video is selected, else placeholder -->
                    {#if previewUrl}
                        <img
                            src={previewUrl}
                            alt="Preview garis hitung"
                            class="h-full w-full object-contain bg-black"
                            style="min-height: 340px;"
                        />
                        <div class="absolute inset-0 flex items-end justify-center pb-6 bg-gradient-to-t from-black/70 to-transparent pt-14">
                            <span class="rounded-full bg-black/60 px-3 py-1.5 text-xs text-white/70">
                                Preview garis hitung · tekan <strong>Mulai</strong> untuk memproses
                            </span>
                        </div>
                    {:else}
                        <div class="absolute inset-0 flex flex-col items-center justify-center gap-y-4 bg-gray-900 pt-14">
                            <div class="flex h-16 w-16 items-center justify-center rounded-full bg-brand-500/20">
                                <Drumstick class="h-8 w-8 text-brand-400" />
                            </div>
                            <p class="text-sm font-medium text-gray-300">Siap Memproses Video</p>
                            <p class="text-xs text-gray-500">Pilih video & model di panel kanan, lalu tekan Mulai</p>
                            <a href="/chicken-counting/config" class="mt-1 rounded-lg border border-gray-600 px-4 py-2 text-xs font-medium text-gray-400 hover:border-brand-400 hover:text-brand-400">
                                Upload Video / Model
                            </a>
                        </div>
                    {/if}
                {/if}
            {/if}

            <!-- Count overlay bottom-left (shown in both modes) -->
            {#if (viewMode === 'cctv' && latest) || (viewMode === 'processing' && countingStatus && countingStatus.status !== 'idle')}
                <div class="absolute bottom-0 left-0 right-0 z-10 flex items-end justify-between px-4 py-3 bg-gradient-to-t from-black/80 to-transparent">
                    <div>
                        <p class="text-xs text-white/60">
                            {viewMode === 'processing' ? 'Counting Aktif' : 'Deteksi Terbaru'}
                        </p>
                        <p class="font-mono text-2xl font-bold text-white">
                            {activeCount.toLocaleString()}
                            <span class="text-sm font-normal text-white/70">ekor</span>
                        </p>
                    </div>
                    {#if viewMode === 'cctv'}
                        <span class={`inline-flex items-center gap-x-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${statusBadgeClass(latest?.status ?? null)}`}>
                            <span class={`h-2 w-2 rounded-full ${isSystemRunning(latest?.status ?? null) ? 'bg-success-500 animate-pulse' : 'bg-error-500'}`}></span>
                            {latest?.status ?? '—'}
                        </span>
                    {:else}
                        <span class={`inline-flex items-center gap-x-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${csInfo.badgeClass}`}>
                            <span class={`h-2 w-2 rounded-full ${csInfo.dotClass} ${csInfo.pulse ? 'animate-pulse' : ''}`}></span>
                            {csInfo.label}
                        </span>
                    {/if}
                </div>
            {/if}
        </div>

        <!-- Stats / Control Panel (1/3 width) -->
        <div class="flex flex-col gap-y-4">

            {#if viewMode === 'cctv'}
                <!-- CCTV: count big card -->
                <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
                    <div class="flex items-center justify-between mb-3">
                        <p class="text-theme-sm font-medium text-gray-500 dark:text-white/60">Ayam Terdeteksi</p>
                        <div class={`h-2 w-2 rounded-full ${isSystemRunning(latest?.status ?? null) ? 'bg-success-500 animate-pulse' : 'bg-gray-300'}`}></div>
                    </div>
                    <p class="text-5xl font-bold text-gray-800 dark:text-white/90 tabular-nums">
                        {isLoading ? '—' : (latest?.chicken_total ?? 0).toLocaleString()}
                    </p>
                    <p class="mt-1 text-theme-sm text-gray-400">ekor</p>
                    {#if latest?.last_update}
                        <div class="mt-4 flex items-center gap-x-1.5 text-xs text-gray-400">
                            <Clock class="h-3.5 w-3.5" />
                            Update: {latest.last_update}
                        </div>
                    {/if}
                </div>

                <!-- CCTV: Session info -->
                <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
                    <p class="mb-3 text-theme-sm font-medium text-gray-500 dark:text-white/60">Info Sesi Aktif</p>
                    <div class="flex flex-col gap-y-3">
                        <div class="flex items-center justify-between">
                            <span class="text-theme-xs text-gray-400">Session ID</span>
                            <span class="font-mono text-theme-xs font-medium text-gray-700 dark:text-gray-300 truncate max-w-[140px]">{latest?.session_id ?? '—'}</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-theme-xs text-gray-400">Mulai</span>
                            <span class="text-theme-xs text-gray-600 dark:text-gray-400">{latest?.start_time ?? '—'}</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-theme-xs text-gray-400">Selesai</span>
                            <span class="text-theme-xs text-gray-600 dark:text-gray-400">{latest?.stop_time ?? 'Berjalan'}</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-theme-xs text-gray-400">Status</span>
                            <span class={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${statusBadgeClass(latest?.status ?? null)}`}>
                                {latest?.status ?? '—'}
                            </span>
                        </div>
                    </div>
                </div>

            {:else}
                <!-- PROCESSING: Count display -->
                <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
                    <div class="flex items-center justify-between mb-3">
                        <p class="text-theme-sm font-medium text-gray-500 dark:text-white/60">Counting Aktif</p>
                        <span class={`inline-flex items-center gap-x-1 rounded-full px-2 py-0.5 text-xs font-medium ${csInfo.badgeClass}`}>
                            <span class={`h-1.5 w-1.5 rounded-full ${csInfo.dotClass} ${csInfo.pulse ? 'animate-pulse' : ''}`}></span>
                            {csInfo.label}
                        </span>
                    </div>
                    <p class="text-5xl font-bold text-brand-600 dark:text-brand-400 tabular-nums">
                        {countingStatus?.total_count ?? 0}
                    </p>
                    <p class="mt-1 text-theme-sm text-gray-400">ekor terdeteksi</p>
                    {#if countingStatus?.start_time}
                        <div class="mt-3 flex flex-col gap-y-1.5 text-xs text-gray-400">
                            <div class="flex justify-between">
                                <span>Sumber</span>
                                <span class="text-gray-600 dark:text-gray-300 truncate max-w-[110px]">{countingStatus.source_name || '—'}</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Model</span>
                                <span class="text-gray-600 dark:text-gray-300 truncate max-w-[110px]">{countingStatus.model_name || '—'}</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Durasi</span>
                                <span class="text-gray-600 dark:text-gray-300">{calcDuration(countingStatus.start_time, countingStatus.stop_time)}</span>
                            </div>
                        </div>
                    {/if}
                    {#if actionMessage}
                        <p class="mt-3 text-xs text-brand-500 font-medium">{actionMessage}</p>
                    {/if}
                </div>

                <!-- PROCESSING: Controls -->
                <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
                    <p class="mb-4 text-theme-sm font-medium text-gray-500 dark:text-white/60">Kontrol Counting</p>
                    <div class="flex flex-col gap-y-3">
                        <!-- Video selector -->
                        <div class="form-groups">
                            <span class="form-label">File Video</span>
                            {#if availableVideos.length === 0}
                                <a href="/chicken-counting/config" class="flex items-center justify-center gap-x-1.5 rounded-lg border border-dashed border-gray-300 dark:border-gray-700 py-2.5 text-xs text-brand-500 hover:border-brand-400">
                                    + Upload Video di Konfigurasi
                                </a>
                            {:else}
                                <select
                                    bind:value={selectedVideo}
                                    disabled={isCountingRunning}
                                    class="select-input"
                                    onchange={async () => { if (selectedVideo) await loadVideoInfo(selectedVideo); }}
                                >
                                    {#each availableVideos as v}
                                        <option value={v.name}>{v.name} ({v.size_mb} MB)</option>
                                    {/each}
                                </select>
                            {/if}
                            {#if videoInfo}
                                <p class="text-theme-xs text-gray-400 mt-1">
                                    {videoInfo.width}×{videoInfo.height} · {videoInfo.fps}fps · {videoInfo.duration_seconds}s
                                </p>
                            {/if}
                        </div>

                        <!-- Model selector -->
                        <div class="form-groups">
                            <span class="form-label">Model YOLO</span>
                            {#if availableModels.length === 0}
                                <a href="/chicken-counting/config" class="flex items-center justify-center gap-x-1.5 rounded-lg border border-dashed border-gray-300 dark:border-gray-700 py-2.5 text-xs text-brand-500 hover:border-brand-400">
                                    + Upload Model di Konfigurasi
                                </a>
                            {:else}
                                <select bind:value={selectedModel} disabled={isCountingRunning} class="select-input">
                                    {#each availableModels as m}
                                        <option value={m.filename}>{m.name} ({m.size_mb} MB)</option>
                                    {/each}
                                </select>
                            {/if}
                        </div>

                        <!-- Line X + Buffer + Live Preview -->
                        <div class="form-groups">
                            <div class="flex items-center justify-between mb-1">
                                <span class="form-label mb-0">Garis Hitung</span>
                                {#if videoInfo}
                                    <button
                                        aria-label="resetSuggested"
                                        class="text-theme-xs text-brand-500 hover:underline"
                                        onclick={() => { lineX = videoInfo!.suggested_line_x; bufferWidth = videoInfo!.suggested_buffer_width; schedulePreviewUpdate(); }}
                                    >
                                        Reset ke saran ({videoInfo.suggested_line_x}px)
                                    </button>
                                {/if}
                            </div>
                            <div class="flex items-center gap-x-2 mb-1">
                                <span class="text-theme-xs text-gray-400 w-14 shrink-0">Line X</span>
                                <input
                                    type="range"
                                    min="20"
                                    max={videoInfo?.width ?? 1200}
                                    step="5"
                                    bind:value={lineX}
                                    disabled={isCountingRunning}
                                    class="flex-1 accent-red-500"
                                    oninput={schedulePreviewUpdate}
                                />
                                <span class="text-theme-xs font-mono text-red-400 w-12 text-right">{lineX}px</span>
                            </div>
                            <div class="flex items-center gap-x-2">
                                <span class="text-theme-xs text-gray-400 w-14 shrink-0">Buffer</span>
                                <input
                                    type="range"
                                    min="10" max="300" step="5"
                                    bind:value={bufferWidth}
                                    disabled={isCountingRunning}
                                    class="flex-1 accent-yellow-400"
                                    oninput={schedulePreviewUpdate}
                                />
                                <span class="text-theme-xs font-mono text-yellow-400 w-12 text-right">+{bufferWidth}px</span>
                            </div>

                            <!-- Live preview of counting line on video frame -->
                            {#if previewUrl && !isCountingRunning}
                                <div class="mt-2 rounded-lg overflow-hidden border border-gray-700">
                                    <img
                                        src={previewUrl}
                                        alt="Preview garis hitung"
                                        class="w-full object-contain"
                                        style="max-height: 140px;"
                                    />
                                    <p class="text-center text-theme-xs text-gray-500 py-1 bg-gray-900">
                                        Preview — garis merah = LINE X, kuning = zona buffer
                                    </p>
                                </div>
                            {/if}
                        </div>

                        <!-- Start / Stop -->
                        {#if isCountingRunning}
                            <!-- Pause / Resume -->
                            {#if isPaused}
                                <button
                                    aria-label="resumeCounting"
                                    class="btn-primary-md w-full justify-center bg-warning-500 hover:bg-warning-600 border-warning-500"
                                    onclick={handleResume}
                                >
                                    <Play class="h-4 w-4" />
                                    Lanjutkan
                                </button>
                            {:else if countingStatus?.status === 'running'}
                                <button
                                    aria-label="pauseCounting"
                                    class="btn-primary-md w-full justify-center bg-gray-600 hover:bg-gray-700 border-gray-600"
                                    onclick={handlePause}
                                >
                                    <Pause class="h-4 w-4" />
                                    Jeda
                                </button>
                            {/if}
                            <!-- Stop -->
                            <button
                                aria-label="stopCounting"
                                class="btn-primary-md w-full justify-center bg-error-500 hover:bg-error-600 border-error-500"
                                onclick={handleStop}
                                disabled={isStopping || isTranscoding}
                            >
                                <Square class="h-4 w-4" />
                                {isStopping ? 'Menghentikan...' : isTranscoding ? 'Mengompresi...' : 'Hentikan'}
                            </button>
                        {:else}
                            <button
                                aria-label="startCounting"
                                class="btn-primary-md w-full justify-center"
                                onclick={handleStart}
                                disabled={isStarting || availableVideos.length === 0 || availableModels.length === 0}
                            >
                                <Play class="h-4 w-4" />
                                {isStarting ? 'Memulai...' : 'Mulai Counting'}
                            </button>
                        {/if}

                        <!-- Refresh lists -->
                        <button
                            aria-label="refreshLists"
                            class="text-xs text-gray-400 hover:text-gray-600 transition-colors text-center"
                            onclick={() => { getChickenModels().then(m => availableModels = m); getUploadedVideos().then(v => availableVideos = v); }}
                        >
                            <RefreshCcw class="inline h-3 w-3 mr-1" />
                            Refresh daftar video & model
                        </button>
                    </div>
                </div>
            {/if}

            <!-- Quick nav (shared) -->
            <a
                href="/chicken-counting/config"
                class="flex items-center justify-between rounded-xl border border-dashed border-gray-300 dark:border-gray-700 px-4 py-3 hover:border-brand-400 hover:bg-brand-50 dark:hover:bg-brand-500/5 transition-colors"
            >
                <div class="flex items-center gap-x-2">
                    <Settings class="h-4 w-4 text-gray-400" />
                    <span class="text-theme-sm text-gray-500">Upload Video, Model & Konfigurasi</span>
                </div>
                <span class="text-xs text-brand-500">→</span>
            </a>
        </div>
    </div>
    <!-- ── END LIVE VIEW ──────────────────────────────────────────────────────── -->

    <!-- Quick stats + link to full rekap -->
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
            <p class="text-xs text-gray-500 dark:text-white/60">Ayam Hari Ini</p>
            <p class="mt-1 text-2xl font-bold text-brand-600 dark:text-brand-400 tabular-nums">{isLoading ? '—' : totalToday.toLocaleString()}</p>
            <p class="text-xs text-gray-400">ekor</p>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
            <p class="text-xs text-gray-500 dark:text-white/60">Rata-rata/Sesi</p>
            <p class="mt-1 text-2xl font-bold text-success-600 dark:text-success-400 tabular-nums">{isLoading ? '—' : avgPerSession.toLocaleString()}</p>
            <p class="text-xs text-gray-400">ekor/sesi</p>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
            <p class="text-xs text-gray-500 dark:text-white/60">Total Sesi</p>
            <p class="mt-1 text-2xl font-bold text-warning-600 dark:text-warning-400 tabular-nums">{isLoading ? '—' : totalSessions}</p>
            <p class="text-xs text-gray-400">sesi hari ini</p>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
            <p class="text-xs text-gray-500 dark:text-white/60">Status Sistem</p>
            <p class={`mt-1 text-base font-semibold ${statusClass(latest?.status ?? null)}`}>
                {isLoading ? '—' : (latest?.status ?? 'Tidak ada data')}
            </p>
            <p class="text-xs text-gray-400 truncate">{latest?.last_update ?? '—'}</p>
        </div>
    </div>

    <!-- Rekap shortcut banner -->
    <a
        href="/chicken-counting/rekap"
        class="flex items-center justify-between rounded-xl border border-dashed border-brand-300 dark:border-brand-700 bg-brand-50 dark:bg-brand-500/5 px-5 py-4 hover:border-brand-500 hover:bg-brand-100 dark:hover:bg-brand-500/10 transition-colors"
    >
        <div class="flex items-center gap-x-3">
            <ClipboardList class="h-5 w-5 text-brand-500" />
            <div>
                <p class="text-sm font-semibold text-brand-700 dark:text-brand-400">Lihat Rekap Lengkap</p>
                <p class="text-xs text-brand-500/70">Rekap sesi, harian, bulanan & tahunan realtime</p>
            </div>
        </div>
        <span class="text-brand-500 text-lg">→</span>
    </a>
</div>

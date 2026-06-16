<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { renderChart } from 'svelte-chart-apex';
    import {
        Activity, CalendarDays, ClipboardList, Clock,
        Download, RefreshCcw, TrendingUp, Users
    } from '@lucide/svelte';
    import Breadcrumb from '../../../../components/breadcrumb/Breadcrumb.svelte';
    import { getLatestCount, getSessions, getDailySummary, BE2_BASE } from '../api';
    import type { ChickenSession, ChickenDailySummary } from '$lib/interfaces/chicken.interfaces';

    const BE2 = BE2_BASE;

    // ── Types ─────────────────────────────────────────────────────────────────
    interface MonthlyRekap {
        year: number; month: number; month_name: string; period: string;
        session_count: number; total_chickens: number;
    }
    interface YearlyRekap {
        year: number; session_count: number; total_chickens: number;
    }
    interface LiveSession {
        running: boolean; status: string; total_count: number;
        current_frame: number; total_frames: number; progress: number;
        source_name: string; model_name: string; start_time: string | null;
    }

    // ── State ─────────────────────────────────────────────────────────────────
    let activeTab: 'sesi' | 'harian' | 'bulanan' | 'tahunan' = $state('sesi');
    let selectedDate: string = $state(todayString());
    let selectedYear: number = $state(new Date().getFullYear());

    let sessions: ChickenSession[]      = $state([]);
    let dailySummary: ChickenDailySummary[] = $state([]);
    let monthlyData: MonthlyRekap[]     = $state([]);
    let yearlyData: YearlyRekap[]       = $state([]);
    let liveSession: LiveSession | null = $state(null);

    let isLoading = $state(false);
    let lastRefresh: Date | null = $state(null);

    let sesiPoll: ReturnType<typeof setInterval> | null = null;
    let dailyPoll: ReturnType<typeof setInterval> | null = null;
    let slowPoll: ReturnType<typeof setInterval> | null = null;

    // ── Helpers ───────────────────────────────────────────────────────────────
    function todayString() { return new Date().toISOString().slice(0, 10); }

    function calcDuration(start: string | null, stop: string | null): string {
        if (!start) return '—';
        const end = stop ? new Date(stop) : new Date();
        const diff = Math.abs(end.getTime() - new Date(start).getTime());
        const h = Math.floor(diff / 3600000);
        const m = Math.floor((diff % 3600000) / 60000);
        const s = Math.floor((diff % 60000) / 1000);
        return h > 0 ? `${h}j ${m}m` : `${m}m ${s}d`;
    }

    function statusBadge(status: string | null) {
        if (!status) return 'bg-gray-100 text-gray-500 dark:bg-gray-800';
        const s = status.toLowerCase();
        if (s === 'dibatalkan') return 'bg-gray-200 text-gray-400 line-through dark:bg-gray-700 dark:text-gray-500';
        if (s.includes('running') || s.includes('active')) return 'bg-success-500/10 text-success-600';
        if (s === 'finished' || s === 'selesai') return 'bg-brand-500/10 text-brand-600';
        if (s.includes('stopped') || s.includes('offline')) return 'bg-warning-500/10 text-warning-600';
        if (s.includes('error')) return 'bg-error-500/10 text-error-600';
        return 'bg-gray-100 text-gray-500 dark:bg-gray-800';
    }

    let cancelingId: string | null = $state(null);

    async function handleCancelSession(s: { session_id: string; date: string; status: string | null }) {
        if (!confirm(`Batalkan sesi ${s.session_id}?\nData sesi ini tidak akan dihitung dalam rekap.`)) return;
        cancelingId = s.session_id;
        try {
            const res = await fetch(`${BE2}/api/mobile/v1/chicken/sessions/${s.date}/${s.session_id}/cancel`, {
                method: 'PATCH',
            });
            if (res.ok) await fetchSessions(selectedDate);
        } finally {
            cancelingId = null;
        }
    }

    // ── API fetchers ──────────────────────────────────────────────────────────
    async function fetchSessions(date: string) {
        const res = await fetch(`${BE2}/api/mobile/v1/chicken/sessions?date=${date}`);
        if (!res.ok) return;
        const j = await res.json();
        sessions = j.data ?? [];
        lastRefresh = new Date();
    }

    async function fetchDaily() {
        const data = await getDailySummary();
        dailySummary = data;
        lastRefresh = new Date();
    }

    async function fetchMonthly(year?: number) {
        const url = year
            ? `${BE2}/api/mobile/v1/chicken/rekap/bulanan?year=${year}`
            : `${BE2}/api/mobile/v1/chicken/rekap/bulanan`;
        const res = await fetch(url);
        if (!res.ok) return;
        const j = await res.json();
        monthlyData = j.data ?? [];
    }

    async function fetchYearly() {
        const res = await fetch(`${BE2}/api/mobile/v1/chicken/rekap/tahunan`);
        if (!res.ok) return;
        const j = await res.json();
        yearlyData = j.data ?? [];
    }

    async function fetchLiveSession() {
        try {
            const res = await fetch(`${BE2}/api/mobile/v1/chicken/rekap/live-session`);
            if (!res.ok) return;
            const j = await res.json();
            liveSession = j.data;
        } catch { liveSession = null; }
    }

    // ── Summary stats ─────────────────────────────────────────────────────────
    const todayTotal = $derived(() => {
        const today = todayString();
        const d = dailySummary.find(x => x.date === today);
        return d?.total_chickens ?? 0;
    });

    const monthTotal = $derived(() => {
        const ym = todayString().slice(0, 7); // YYYY-MM
        return dailySummary
            .filter(x => x.date.startsWith(ym))
            .reduce((sum, x) => sum + x.total_chickens, 0);
    });

    const yearTotal = $derived(() => {
        const y = todayString().slice(0, 4);
        return dailySummary
            .filter(x => x.date.startsWith(y))
            .reduce((sum, x) => sum + x.total_chickens, 0);
    });

    const todaySessions = $derived(sessions.length);

    // ── Charts ────────────────────────────────────────────────────────────────
    const sesiChart = $derived({
        options: {
            chart: { type: 'bar' as const, toolbar: { show: false }, height: 220 },
            plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
            colors: ['#465FFF'],
            series: [{ name: 'Ayam', data: [...sessions].reverse().map(s => s.chicken_total) }],
            xaxis: {
                categories: [...sessions].reverse().map(s => s.session_id.replace('session_', '')),
                labels: { style: { fontSize: '10px' } },
            },
            yaxis: { title: { text: 'Ekor' } },
            tooltip: { y: { formatter: (v: number) => `${v} ekor` } },
            dataLabels: { enabled: false },
            grid: { strokeDashArray: 4 },
        },
    });

    const harianChart = $derived({
        options: {
            chart: { type: 'area' as const, toolbar: { show: false }, height: 240, sparkline: { enabled: false } },
            stroke: { curve: 'smooth' as const, width: 2 },
            fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05 } },
            colors: ['#465FFF'],
            series: [{
                name: 'Ayam',
                data: [...dailySummary].reverse().slice(-30).map(s => s.total_chickens),
            }],
            xaxis: {
                categories: [...dailySummary].reverse().slice(-30).map(s => s.date.slice(5)),
                labels: { rotate: -30, style: { fontSize: '10px' } },
                tickAmount: 10,
            },
            yaxis: { title: { text: 'Ekor' } },
            tooltip: { x: { show: true }, y: { formatter: (v: number) => `${v} ekor` } },
            dataLabels: { enabled: false },
            grid: { strokeDashArray: 4 },
        },
    });

    const bulananChart = $derived({
        options: {
            chart: { type: 'bar' as const, toolbar: { show: false }, height: 240 },
            plotOptions: { bar: { borderRadius: 5, columnWidth: '55%' } },
            colors: ['#17B26A'],
            series: [{ name: 'Ayam', data: [...monthlyData].reverse().map(m => m.total_chickens) }],
            xaxis: {
                categories: [...monthlyData].reverse().map(m => m.period),
                labels: { rotate: -30, style: { fontSize: '10px' } },
            },
            yaxis: { title: { text: 'Ekor' } },
            tooltip: { y: { formatter: (v: number) => `${v} ekor` } },
            dataLabels: { enabled: false },
            grid: { strokeDashArray: 4 },
        },
    });

    const tahunanChart = $derived({
        options: {
            chart: { type: 'bar' as const, toolbar: { show: false }, height: 240 },
            plotOptions: { bar: { borderRadius: 6, columnWidth: '45%' } },
            colors: ['#F79009'],
            series: [{ name: 'Ayam', data: [...yearlyData].reverse().map(y => y.total_chickens) }],
            xaxis: {
                categories: [...yearlyData].reverse().map(y => String(y.year)),
                labels: { style: { fontSize: '12px' } },
            },
            yaxis: { title: { text: 'Ekor' } },
            tooltip: { y: { formatter: (v: number) => `${v} ekor` } },
            dataLabels: { enabled: true, style: { fontSize: '11px' } },
            grid: { strokeDashArray: 4 },
        },
    });

    // ── Polling ────────────────────────────────────────────────────────────────
    function startPolling() {
        stopPolling();
        // Session & live: every 3s
        sesiPoll = setInterval(async () => {
            await fetchSessions(selectedDate);
            await fetchLiveSession();
        }, 3_000);
        // Daily: every 20s
        dailyPoll = setInterval(() => fetchDaily(), 20_000);
        // Monthly + Yearly: every 2 minutes
        slowPoll = setInterval(async () => {
            await fetchMonthly(selectedYear);
            await fetchYearly();
        }, 120_000);
    }

    function stopPolling() {
        [sesiPoll, dailyPoll, slowPoll].forEach(t => { if (t) clearInterval(t); });
        sesiPoll = dailyPoll = slowPoll = null;
    }

    async function loadAll() {
        isLoading = true;
        await Promise.all([
            fetchSessions(selectedDate),
            fetchDaily(),
            fetchMonthly(selectedYear),
            fetchYearly(),
            fetchLiveSession(),
        ]);
        isLoading = false;
    }

    function exportCSV() {
        const headers = ['Session ID', 'Tanggal', 'Mulai', 'Selesai', 'Durasi', 'Total Ayam', 'Status'];
        const rows = sessions.map(s => [
            s.session_id, s.date, s.start_time ?? '', s.stop_time ?? '',
            calcDuration(s.start_time, s.stop_time), s.chicken_total, s.status ?? '',
        ]);
        const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
        const a = document.createElement('a');
        a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
        a.download = `rekap-ayam-${selectedDate}.csv`;
        a.click();
    }

    onMount(async () => { await loadAll(); startPolling(); });
    onDestroy(stopPolling);
</script>

<div class="flex flex-col gap-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-y-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
            <h1 class="text-xl font-bold text-gray-800 dark:text-white/90">Rekap Counting Ayam</h1>
            <p class="text-sm text-gray-500 dark:text-white/50">Data realtime dari Firebase</p>
        </div>
        <div class="flex items-center gap-x-3">
            {#if liveSession?.running}
                <span class="inline-flex items-center gap-x-1.5 rounded-full bg-success-500/10 px-3 py-1 text-xs font-semibold text-success-600">
                    <span class="h-2 w-2 rounded-full bg-success-500 animate-pulse"></span>
                    Counting Aktif — {liveSession.total_count} ekor
                </span>
            {/if}
            {#if lastRefresh}
                <span class="text-xs text-gray-400">
                    <Clock class="inline h-3 w-3 mr-1" />
                    {lastRefresh.toLocaleTimeString('id-ID')}
                </span>
            {/if}
            <button
                class="inline-flex items-center gap-x-1.5 rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-medium text-gray-600 hover:border-brand-400 hover:text-brand-500 dark:border-gray-700 dark:bg-white/[0.03] dark:text-gray-400"
                onclick={loadAll}
                disabled={isLoading}
            >
                <RefreshCcw class={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
            </button>
        </div>
    </div>

    <!-- Summary stat cards -->
    <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <!-- Hari Ini -->
        <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between mb-3">
                <p class="text-theme-xs text-gray-500 dark:text-white/60">Hari Ini</p>
                <span class="flex h-8 w-8 items-center justify-center rounded-full bg-brand-500/10">
                    <Activity class="h-4 w-4 text-brand-500" />
                </span>
            </div>
            <p class="text-3xl font-bold text-gray-800 dark:text-white/90 tabular-nums">{todayTotal()}</p>
            <p class="mt-1 text-xs text-gray-400">ekor · {todaySessions} sesi</p>
        </div>

        <!-- Bulan Ini -->
        <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between mb-3">
                <p class="text-theme-xs text-gray-500 dark:text-white/60">Bulan Ini</p>
                <span class="flex h-8 w-8 items-center justify-center rounded-full bg-success-500/10">
                    <CalendarDays class="h-4 w-4 text-success-500" />
                </span>
            </div>
            <p class="text-3xl font-bold text-gray-800 dark:text-white/90 tabular-nums">{monthTotal()}</p>
            <p class="mt-1 text-xs text-gray-400">ekor</p>
        </div>

        <!-- Tahun Ini -->
        <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between mb-3">
                <p class="text-theme-xs text-gray-500 dark:text-white/60">Tahun Ini</p>
                <span class="flex h-8 w-8 items-center justify-center rounded-full bg-warning-500/10">
                    <TrendingUp class="h-4 w-4 text-warning-500" />
                </span>
            </div>
            <p class="text-3xl font-bold text-gray-800 dark:text-white/90 tabular-nums">{yearTotal()}</p>
            <p class="mt-1 text-xs text-gray-400">ekor</p>
        </div>

        <!-- Total Sesi Hari Ini -->
        <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between mb-3">
                <p class="text-theme-xs text-gray-500 dark:text-white/60">Sesi Hari Ini</p>
                <span class="flex h-8 w-8 items-center justify-center rounded-full bg-purple-500/10">
                    <Users class="h-4 w-4 text-purple-500" />
                </span>
            </div>
            <p class="text-3xl font-bold text-gray-800 dark:text-white/90 tabular-nums">{todaySessions}</p>
            <p class="mt-1 text-xs text-gray-400">sesi</p>
        </div>
    </div>

    <!-- Live session progress bar (shown when counting is active) -->
    {#if liveSession?.running}
        <div class="rounded-2xl border border-success-200 bg-success-50 p-4 dark:border-success-800/30 dark:bg-success-500/5">
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-x-2">
                    <span class="h-2 w-2 rounded-full bg-success-500 animate-pulse"></span>
                    <span class="text-sm font-semibold text-success-700 dark:text-success-400">
                        Sesi Berjalan: {liveSession.source_name}
                    </span>
                </div>
                <span class="text-sm font-bold text-success-700 dark:text-success-400">
                    {liveSession.total_count} ekor · {liveSession.progress}%
                </span>
            </div>
            <div class="h-2 w-full rounded-full bg-success-200 dark:bg-success-800/40 overflow-hidden">
                <div
                    class="h-full rounded-full bg-success-500 transition-all duration-500"
                    style="width: {liveSession.progress}%"
                ></div>
            </div>
            <p class="mt-1 text-xs text-success-600 dark:text-success-500">
                Frame {liveSession.current_frame.toLocaleString()} / {liveSession.total_frames.toLocaleString()}
                · Model: {liveSession.model_name}
            </p>
        </div>
    {/if}

    <!-- Tabs -->
    <div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
        <!-- Tab header -->
        <div class="flex border-b border-gray-200 dark:border-gray-800">
            {#each [
                { key: 'sesi',    label: 'Per Sesi',  desc: 'realtime' },
                { key: 'harian',  label: 'Harian',    desc: '30 hari'  },
                { key: 'bulanan', label: 'Bulanan',   desc: ''         },
                { key: 'tahunan', label: 'Tahunan',   desc: ''         },
            ] as tab}
                <button
                    class={`flex flex-col items-start px-5 py-3.5 text-sm font-medium border-b-2 transition-colors
                        ${activeTab === tab.key
                            ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                            : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                        }`}
                    onclick={() => { activeTab = tab.key as typeof activeTab; }}
                >
                    {tab.label}
                    {#if tab.desc}
                        <span class="text-xs font-normal text-gray-400">{tab.desc}</span>
                    {/if}
                </button>
            {/each}
        </div>

        <!-- ── TAB: SESI ─────────────────────────────────────────────────── -->
        {#if activeTab === 'sesi'}
            <div class="p-5 flex flex-col gap-y-4">
                <!-- Controls -->
                <div class="flex items-center justify-between gap-x-3">
                    <div class="flex items-center gap-x-2">
                        <CalendarDays class="h-4 w-4 text-gray-400" />
                        <input
                            type="date"
                            bind:value={selectedDate}
                            onchange={async () => fetchSessions(selectedDate)}
                            class="rounded-lg border border-gray-200 bg-transparent px-3 py-1.5 text-sm text-gray-700 dark:border-gray-700 dark:text-gray-300"
                        />
                        <span class="text-xs text-gray-400">
                            {sessions.length} sesi ditemukan
                        </span>
                    </div>
                    <div class="flex items-center gap-x-2">
                        <span class="inline-flex items-center gap-x-1 text-xs text-success-600">
                            <span class="h-1.5 w-1.5 rounded-full bg-success-500 animate-pulse"></span>
                            Live · tiap 3 detik
                        </span>
                        <button
                            onclick={exportCSV}
                            disabled={sessions.length === 0}
                            class="inline-flex items-center gap-x-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 hover:border-brand-400 hover:text-brand-500 disabled:opacity-40 dark:border-gray-700 dark:text-gray-400"
                        >
                            <Download class="h-3.5 w-3.5" />
                            Export CSV
                        </button>
                    </div>
                </div>

                <!-- Session chart -->
                {#if sessions.length > 0}
                    <div use:renderChart={sesiChart}></div>
                {/if}

                <!-- Session table -->
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="border-b border-gray-100 dark:border-gray-800 text-left">
                                <th class="pb-3 pr-4 text-xs font-medium text-gray-400">Session ID</th>
                                <th class="pb-3 pr-4 text-xs font-medium text-gray-400">Mulai</th>
                                <th class="pb-3 pr-4 text-xs font-medium text-gray-400">Selesai</th>
                                <th class="pb-3 pr-4 text-xs font-medium text-gray-400">Durasi</th>
                                <th class="pb-3 pr-4 text-xs font-medium text-gray-400 text-right">Jumlah</th>
                                <th class="pb-3 text-xs font-medium text-gray-400">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#if sessions.length === 0}
                                <tr>
                                    <td colspan="6" class="py-10 text-center text-sm text-gray-400">
                                        Tidak ada sesi untuk tanggal ini
                                    </td>
                                </tr>
                            {:else}
                                {#each sessions as s}
                                    <tr class="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors">
                                        <td class="py-3 pr-4">
                                            <span class="font-mono text-xs text-gray-600 dark:text-gray-300">{s.session_id}</span>
                                            {#if s.status?.toLowerCase().includes('running')}
                                                <span class="ml-1.5 inline-flex items-center gap-x-1 rounded-full bg-success-500/10 px-1.5 py-0.5 text-xs text-success-600">
                                                    <span class="h-1 w-1 rounded-full bg-success-500 animate-pulse"></span>
                                                    live
                                                </span>
                                            {/if}
                                        </td>
                                        <td class="py-3 pr-4 text-xs text-gray-500">{s.start_time ?? '—'}</td>
                                        <td class="py-3 pr-4 text-xs text-gray-500">{s.stop_time ?? '—'}</td>
                                        <td class="py-3 pr-4 text-xs text-gray-500">{calcDuration(s.start_time, s.stop_time)}</td>
                                        <td class="py-3 pr-4 text-right">
                                            <span class="font-mono text-sm font-semibold text-brand-600 dark:text-brand-400">{s.chicken_total.toLocaleString()}</span>
                                            <span class="text-xs text-gray-400 ml-1">ekor</span>
                                        </td>
                                        <td class="py-3">
                                            <span class={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${statusBadge(s.status)}`}>
                                                {s.status ?? '—'}
                                            </span>
                                        </td>
                                    </tr>
                                {/each}
                            {/if}
                        </tbody>
                    </table>
                </div>
            </div>

        <!-- ── TAB: HARIAN ───────────────────────────────────────────────── -->
        {:else if activeTab === 'harian'}
            <div class="p-5 flex flex-col gap-y-4">
                <div class="flex items-center justify-between">
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                        Menampilkan {Math.min(dailySummary.length, 30)} hari terakhir
                    </p>
                    <span class="inline-flex items-center gap-x-1 text-xs text-success-600">
                        <span class="h-1.5 w-1.5 rounded-full bg-success-500 animate-pulse"></span>
                        Live · tiap 20 detik
                    </span>
                </div>

                {#if dailySummary.length === 0}
                    <p class="py-10 text-center text-sm text-gray-400">Belum ada data harian</p>
                {:else}
                    <div use:renderChart={harianChart}></div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-sm">
                            <thead>
                                <tr class="border-b border-gray-100 dark:border-gray-800 text-left">
                                    <th class="pb-3 pr-4 text-xs font-medium text-gray-400">Tanggal</th>
                                    <th class="pb-3 pr-4 text-xs font-medium text-gray-400 text-right">Jumlah Sesi</th>
                                    <th class="pb-3 text-xs font-medium text-gray-400 text-right">Total Ayam</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each dailySummary.slice(0, 30) as d}
                                    <tr class="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors">
                                        <td class="py-3 pr-4 text-sm font-medium text-gray-700 dark:text-gray-300">{d.date}</td>
                                        <td class="py-3 pr-4 text-right text-sm text-gray-500">{d.session_count}</td>
                                        <td class="py-3 text-right">
                                            <span class="font-mono text-sm font-semibold text-success-600">{d.total_chickens.toLocaleString()}</span>
                                            <span class="text-xs text-gray-400 ml-1">ekor</span>
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {/if}
            </div>

        <!-- ── TAB: BULANAN ──────────────────────────────────────────────── -->
        {:else if activeTab === 'bulanan'}
            <div class="p-5 flex flex-col gap-y-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-x-2">
                        <label class="text-sm text-gray-500">Tahun:</label>
                        <select
                            bind:value={selectedYear}
                            onchange={() => fetchMonthly(selectedYear)}
                            class="rounded-lg border border-gray-200 bg-transparent px-3 py-1.5 text-sm text-gray-700 dark:border-gray-700 dark:text-gray-300"
                        >
                            {#each yearlyData as y}
                                <option value={y.year}>{y.year}</option>
                            {/each}
                            {#if yearlyData.length === 0}
                                <option value={new Date().getFullYear()}>{new Date().getFullYear()}</option>
                            {/if}
                        </select>
                    </div>
                    <span class="inline-flex items-center gap-x-1 text-xs text-success-600">
                        <span class="h-1.5 w-1.5 rounded-full bg-success-500 animate-pulse"></span>
                        Live · tiap 2 menit
                    </span>
                </div>

                {#if monthlyData.length === 0}
                    <p class="py-10 text-center text-sm text-gray-400">Belum ada data bulanan</p>
                {:else}
                    <div use:renderChart={bulananChart}></div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-sm">
                            <thead>
                                <tr class="border-b border-gray-100 dark:border-gray-800 text-left">
                                    <th class="pb-3 pr-4 text-xs font-medium text-gray-400">Bulan</th>
                                    <th class="pb-3 pr-4 text-xs font-medium text-gray-400 text-right">Jumlah Sesi</th>
                                    <th class="pb-3 text-xs font-medium text-gray-400 text-right">Total Ayam</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each monthlyData as m}
                                    <tr class="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors">
                                        <td class="py-3 pr-4 text-sm font-medium text-gray-700 dark:text-gray-300">{m.period}</td>
                                        <td class="py-3 pr-4 text-right text-sm text-gray-500">{m.session_count}</td>
                                        <td class="py-3 text-right">
                                            <span class="font-mono text-sm font-semibold text-success-600">{m.total_chickens.toLocaleString()}</span>
                                            <span class="text-xs text-gray-400 ml-1">ekor</span>
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {/if}
            </div>

        <!-- ── TAB: TAHUNAN ──────────────────────────────────────────────── -->
        {:else if activeTab === 'tahunan'}
            <div class="p-5 flex flex-col gap-y-4">
                <div class="flex items-center justify-between">
                    <p class="text-sm text-gray-500">Rekap per tahun — semua data historis</p>
                    <span class="inline-flex items-center gap-x-1 text-xs text-success-600">
                        <span class="h-1.5 w-1.5 rounded-full bg-success-500 animate-pulse"></span>
                        Live · tiap 2 menit
                    </span>
                </div>

                {#if yearlyData.length === 0}
                    <p class="py-10 text-center text-sm text-gray-400">Belum ada data tahunan</p>
                {:else}
                    <div use:renderChart={tahunanChart}></div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-sm">
                            <thead>
                                <tr class="border-b border-gray-100 dark:border-gray-800 text-left">
                                    <th class="pb-3 pr-4 text-xs font-medium text-gray-400">Tahun</th>
                                    <th class="pb-3 pr-4 text-xs font-medium text-gray-400 text-right">Jumlah Sesi</th>
                                    <th class="pb-3 text-xs font-medium text-gray-400 text-right">Total Ayam</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each yearlyData as y}
                                    <tr class="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors">
                                        <td class="py-3 pr-4 text-sm font-semibold text-gray-700 dark:text-gray-300">{y.year}</td>
                                        <td class="py-3 pr-4 text-right text-sm text-gray-500">{y.session_count}</td>
                                        <td class="py-3 text-right">
                                            <span class="font-mono text-lg font-bold text-warning-600">{y.total_chickens.toLocaleString()}</span>
                                            <span class="text-xs text-gray-400 ml-1">ekor</span>
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>

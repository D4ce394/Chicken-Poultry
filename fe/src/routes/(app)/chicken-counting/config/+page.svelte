<script lang="ts">
    import { onMount } from 'svelte';
    import {
        Check, CheckCircle, CloudUpload, Cpu, Link,
        RefreshCcw, Trash2, Upload, X,
    } from '@lucide/svelte';
    import Breadcrumb from '../../../../components/breadcrumb/Breadcrumb.svelte';
    import {
        testStreamUrl, uploadChickenVideo, getUploadedVideos, deleteChickenModel,
        getChickenModels, uploadChickenModel,
    } from '../api';
    import type { ChickenModel, UploadedVideo } from '../api';

    // ── Stream URL ────────────────────────────────────────────────────────────
    let streamUrl: string = $state(
        typeof localStorage !== 'undefined' ? localStorage.getItem('chicken_stream_url') ?? '' : ''
    );
    let testingStream: boolean = $state(false);
    let streamTestResult: 'idle' | 'ok' | 'fail' = $state('idle');
    let streamTestMessage: string = $state('');
    let streamSaved: boolean = $state(false);

    function saveStreamUrl() {
        localStorage.setItem('chicken_stream_url', streamUrl);
        streamTestResult = 'idle';
        streamSaved = true;
        setTimeout(() => { streamSaved = false; }, 2000);
    }

    async function doTestStream() {
        if (!streamUrl) return;
        testingStream = true;
        streamTestResult = 'idle';
        streamTestMessage = '';
        const result = await testStreamUrl(streamUrl);
        streamTestResult = result.ok ? 'ok' : 'fail';
        streamTestMessage = result.message;
        testingStream = false;
    }

    // ── Upload Video ──────────────────────────────────────────────────────────
    let videoFile: File | null = $state(null);
    let videoProgress: number = $state(0);
    let videoStatus: 'idle' | 'uploading' | 'done' | 'error' = $state('idle');
    let videoMessage: string = $state('');
    let videoDragOver: boolean = $state(false);
    let uploadedVideos: UploadedVideo[] = $state([]);
    let loadingVideos: boolean = $state(false);

    async function loadVideos() {
        loadingVideos = true;
        uploadedVideos = await getUploadedVideos();
        loadingVideos = false;
    }

    function onVideoFileChange(e: Event) {
        const input = e.target as HTMLInputElement;
        if (input.files?.[0]) {
            videoFile = input.files[0];
            videoStatus = 'idle';
            videoProgress = 0;
        }
    }

    function onVideoDrop(e: DragEvent) {
        e.preventDefault();
        videoDragOver = false;
        const file = e.dataTransfer?.files?.[0];
        if (file && file.type.startsWith('video/')) {
            videoFile = file;
            videoStatus = 'idle';
            videoProgress = 0;
        }
    }

    async function submitVideo() {
        if (!videoFile) return;
        videoStatus = 'uploading';
        videoProgress = 0;
        const result = await uploadChickenVideo(videoFile, (pct) => { videoProgress = pct; });
        if (result.success) {
            videoStatus = 'done';
            videoMessage = result.message ?? `Video '${result.filename}' berhasil diupload.`;
            await loadVideos();
        } else {
            videoStatus = 'error';
            videoMessage = result.message ?? 'Upload gagal.';
        }
    }

    function clearVideo() {
        videoFile = null;
        videoStatus = 'idle';
        videoProgress = 0;
        videoMessage = '';
    }

    // ── Model management ──────────────────────────────────────────────────────
    let modelList: ChickenModel[] = $state([]);
    let loadingModels: boolean = $state(false);
    let deletingModel: string = $state('');

    async function loadModels() {
        loadingModels = true;
        modelList = await getChickenModels();
        loadingModels = false;
    }

    async function handleDeleteModel(filename: string) {
        deletingModel = filename;
        const ok = await deleteChickenModel(filename);
        if (ok) await loadModels();
        deletingModel = '';
    }

    // ── Upload Model ──────────────────────────────────────────────────────────
    let modelFile: File | null = $state(null);
    let modelName: string = $state('');
    let modelVersion: string = $state('');
    let modelDragOver: boolean = $state(false);
    let modelStatus: 'idle' | 'uploading' | 'done' | 'error' = $state('idle');
    let modelMessage: string = $state('');
    let modelProgress: number = $state(0);

    function onModelFileChange(e: Event) {
        const input = e.target as HTMLInputElement;
        if (input.files?.[0]) {
            modelFile = input.files[0];
            modelStatus = 'idle';
            modelProgress = 0;
            // Auto-fill name from filename if empty
            if (!modelName) modelName = input.files[0].name.replace(/\.[^.]+$/, '');
        }
    }

    function onModelDrop(e: DragEvent) {
        e.preventDefault();
        modelDragOver = false;
        const file = e.dataTransfer?.files?.[0];
        if (file) {
            modelFile = file;
            modelStatus = 'idle';
            modelProgress = 0;
            if (!modelName) modelName = file.name.replace(/\.[^.]+$/, '');
        }
    }

    async function submitModel() {
        if (!modelFile || !modelName) return;
        modelStatus = 'uploading';
        modelProgress = 0;
        const result = await uploadChickenModel(modelFile, modelName, modelVersion, (pct) => { modelProgress = pct; });
        if (result.success) {
            modelStatus = 'done';
            modelMessage = result.message;
            await loadModels();
        } else {
            modelStatus = 'error';
            modelMessage = result.message;
        }
    }

    function clearModel() {
        modelFile = null;
        modelName = '';
        modelVersion = '';
        modelStatus = 'idle';
        modelMessage = '';
        modelProgress = 0;
    }

    function statusModelClass(active: boolean) {
        return active ? 'bg-success-500/10 text-success-600' : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400';
    }

    onMount(async () => {
        await Promise.all([loadModels(), loadVideos()]);
    });
</script>

<div class="flex flex-col gap-y-6">
    <Breadcrumb pageName="Konfigurasi Chicken Counter" />

    <!-- Row 1: Stream URL + Upload Video -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">

        <!-- Koneksi CCTV / Stream URL -->
        <div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center gap-x-3 border-b border-gray-100 px-6 py-4 dark:border-gray-800">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500/10">
                    <Link class="h-4 w-4 text-brand-500" />
                </div>
                <h3 class="text-base font-medium text-gray-800 dark:text-white/90">Koneksi CCTV</h3>
            </div>
            <div class="flex flex-col gap-y-4 px-6 py-5">
                <div class="form-groups">
                    <span class="form-label">CCTV Stream URL</span>
                    <input
                        type="text"
                        bind:value={streamUrl}
                        placeholder="http://192.168.1.x:8080/video atau rtsp://..."
                        class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 outline-none focus:border-brand-500 dark:border-gray-700 dark:text-white/90"
                        oninput={() => { streamTestResult = 'idle'; streamTestMessage = ''; }}
                    />
                    <p class="text-theme-xs text-gray-400">
                        HTTP/MJPEG: tampil langsung di browser. RTSP: perlu media server seperti MediaMTX.
                    </p>
                </div>

                {#if streamTestResult === 'ok'}
                    <div class="flex items-center gap-x-2 rounded-lg bg-success-500/10 px-4 py-2.5">
                        <CheckCircle class="h-4 w-4 text-success-500 shrink-0" />
                        <p class="text-theme-sm text-success-600">{streamTestMessage || 'Koneksi berhasil'}</p>
                    </div>
                {:else if streamTestResult === 'fail'}
                    <div class="flex items-center gap-x-2 rounded-lg bg-error-500/10 px-4 py-2.5">
                        <X class="h-4 w-4 text-error-500 shrink-0" />
                        <p class="text-theme-sm text-error-600">{streamTestMessage || 'Koneksi gagal'}</p>
                    </div>
                {/if}

                <div class="flex items-center gap-x-2">
                    <button
                        aria-label="testConnection"
                        class="btn-secondary-outline-md"
                        onclick={doTestStream}
                        disabled={!streamUrl || testingStream}
                    >
                        <RefreshCcw class={`h-4 w-4 ${testingStream ? 'animate-spin' : ''}`} />
                        Test Koneksi
                    </button>
                    <button
                        aria-label="saveStream"
                        class="btn-primary-md"
                        onclick={saveStreamUrl}
                        disabled={!streamUrl}
                    >
                        {#if streamSaved}
                            <CheckCircle class="h-4 w-4" />
                            Tersimpan!
                        {:else}
                            <Check class="h-4 w-4" />
                            Simpan
                        {/if}
                    </button>
                </div>

                {#if streamUrl}
                    <div class="rounded-lg bg-gray-50 dark:bg-gray-800 px-4 py-3">
                        <p class="text-theme-xs text-gray-400 mb-1">URL Tersimpan</p>
                        <p class="font-mono text-theme-xs text-gray-600 dark:text-gray-300 break-all">{streamUrl}</p>
                    </div>
                {/if}
            </div>
        </div>

        <!-- Upload Video -->
        <div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center gap-x-3 border-b border-gray-100 px-6 py-4 dark:border-gray-800">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-warning-500/10">
                    <Upload class="h-4 w-4 text-warning-500" />
                </div>
                <div>
                    <h3 class="text-base font-medium text-gray-800 dark:text-white/90">Upload Video</h3>
                    <p class="text-theme-xs text-gray-400">Upload rekaman video untuk chicken counting</p>
                </div>
            </div>
            <div class="flex flex-col gap-y-4 px-6 py-5">
                <label
                    class={`flex flex-col items-center justify-center gap-y-2 rounded-xl border-2 border-dashed py-8 cursor-pointer transition-colors
                        ${videoDragOver ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/10' : 'border-gray-300 dark:border-gray-700 hover:border-brand-400'}`}
                    ondragover={(e) => { e.preventDefault(); videoDragOver = true; }}
                    ondragleave={() => { videoDragOver = false; }}
                    ondrop={onVideoDrop}
                >
                    <input type="file" accept="video/mp4,video/avi,video/mov,video/*" class="hidden" onchange={onVideoFileChange} />
                    <CloudUpload class={`h-10 w-10 ${videoDragOver ? 'text-brand-500' : 'text-gray-400'}`} />
                    {#if videoFile}
                        <p class="text-theme-sm font-medium text-gray-700 dark:text-gray-300">{videoFile.name}</p>
                        <p class="text-theme-xs text-gray-400">{(videoFile.size / 1024 / 1024).toFixed(1)} MB</p>
                    {:else}
                        <p class="text-theme-sm text-gray-500">Drag & drop atau <span class="text-brand-500 font-medium">pilih file</span></p>
                        <p class="text-theme-xs text-gray-400">MP4, AVI, MOV, MKV</p>
                    {/if}
                </label>

                {#if videoStatus === 'uploading'}
                    <div class="flex flex-col gap-y-1">
                        <div class="flex justify-between text-theme-xs text-gray-400">
                            <span>Mengunggah...</span>
                            <span>{videoProgress}%</span>
                        </div>
                        <div class="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                            <div class="bg-brand-500 h-full rounded-full transition-all" style="width: {videoProgress}%"></div>
                        </div>
                    </div>
                {/if}

                {#if videoStatus === 'done'}
                    <div class="flex items-center gap-x-2 rounded-lg bg-success-500/10 px-4 py-2.5">
                        <CheckCircle class="h-4 w-4 text-success-500 shrink-0" />
                        <p class="text-theme-sm text-success-600">{videoMessage}</p>
                    </div>
                {:else if videoStatus === 'error'}
                    <div class="flex items-center gap-x-2 rounded-lg bg-error-500/10 px-4 py-2.5">
                        <X class="h-4 w-4 text-error-500 shrink-0" />
                        <p class="text-theme-sm text-error-600">{videoMessage}</p>
                    </div>
                {/if}

                <div class="flex items-center gap-x-2">
                    <button
                        aria-label="uploadVideo"
                        class="btn-primary-md"
                        onclick={submitVideo}
                        disabled={!videoFile || videoStatus === 'uploading'}
                    >
                        <Upload class="h-4 w-4" />
                        {videoStatus === 'uploading' ? 'Mengunggah...' : 'Upload Video'}
                    </button>
                    {#if videoFile}
                        <button aria-label="clearVideo" class="btn-secondary-outline-md" onclick={clearVideo}>
                            <X class="h-4 w-4" />
                            Batal
                        </button>
                    {/if}
                </div>

                <!-- Daftar video yang sudah diupload -->
                {#if uploadedVideos.length > 0}
                    <div class="border-t border-gray-100 dark:border-gray-800 pt-3">
                        <p class="text-theme-xs font-medium text-gray-400 mb-2">Video Tersedia ({uploadedVideos.length})</p>
                        <ul class="flex flex-col gap-y-1.5 max-h-36 overflow-y-auto">
                            {#each uploadedVideos as v}
                                <li class="flex items-center justify-between rounded-lg bg-gray-50 dark:bg-gray-800 px-3 py-2">
                                    <span class="text-theme-xs text-gray-600 dark:text-gray-300 truncate max-w-[160px]">{v.name}</span>
                                    <span class="text-theme-xs text-gray-400 ml-2 shrink-0">{v.size_mb} MB</span>
                                </li>
                            {/each}
                        </ul>
                    </div>
                {:else if !loadingVideos}
                    <p class="text-theme-xs text-gray-400 text-center py-2">Belum ada video diupload.</p>
                {/if}
            </div>
        </div>
    </div>

    <!-- Row 2: Daftar Model + Upload Model -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">

        <!-- Daftar Model (dari API) -->
        <div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between border-b border-gray-100 px-6 py-4 dark:border-gray-800">
                <div class="flex items-center gap-x-3">
                    <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-success-500/10">
                        <Cpu class="h-4 w-4 text-success-500" />
                    </div>
                    <h3 class="text-base font-medium text-gray-800 dark:text-white/90">Daftar Model</h3>
                </div>
                <div class="flex items-center gap-x-2">
                    <span class="rounded-full bg-brand-500/10 px-2.5 py-0.5 text-xs font-medium text-brand-500">
                        {modelList.length} Model
                    </span>
                    <button
                        aria-label="refreshModels"
                        class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                        onclick={loadModels}
                        disabled={loadingModels}
                    >
                        <RefreshCcw class={`h-3.5 w-3.5 ${loadingModels ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>
            <div class="px-6 py-4">
                {#if loadingModels}
                    <p class="text-center text-theme-sm text-gray-400 py-6">Memuat model...</p>
                {:else if modelList.length === 0}
                    <div class="flex flex-col items-center gap-y-2 py-8 text-center">
                        <Cpu class="h-10 w-10 text-gray-300" />
                        <p class="text-theme-sm text-gray-400">Belum ada model tersedia.</p>
                        <p class="text-theme-xs text-gray-400">Upload file .pt YOLO di panel kanan.</p>
                    </div>
                {:else}
                    <table class="min-w-full">
                        <thead>
                            <tr class="border-b border-gray-100 dark:border-gray-800">
                                <th class="pb-3 text-left text-theme-xs font-medium text-gray-400">Aktif</th>
                                <th class="pb-3 text-left text-theme-xs font-medium text-gray-400">Nama Model</th>
                                <th class="pb-3 text-left text-theme-xs font-medium text-gray-400">Ukuran</th>
                                <th class="pb-3 text-left text-theme-xs font-medium text-gray-400"></th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                            {#each modelList as model}
                                <tr class="hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors">
                                    <td class="py-3.5 pr-4">
                                        <div class={`h-3 w-3 rounded-full ${model.active ? 'bg-success-500' : 'bg-gray-300 dark:bg-gray-600'}`}></div>
                                    </td>
                                    <td class="py-3.5 pr-2">
                                        <p class="text-theme-sm font-medium text-gray-700 dark:text-gray-300">{model.name}</p>
                                        <p class="font-mono text-theme-xs text-gray-400">{model.filename}</p>
                                    </td>
                                    <td class="py-3.5 pr-4">
                                        <p class="text-theme-xs text-gray-500">{model.size_mb} MB</p>
                                    </td>
                                    <td class="py-3.5">
                                        <button
                                            aria-label="deleteModel"
                                            class="rounded-lg p-1.5 text-gray-400 hover:bg-error-50 hover:text-error-500 dark:hover:bg-error-500/10 transition-colors"
                                            onclick={() => handleDeleteModel(model.filename)}
                                            disabled={deletingModel === model.filename}
                                        >
                                            {#if deletingModel === model.filename}
                                                <RefreshCcw class="h-4 w-4 animate-spin" />
                                            {:else}
                                                <Trash2 class="h-4 w-4" />
                                            {/if}
                                        </button>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                {/if}
            </div>
        </div>

        <!-- Upload Model Baru (ke API yang benar) -->
        <div class="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center gap-x-3 border-b border-gray-100 px-6 py-4 dark:border-gray-800">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-error-500/10">
                    <CloudUpload class="h-4 w-4 text-error-500" />
                </div>
                <div>
                    <h3 class="text-base font-medium text-gray-800 dark:text-white/90">Upload Model Baru</h3>
                    <p class="text-theme-xs text-gray-400">Mendukung format .pt (PyTorch / YOLO)</p>
                </div>
            </div>
            <div class="flex flex-col gap-y-4 px-6 py-5">
                <div class="grid grid-cols-2 gap-x-3">
                    <div class="form-groups">
                        <span class="form-label">Nama Model</span>
                        <input
                            type="text"
                            bind:value={modelName}
                            placeholder="Misal: chicken-v2"
                            class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 outline-none focus:border-brand-500 dark:border-gray-700 dark:text-white/90"
                        />
                    </div>
                    <div class="form-groups">
                        <span class="form-label">Versi</span>
                        <input
                            type="text"
                            bind:value={modelVersion}
                            placeholder="Misal: 1.0.0"
                            class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 outline-none focus:border-brand-500 dark:border-gray-700 dark:text-white/90"
                        />
                    </div>
                </div>

                <label
                    class={`flex flex-col items-center justify-center gap-y-2 rounded-xl border-2 border-dashed py-7 cursor-pointer transition-colors
                        ${modelDragOver ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/10' : 'border-gray-300 dark:border-gray-700 hover:border-brand-400'}`}
                    ondragover={(e) => { e.preventDefault(); modelDragOver = true; }}
                    ondragleave={() => { modelDragOver = false; }}
                    ondrop={onModelDrop}
                >
                    <input type="file" accept=".pt,.bin,.onnx" class="hidden" onchange={onModelFileChange} />
                    <CloudUpload class={`h-9 w-9 ${modelDragOver ? 'text-brand-500' : 'text-gray-400'}`} />
                    {#if modelFile}
                        <p class="text-theme-sm font-medium text-gray-700 dark:text-gray-300">{modelFile.name}</p>
                        <p class="text-theme-xs text-gray-400">{(modelFile.size / 1024 / 1024).toFixed(2)} MB</p>
                    {:else}
                        <p class="text-theme-sm text-gray-500">Drop file atau <span class="text-brand-500 font-medium">browse</span></p>
                        <p class="text-theme-xs text-gray-400">.pt / .onnx / .bin</p>
                    {/if}
                </label>

                {#if modelStatus === 'uploading'}
                    <div class="flex flex-col gap-y-1">
                        <div class="flex justify-between text-theme-xs text-gray-400">
                            <span>Mengunggah model...</span>
                            <span>{modelProgress}%</span>
                        </div>
                        <div class="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                            <div class="bg-brand-500 h-full rounded-full transition-all" style="width: {modelProgress}%"></div>
                        </div>
                    </div>
                {:else if modelStatus === 'done'}
                    <div class="flex items-center gap-x-2 rounded-lg bg-success-500/10 px-4 py-2.5">
                        <CheckCircle class="h-4 w-4 text-success-500 shrink-0" />
                        <p class="text-theme-sm text-success-600">{modelMessage}</p>
                    </div>
                {:else if modelStatus === 'error'}
                    <div class="flex items-center gap-x-2 rounded-lg bg-error-500/10 px-4 py-2.5">
                        <X class="h-4 w-4 text-error-500 shrink-0" />
                        <p class="text-theme-sm text-error-600">{modelMessage}</p>
                    </div>
                {/if}

                <div class="flex items-center gap-x-2">
                    <button
                        aria-label="uploadModel"
                        class="btn-primary-md"
                        onclick={submitModel}
                        disabled={!modelFile || !modelName || modelStatus === 'uploading'}
                    >
                        <CloudUpload class="h-4 w-4" />
                        {modelStatus === 'uploading' ? 'Mengunggah...' : 'Simpan Model'}
                    </button>
                    {#if modelFile}
                        <button aria-label="clearModel" class="btn-secondary-outline-md" onclick={clearModel}>
                            <X class="h-4 w-4" />
                            Batal
                        </button>
                    {/if}
                </div>

            </div>
        </div>
    </div>
</div>

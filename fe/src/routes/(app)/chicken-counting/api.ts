import axios from 'axios';
import { PUBLIC_BE2_URL } from '$env/static/public';
import type { ChickenSession, ChickenLatest, ChickenDailySummary } from '$lib/interfaces/chicken.interfaces';

const apiAI = axios.create({ baseURL: PUBLIC_BE2_URL || 'http://localhost:8000' });

export const BE2_BASE = PUBLIC_BE2_URL || 'http://localhost:8000';

// URL to play the processed result video (use in <video src={...}>)
export const PROCESSED_VIDEO_URL = `${BE2_BASE}/api/mobile/v1/chicken/process/video`;

// ── Firebase data endpoints ────────────────────────────────────────────────

export const getLatestCount = async (date?: string): Promise<ChickenLatest | null> => {
    try {
        const params = date ? { date } : {};
        const res = await apiAI.get('/api/mobile/v1/chicken/latest', { params });
        return res.data.data;
    } catch {
        return null;
    }
};

export const getSessions = async (date?: string): Promise<ChickenSession[]> => {
    try {
        const params = date ? { date } : {};
        const res = await apiAI.get('/api/mobile/v1/chicken/sessions', { params });
        return res.data.data ?? [];
    } catch {
        return [];
    }
};

export const getDailySummary = async (): Promise<ChickenDailySummary[]> => {
    try {
        const res = await apiAI.get('/api/mobile/v1/chicken/summary');
        return res.data.data ?? [];
    } catch {
        return [];
    }
};

// ── Counting process control ───────────────────────────────────────────────

// status: idle | running | paused | transcoding | finished | stopped | error
export interface CountingStatus {
    running: boolean;
    status: 'idle' | 'running' | 'paused' | 'transcoding' | 'finished' | 'stopped' | 'error';
    total_count: number;
    total_frames: number;
    current_frame: number;
    progress: number;      // 0–100
    fps: number;
    device: string;        // "cuda" | "cpu"
    source_name: string;
    model_name: string;
    start_time: string | null;
    stop_time: string | null;
    error_message: string;
    output_file: string | null;   // basename of result MP4
}

export const getCountingStatus = async (): Promise<CountingStatus | null> => {
    try {
        const res = await fetch(`${BE2_BASE}/api/mobile/v1/chicken/process/status`);
        if (!res.ok) return null;
        const json = await res.json();
        return json.data;
    } catch {
        return null;
    }
};

export const startCounting = async (params: {
    sourceType: 'video' | 'stream';
    sourceName: string;
    modelFilename?: string;
    lineX?: number;
    bufferWidth?: number;
}): Promise<{ success: boolean; message: string }> => {
    try {
        const form = new FormData();
        form.append('source_type', params.sourceType);
        form.append('source_name', params.sourceName);
        form.append('model_filename', params.modelFilename ?? '');
        form.append('line_x', String(params.lineX ?? 400));
        form.append('buffer_width', String(params.bufferWidth ?? 100));
        const res = await apiAI.post('/api/mobile/v1/chicken/process/start', form);
        return { success: true, message: res.data.message };
    } catch (err: any) {
        return { success: false, message: err?.response?.data?.detail ?? 'Gagal memulai counting' };
    }
};

export const pauseCounting = async (): Promise<{ success: boolean; message?: string }> => {
    try {
        const res = await apiAI.post('/api/mobile/v1/chicken/process/pause');
        return { success: true, message: res.data.message };
    } catch (err: any) {
        return { success: false, message: err?.response?.data?.detail ?? 'Gagal menjeda' };
    }
};

export const resumeCounting = async (): Promise<{ success: boolean; message?: string }> => {
    try {
        const res = await apiAI.post('/api/mobile/v1/chicken/process/resume');
        return { success: true, message: res.data.message };
    } catch (err: any) {
        return { success: false, message: err?.response?.data?.detail ?? 'Gagal melanjutkan' };
    }
};

export const stopCounting = async (): Promise<{ success: boolean; total_count?: number }> => {
    try {
        const res = await apiAI.post('/api/mobile/v1/chicken/process/stop');
        return { success: true, total_count: res.data.total_count };
    } catch {
        return { success: false };
    }
};

// ── Model management ──────────────────────────────────────────────────────

export interface ChickenModel {
    name: string;
    filename: string;
    size_mb: number;
    active: boolean;
}

export const getChickenModels = async (): Promise<ChickenModel[]> => {
    try {
        const res = await apiAI.get('/api/mobile/v1/chicken/models');
        return res.data.data ?? [];
    } catch {
        return [];
    }
};

export const uploadChickenModel = async (
    file: File,
    name: string,
    version: string,
    onProgress?: (pct: number) => void,
): Promise<{ success: boolean; message: string; filename?: string }> => {
    try {
        const form = new FormData();
        form.append('file', file);
        form.append('name', name);
        form.append('version', version);
        const res = await apiAI.post('/api/mobile/v1/chicken/models/upload', form, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (e) => {
                if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
            },
        });
        return { success: true, message: res.data.message, filename: res.data.filename };
    } catch (err: any) {
        return { success: false, message: err?.response?.data?.detail ?? 'Upload gagal' };
    }
};

export const getVideoPreviewUrl = (filename: string, lineX: number, bufferWidth: number) =>
    `${BE2_BASE}/api/mobile/v1/chicken/videos/${encodeURIComponent(filename)}/preview?line_x=${lineX}&buffer_width=${bufferWidth}`;

export interface VideoInfo {
    width: number; height: number; fps: number;
    total_frames: number; duration_seconds: number;
    suggested_line_x: number; suggested_buffer_width: number;
}
export const getVideoInfo = async (filename: string): Promise<VideoInfo | null> => {
    try {
        const res = await apiAI.get(`/api/mobile/v1/chicken/videos/${encodeURIComponent(filename)}/info`);
        return res.data.data;
    } catch { return null; }
};

export const deleteChickenModel = async (filename: string): Promise<boolean> => {
    try {
        await apiAI.delete(`/api/mobile/v1/chicken/models/${filename}`);
        return true;
    } catch {
        return false;
    }
};

// ── Video management ──────────────────────────────────────────────────────

export interface UploadedVideo {
    name: string;
    size_mb: number;
}

export const getUploadedVideos = async (): Promise<UploadedVideo[]> => {
    try {
        const res = await apiAI.get('/api/mobile/v1/chicken/videos');
        return res.data.data ?? [];
    } catch {
        return [];
    }
};

export const uploadChickenVideo = async (
    file: File,
    onProgress?: (pct: number) => void,
): Promise<{ success: boolean; filename?: string; message?: string }> => {
    try {
        const form = new FormData();
        form.append('file', file);
        const res = await apiAI.post('/api/mobile/v1/chicken/videos/upload', form, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (e) => {
                if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
            },
        });
        return { success: true, filename: res.data.filename, message: res.data.message };
    } catch (err: any) {
        return { success: false, message: err?.response?.data?.detail ?? 'Upload gagal' };
    }
};

// ── Stream URL test (via be2 proxy to avoid browser CORS) ────────────────

export const testStreamUrl = async (url: string): Promise<{ ok: boolean; message: string }> => {
    try {
        const res = await apiAI.post('/api/mobile/v1/chicken/process/test-stream', null, {
            params: { url },
        });
        return { ok: res.data.success, message: res.data.message };
    } catch (err: any) {
        return { ok: false, message: err?.response?.data?.detail ?? 'Tidak dapat terhubung ke server' };
    }
};

// ── Legacy generic video upload (kept for other features) ─────────────────

export const uploadVideo = async (
    file: File,
    onProgress?: (pct: number) => void,
): Promise<{ success: boolean; job_id?: string; message?: string }> => {
    try {
        const form = new FormData();
        form.append('video_file', file);
        form.append('model_types', 'chicken');
        form.append('frame_skip', '30');
        const res = await apiAI.post('/api/mobile/v1/video/upload', form, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (e) => {
                if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
            },
        });
        return { success: true, job_id: res.data?.job_id };
    } catch (err: any) {
        return { success: false, message: err?.response?.data?.detail ?? 'Upload gagal' };
    }
};

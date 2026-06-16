export interface ChickenSession {
    session_id: string;
    date: string;
    chicken_total: number;
    start_time: string | null;
    stop_time: string | null;
    last_update: string | null;
    status: string | null;
}

export interface ChickenLatest {
    date: string;
    session_id?: string;
    chicken_total: number;
    last_update: string | null;
    start_time: string | null;
    stop_time: string | null;
    status: string;
}

export interface ChickenDailySummary {
    date: string;
    session_count: number;
    total_chickens: number;
}

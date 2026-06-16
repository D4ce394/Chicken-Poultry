import axios from 'axios';
import { PUBLIC_API_URL } from '$env/static/public';

export const api = axios.create({
    baseURL: PUBLIC_API_URL || 'http://localhost:3000/api'
});

api.interceptors.request.use(
    (config) => {
        if (typeof window !== 'undefined') {
            const token = localStorage.getItem('accessToken');
            if (token) {
                config.headers['Authorization'] = token;
            }
        }

        config.headers['Cache-Control'] = 'no-cache';
        config.headers['Pragma'] = 'no-cache';
        config.headers['If-Modified-Since'] = '0';

        return config;
    },
    (error) => {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('accessToken');
            window.location.href = '/signin';
        }
        return Promise.reject(error);
    }
);

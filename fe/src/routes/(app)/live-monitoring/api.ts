import { api } from "$lib/axios";
import type { MonitoringFeed } from '$lib/interfaces/monitoring.interfaces'; 
import type { LiveAlert } from '$lib/interfaces/alert.interfaces'; 


export const getMonitoringFeeds = async (): Promise<MonitoringFeed[]> => {
  try {
    const res = await api.get('/monitoring/feeds'); 
    return res.data.data;
  } catch (error) {
    console.error('Failed to fetch monitoring feeds:', error);
    return [];
  }
};

export const getLiveAlerts = async (): Promise<LiveAlert[]> => {
  try {
    const res = await api.get('/alerts/live'); 
    return res.data.data;
  } catch (error) {
    console.error('Failed to fetch live alerts:', error);
    return [];
  }
};

export const getAllStream = async (): Promise<string[]> => {
  try {
    const res = await api.get('/monitoring/streams'); 
    return res.data.data;
  } catch (error) {
    console.error('Failed to fetch streams:', error);
    return [];
  }
};

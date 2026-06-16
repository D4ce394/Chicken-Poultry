export const activityTimelineChartData = {
    options: {
        chart: { type: "line" as const },
        series: [
            {
                name: 'Motion Event',
                data: [5, 2, 15, 25, 30, 20],
            },
            {
                name: 'Face Detection',
                data: [2, 1, 8, 20, 15, 10],
            },
            {
                name: 'Intrusion Alert',
                data: [0, 0, 1, 3, 2, 1],
            },
        ],
        xaxis: { categories: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
        legend: {
            position: 'top',
            horizontalAlign: 'center',
        },
    }
};

export const cameraStatusChartData = {
    options: {
        chart: { type: 'donut' as const },
        series: [35, 25, 40],
        labels: ['Online', 'Offline', 'Maintenance',],
        legend: {
            position: 'bottom',
            horizontalAlign: 'center',
        },
    }
};
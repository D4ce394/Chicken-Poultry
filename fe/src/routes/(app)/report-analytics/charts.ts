export const incidentsChartData = {
    options: {
        chart: {
            type: 'pie' as 'pie', 
        },
        series: [44, 55, 13, 43, 22],
        labels: ['Front Gate', 'Lobby', 'Parking Lot', 'Warehouse', 'Server Room'],
        legend: {
            position: 'bottom' as 'bottom',
            horizontalAlign: 'center' as 'center', 
        },
    },
};

export const securityIncidentsChartData = {
    options: {
        chart: {
            type: 'bar' as 'bar',
        },
        series: [
            {
                name: 'Incidents',
                data: [30, 40, 45, 50, 49, 60, 70, 91, 125],
            },
        ],
        xaxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
        },
        legend: {
            position: 'top' as 'top', 
            horizontalAlign: 'right' as 'right', 
        },
    },
};

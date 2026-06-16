import { Router } from 'express';
import { getLiveAlertsFromDB, getAlertHistoryFromDB, getAlertsTodayCount } from './alert.service'; 

const router = Router();

router.get('/live', async (req, res) => {
    try {
        const data = await getLiveAlertsFromDB();
        res.json({ data });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

router.get('/history', async (req, res) => {
    try {
        const { typeFilter, locationFilter, dateRangeFilter } = req.query;

        const data = await getAlertHistoryFromDB(
            typeFilter as string,
            locationFilter as string,
            dateRangeFilter as string
        );
        res.json({ data });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

router.get('/today-count', async (req, res) => {
    try {
        const count = await getAlertsTodayCount();
        res.json({ data: count });
    } catch (err) {
        console.error('getAlertsTodayCountController error:', err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

export default router;

import { Router } from 'express';
import monitoringController from './monitoring.controller';

const router = Router(); 

router.use('/', monitoringController);

export default router;

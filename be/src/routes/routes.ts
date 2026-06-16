import authRouter from '@/modules/auth/auth.routes';
import userRouter from '@/modules/user/user.routes';
import roleRouter from '@/modules/role/role.routes';
import monitoringRoutes from '@/modules/monitoring/monitoring.routes';
import alertRoutes from '@/modules/alert/alert.controller'; 

import express from 'express';

const router = express.Router();

router.use('/auth', authRouter);
router.use('/users', userRouter);
router.use('/roles', roleRouter);
router.use('/monitoring', monitoringRoutes); 
router.use('/alerts', alertRoutes); 

export default router;

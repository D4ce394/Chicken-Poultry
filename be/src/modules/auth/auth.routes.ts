import express from 'express';
import { signInController, signUpController, register } from './auth.controller';

const authRouter = express.Router();

authRouter.post('/register', signUpController); 
authRouter.post('/signin', signInController);
// authRouter.post('/signup', signUpController); 
authRouter.post('/register-manual', register); 

export default authRouter;

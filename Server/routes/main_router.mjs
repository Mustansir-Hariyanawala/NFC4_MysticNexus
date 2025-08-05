import { Router } from 'express';
import authRouter from './login_apis.mjs';
import userRouter from './user_apis.mjs';

const router = Router();

router.use(authRouter);
router.use("/users", userRouter);

export default router;
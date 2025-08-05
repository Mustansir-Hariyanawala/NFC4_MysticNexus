import express from 'express';
import AUTH_FNS from '../controllers/auth.mjs';

const router = express.Router();

// Login endpoint
router.post('/login', AUTH_FNS.login);

// Signup endpoint
router.post('/signup', AUTH_FNS.signup);

export default router;
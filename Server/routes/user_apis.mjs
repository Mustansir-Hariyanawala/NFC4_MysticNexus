import express from 'express';
import USER_FNS from '../controllers/users_controller.mjs';

const router = express.Router();

// Get all users
router.get('/', USER_FNS.getAllUsers);

// Get a single user by ID
router.get('/:id', USER_FNS.getUserById);

// Get a single user by username
router.get('/username/:username', USER_FNS.getUserByUsername);

// Create a new user
router.post('/', USER_FNS.createUser);

// Change password for a user
router.put('/change-password', USER_FNS.changePassword);

// Delete a user by ID
router.delete('/:id', USER_FNS.deleteUser);

export default router;
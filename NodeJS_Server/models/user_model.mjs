import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  email: { type: String, required: true, unique: true },
  salt: { type: String, required: true },
  passwordHash: { type: String, required: true }
}, { timestamps: true });

const User = mongoose.model('Users', userSchema);

export default User;
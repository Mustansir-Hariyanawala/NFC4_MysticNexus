import crypto from 'crypto';

/**
 * Generates a password hash and salt.
 * @param {string} username - The username.
 * @param {string} password - The password.
 * @returns {[string, string]} - An array containing the salt and the hashed password.
 */
export function generatePasswordHash(username, password) {
  const salt = crypto.randomBytes(16).toString('base64');
  const hash = crypto.pbkdf2Sync(password, salt + username + ":", 1000, 64, 'sha512').toString('base64');
  return [salt, hash];
}
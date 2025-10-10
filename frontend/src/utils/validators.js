// frontend/src/utils/validators.js

/**
 * Validates an email address format.
 * @param {string} email - The email to validate.
 * @returns {boolean} True if the email is valid, false otherwise.
 */
export const validateEmail = (email) => {
  if (!email) return false;
  // A simple regex for email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validates password strength.
 * (e.g., minimum 8 characters, at least one number)
 * @param {string} password - The password to validate.
 * @returns {{isValid: boolean, message: string}} An object indicating if the password is valid and an error message if not.
 */
export const validatePassword = (password) => {
  if (!password || password.length < 8) {
    return { isValid: false, message: 'Password must be at least 8 characters long.' };
  }
  if (!/\d/.test(password)) {
    return { isValid: false, message: 'Password must contain at least one number.' };
  }
  return { isValid: true, message: 'Password is strong.' };
};

/**
 * Checks if a value is a non-empty string.
 * @param {string} value - The value to check.
 * @returns {boolean} True if the value is a non-empty string.
 */
export const isNotEmpty = (value) => {
  return value && typeof value === 'string' && value.trim() !== '';
};
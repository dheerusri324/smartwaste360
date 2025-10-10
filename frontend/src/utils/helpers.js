// frontend/src/utils/helpers.js

/**
 * Formats a date string or Date object into a readable format.
 * @param {string | Date} date - The date to format.
 * @param {object} options - Formatting options for Intl.DateTimeFormat.
 * @returns {string} The formatted date string.
 */
export const formatDate = (date, options = { year: 'numeric', month: 'long', day: 'numeric' }) => {
  if (!date) return '';
  try {
    return new Intl.DateTimeFormat('en-US', options).format(new Date(date));
  } catch (error) {
    console.error("Failed to format date:", error);
    return 'Invalid Date';
  }
};

/**
 * Truncates a string to a specified length and adds an ellipsis.
 * @param {string} text - The text to truncate.
 * @param {number} maxLength - The maximum length of the string.
 * @returns {string} The truncated string.
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text || text.length <= maxLength) {
    return text;
  }
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Generates initials from a full name.
 * @param {string} name - The full name.
 * @returns {string} The initials (e.g., "Saanvi Dheeraj" -> "SD").
 */
export const getInitials = (name = '') => {
  if (!name) return '?';
  const nameParts = name.trim().split(' ');
  if (nameParts.length > 1) {
    return `${nameParts[0][0]}${nameParts[nameParts.length - 1][0]}`.toUpperCase();
  }
  return name.substring(0, 2).toUpperCase();
};
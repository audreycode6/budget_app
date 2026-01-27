/**
 * Formats a number as USD currency
 * @param {number} num - The number to format
 * @returns {string} Formatted currency string (e.g "$1,234.56")
 */
export function formatFloatToUSD(num) {
  return `$${Number(num)
    .toFixed(2)
    .replace(/\d(?=(\d{3})+\.)/g, '$&,')}`;
}

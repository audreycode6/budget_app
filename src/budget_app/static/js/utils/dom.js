/**
 * Create a DOM element with options and children.
 * @param {string} tag - HTML tag name (e.g., 'div', 'button')
 * @param {object} options - Element attributes and special keys:
 *   - class: Sets className (can be space-separated string)
 *   - text: Sets textContent (alternative to passing string children)
 *   - data-*: Sets data attributes
 *   - Any other key becomes an attribute
 * @param {Array} children - Child nodes (DOM elements, strings as text nodes, or DocumentFragment)
 * @returns {Element} The created DOM element
 */
export function el(tag, options = {}, children = []) {
  const element = document.createElement(tag);

  Object.entries(options).forEach(([key, value]) => {
    if (key === 'class') {
      element.className = value;
    } else if (key === 'text') {
      element.textContent = value;
    } else if (key.startsWith('data-')) {
      element.setAttribute(key, value);
    } else {
      element.setAttribute(key, value);
    }
  });

  // Handle text nodes, DOM elements, and fragments
  children.forEach((child) => {
    if (typeof child === 'string') {
      // Convert strings to text nodes to prevent XSS
      element.appendChild(document.createTextNode(child));
    } else if (child instanceof Node || child instanceof DocumentFragment) {
      // Append DOM nodes and fragments as-is
      element.appendChild(child);
    }
  });

  return element;
}

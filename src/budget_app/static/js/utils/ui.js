/**
 * Displays or hides error message by element ID with Bootstrap alert styling
 * @param {string} elementId - The error element ID
 * @param {string} message - Error message to display (or empty to hide)
 * @param {string} type - Bootstrap alert type: 'danger', 'warning', 'success', 'info' (default: 'danger')
 */
export function displayError(elementId, message = '', type = 'danger') {
  const errorEl = document.getElementById(elementId);
  if (!errorEl) return;

  if (message) {
    errorEl.textContent = message;
    errorEl.className = `alert alert-${type}`;
    errorEl.setAttribute('role', 'alert');
    errorEl.style.display = 'block';
  } else {
    errorEl.style.display = 'none';
  }
}

/**
 * Sets disabled state on form submit button with optional text change
 * @param {HTMLFormElement} form - The form element
 * @param {boolean} disabled - Whether to disable the button
 * @param {Object} options - Configuration options
 * @param {string} options.loadingText - Text to show while loading (e.g., "Saving...")
 * @param {string} options.defaultText - Default button text to restore
 */
export function setFormDisabled(form, disabled, options = {}) {
  const submitBtn = form?.querySelector('[type="submit"]');
  if (!submitBtn) return;

  submitBtn.disabled = disabled;
  if (disabled) {
    submitBtn.setAttribute('aria-busy', 'true');
    submitBtn.dataset.originalText = submitBtn.textContent;
    if (options.loadingText) {
      submitBtn.textContent = options.loadingText;
    }
  } else {
    submitBtn.removeAttribute('aria-busy');
    submitBtn.textContent =
      submitBtn.dataset.originalText || options.defaultText || 'Submit';
  }
}

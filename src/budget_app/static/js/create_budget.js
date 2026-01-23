/* =========================================================
   Constants
========================================================= */
const ELEMENT_IDS = {
  FORM: 'create-budget-form',
  NAME: 'name',
  GROSS_INCOME: 'gross_income',
  MONTH_DURATION: 'month_duration',
  ERROR: 'error',
};

const API_ENDPOINTS = {
  CREATE_BUDGET: '/api/budget/create',
};

/* =========================================================
   Utilities
========================================================= */

/**
 * Displays or hides error message
 * @param {string} message - Error message to display (or empty to hide)
 */
function displayError(message = '') {
  const errorEl = document.getElementById(ELEMENT_IDS.ERROR);
  if (!errorEl) return;

  if (message) {
    errorEl.textContent = message;
    errorEl.style.display = 'block';
  } else {
    errorEl.style.display = 'none';
  }
}

/**
 * Sets disabled state on form submit button
 * @param {HTMLFormElement} form - The form element
 * @param {boolean} disabled - Whether to disable the button
 */
function setFormDisabled(form, disabled) {
  const submitBtn = form?.querySelector('[type="submit"]');
  if (!submitBtn) return;

  submitBtn.disabled = disabled;
  if (disabled) {
    submitBtn.setAttribute('aria-busy', 'true');
    submitBtn.dataset.originalText = submitBtn.textContent;
    submitBtn.textContent = 'Creating...';
  } else {
    submitBtn.removeAttribute('aria-busy');
    submitBtn.textContent = submitBtn.dataset.originalText || 'Create Budget';
  }
}

/* =========================================================
   Form Submission
========================================================= */

/**
 * Handles budget creation form submission
 */
async function handleCreateBudget(e) {
  e.preventDefault();

  const form = e.target;
  const formData = {
    name: document.getElementById(ELEMENT_IDS.NAME).value,
    gross_income: document.getElementById(ELEMENT_IDS.GROSS_INCOME).value,
    month_duration: document.getElementById(ELEMENT_IDS.MONTH_DURATION).value,
  };

  // Show loading state
  setFormDisabled(form, true);
  displayError(); // Clear previous errors

  try {
    const response = await fetch(API_ENDPOINTS.CREATE_BUDGET, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Budget creation failed');
    }

    const budgetId = data?.budget?.id;
    if (!budgetId) {
      throw new Error('Missing budget ID in response');
    }

    window.location.href = `/budget/${budgetId}`;
  } catch (err) {
    console.error('Create budget failed:', err);
    displayError(err.message || 'Failed to create budget');
    setFormDisabled(form, false);
  }
}

/* =========================================================
   Initialization
========================================================= */

/**
 * Initializes the create budget form
 */
function initializeForm() {
  const form = document.getElementById(ELEMENT_IDS.FORM);
  if (!form) return;

  form.addEventListener('submit', handleCreateBudget);
}

document.addEventListener('DOMContentLoaded', initializeForm);

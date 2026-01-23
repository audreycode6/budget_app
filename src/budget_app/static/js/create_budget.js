import { displayError, setFormDisabled } from './utils/ui.js';

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
  setFormDisabled(form, true, {
    loadingText: 'Creating...',
    defaultText: 'Create Budget',
  });
  displayError(ELEMENT_IDS.ERROR); // Clear previous errors

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
    displayError(ELEMENT_IDS.ERROR, err.message || 'Failed to create budget');
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

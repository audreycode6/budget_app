import { getBudgetIdFromUrl } from './utils/url.js';
import { displayError, setFormDisabled } from './utils/ui.js';

/* =========================================================
   Constants
========================================================= */
const ELEMENT_IDS = {
  FORM: 'edit-budget-form',
  NAME: 'name',
  GROSS_INCOME: 'gross_income_raw',
  MONTH_DURATION: 'month_duration',
  CANCEL_LINK: 'cancel-link',
  ERROR: 'error',
};

const API_ENDPOINTS = {
  BUDGET: '/api/budget',
  EDIT_BUDGET: '/api/budget/edit',
};

const PAGE_ROUTES = {
  BUDGET: '/budget',
};

/* =========================================================
   Budget Loading
========================================================= */

/**
 * Loads budget data and populates form
 */
async function loadBudgetForEdit() {
  const budgetId = getBudgetIdFromUrl();

  if (!budgetId) {
    displayError(ELEMENT_IDS.ERROR, 'Invalid budget URL');
    return;
  }

  try {
    const res = await fetch(`${API_ENDPOINTS.BUDGET}/${budgetId}`, {
      credentials: 'include',
    });

    if (!res.ok) {
      throw new Error('Failed to load budget');
    }

    const { budget } = await res.json();

    // Populate form fields
    const nameEl = document.getElementById(ELEMENT_IDS.NAME);
    const grossIncomeEl = document.getElementById(ELEMENT_IDS.GROSS_INCOME);
    const durationEl = document.getElementById(ELEMENT_IDS.MONTH_DURATION);
    const cancelLinkEl = document.getElementById(ELEMENT_IDS.CANCEL_LINK);

    if (nameEl) nameEl.value = budget.name;
    if (grossIncomeEl) grossIncomeEl.value = budget.gross_income_raw;
    if (durationEl) durationEl.value = budget.month_duration;
    if (cancelLinkEl) cancelLinkEl.href = `${PAGE_ROUTES.BUDGET}/${budgetId}`;
  } catch (err) {
    console.error('Failed to load budget:', err);
    displayError(ELEMENT_IDS.ERROR, err.message || 'Failed to load budget');
  }
}

/* =========================================================
   Form Submission
========================================================= */

/**
 * Handles budget edit form submission
 */
async function handleEditBudget(e) {
  e.preventDefault();

  const form = e.target;
  const budgetId = getBudgetIdFromUrl();

  if (!budgetId) {
    displayError(ELEMENT_IDS.ERROR, 'Invalid budget URL');
    return;
  }

  const body = {
    budget_id: budgetId,
    name: document.getElementById(ELEMENT_IDS.NAME).value,
    gross_income: parseFloat(
      document.getElementById(ELEMENT_IDS.GROSS_INCOME).value
    ),
    month_duration: document.getElementById(ELEMENT_IDS.MONTH_DURATION).value,
  };

  // Show loading state
  setFormDisabled(form, true, {
    loadingText: 'Saving...',
    defaultText: 'Save Changes',
  });
  displayError(ELEMENT_IDS.ERROR); // Clear previous errors

  try {
    const res = await fetch(API_ENDPOINTS.EDIT_BUDGET, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.message || 'Failed to update budget');
    }

    window.location.href = `${PAGE_ROUTES.BUDGET}/${budgetId}`;
  } catch (err) {
    console.error('Edit budget failed:', err);
    displayError(ELEMENT_IDS.ERROR, err.message || 'Failed to update budget');
    setFormDisabled(form, false);
  }
}

/* =========================================================
   Initialization
========================================================= */

/**
 * Initializes the edit budget page
 */
function initializeEditPage() {
  const form = document.getElementById(ELEMENT_IDS.FORM);
  if (!form) return;

  loadBudgetForEdit();
  form.addEventListener('submit', handleEditBudget);
}

document.addEventListener('DOMContentLoaded', initializeEditPage);

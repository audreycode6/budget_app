import { el } from './utils/dom.js';
import { displayError } from './utils/ui.js';

/* =========================================================
   Constants
========================================================= */
const ELEMENT_IDS = {
  BUDGETS_LIST: 'budgets-list',
  EMPTY_MESSAGE: 'empty_budgets',
  ERROR: 'error',
};

/* =========================================================
   Utilities
========================================================= */

/**
 * Creates a budget list item row
 * @param {Object} budget - Budget object with id and name
 * @returns {HTMLElement} Budget row element
 */
function createBudgetRow(budget) {
  const info = el('div', {}, [
    el('div', { class: 'fw-semibold', text: budget.name }),
  ]);

  const actions = el('div', {}, [
    el('a', {
      href: `/budget/${encodeURIComponent(budget.id)}`,
      class: 'btn btn-sm btn-outline-primary',
      'aria-label': `View budget ${budget.name}`,
      text: 'View',
    }),
  ]);

  return el(
    'div',
    {
      class:
        'list-group-item d-flex justify-content-between align-items-center',
    },
    [info, actions],
  );
}

/**
 * Displays or hides empty state message
 * @param {boolean} show - Whether to show the empty message
 */
function displayEmptyState(show) {
  const emptyEl = document.getElementById(ELEMENT_IDS.EMPTY_MESSAGE);
  if (emptyEl) {
    emptyEl.style.display = show ? 'inline' : 'none';
  }
}

/**
 * Sets up click handler for create budget button
 */
function setupCreateBudgetButton() {
  const createBtn = document.getElementById('create-budget-btn');
  if (!createBtn) return;
  createBtn.addEventListener('click', () => {
    window.location.href = '/create_budget';
  });
}

document.addEventListener('DOMContentLoaded', setupCreateBudgetButton);

/* =========================================================
   Budget Loading
========================================================= */

/**
 * Loads and displays all budgets for the current user
 */
async function loadBudgets() {
  const list = document.getElementById(ELEMENT_IDS.BUDGETS_LIST);
  if (!list) return;

  try {
    displayError(ELEMENT_IDS.ERROR); // Clear previous errors

    const response = await fetch('/api/budgets', { credentials: 'include' });

    const data = await response.json();
    const { budgets } = data;

    list.innerHTML = '';

    if (!response.ok) {
      throw new Error(
        data.message || `Failed to load budgets (${response.status})`,
      );
    }

    // Handle empty state
    if (!budgets || budgets.length === 0) {
      displayEmptyState(true);
      return;
    }

    displayEmptyState(false);

    // Render budget rows
    budgets.forEach((budget) => {
      const row = createBudgetRow(budget);
      list.appendChild(row);
    });
  } catch (err) {
    console.error('Failed to load budgets:', err);
    displayError(ELEMENT_IDS.ERROR, err.message || 'Failed to load budgets');
  }
}

document.addEventListener('DOMContentLoaded', loadBudgets);

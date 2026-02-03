import { el } from './utils/dom.js';
import { displayError } from './utils/ui.js';
import { formatFloatToUSD } from './utils/format_currency.js';

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
 * Creates a budget card element
 * @param {Object} budget - Budget object with id and name
 * @returns {HTMLElement} Budget card wrapper element
 */
function createBudgetRow(budget) {
  const cardBody = el('div', { class: 'card-body d-flex flex-column' }, [
    el('h5', { class: 'card-title', text: budget.name }),
    el('p', {
      class: 'card-text text-muted flex-grow-1',
      text: `Gross Income: ${formatFloatToUSD(budget.gross_income)}`,
    }),
    el('a', {
      href: `/budget/${encodeURIComponent(budget.id)}`,
      class: 'btn btn-outline-primary mt-auto',
      text: 'View Budget',
    }),
  ]);

  const card = el('div', { class: 'card h-100 shadow-sm' }, [cardBody]);
  return el('div', { class: 'col-12 col-md-6 col-lg-4' }, [card]);
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

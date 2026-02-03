import { getBudgetIdFromUrl } from './utils/url.js';
import { fetchBudget } from './services/budget_api.js';
import {
  buildCategoryAccordion,
  groupItemsByCategory,
} from './components/budget_categories.js';
import {
  restoreAccordionState,
  bindAccordionPersistence,
} from './components/accordion_state.js';
import { bindItemActions } from './components/item_actions.js';
import { setupEditItemModal } from './modals/edit_item_modal.js';
import { formatCategoryLabel } from './components/budget_categories.js';
import { formatFloatToUSD } from './utils/format_currency.js';
import { getTotalExpenses, calculateNetIncome } from './utils/net_income.js';
import { displayError } from './utils/ui.js';

/* =========================================================
   Constants
========================================================= */
const ELEMENT_IDS = {
  BUDGET_TITLE: 'budget-title',
  BUDGET_GROSS: 'budget-gross',
  BUDGET_DURATION: 'budget-duration',
  BUDGET_ERROR: 'error',
  BUDGET_CATEGORIES: 'budget-categories',
  EMPTY_MESSAGE: 'empty-budget-items',
  NET_INCOME_DIV: 'net-income',
  NET_INCOME: 'budget-net-income',
  EDIT_BUDGET_BTN: 'edit-budget-btn',
  DELETE_BUDGET_BTN: 'delete-budget-btn',
  ADD_ITEM_FORM: 'add-item-form',
  ADD_ITEM_MODAL: 'addItemModal',
  ADD_ITEM_ERROR: 'add-item-error',
  ADD_ITEM_MODAL_CONTAINER: 'add-item-modal-container',
  EDIT_ITEM_MODAL_CONTAINER: 'edit-item-modal-container',
  EDIT_ITEM_MODAL: 'editItemModal',
  ITEM_CATEGORY: 'item-category',
  ITEM_NAME: 'item-name',
  ITEM_TOTAL: 'item-total',
  EDIT_ITEM_ID: 'edit-item-id',
  EDIT_ITEM_NAME: 'edit-item-name',
  EDIT_ITEM_TOTAL: 'edit-item-total',
  EDIT_ITEM_CATEGORY: 'edit-item-category',
};

const API_ENDPOINTS = {
  BUDGET: '/api/budget',
  CATEGORIES: '/api/budget/item/categories',
  CREATE_ITEM: '/api/budget/item/create',
  DELETE_ITEM: '/api/budget/item/delete',
  DELETE_BUDGET: '/api/budget/delete',
};

const PARTIAL_URLS = {
  ADD_ITEM_MODAL: '/static/partials/add_item_modal.html',
  EDIT_ITEM_MODAL: '/static/partials/edit_item_modal.html',
};

/* =========================================================
   Utilities
========================================================= */

/**
 * Safely retrieves a DOM element by ID with warning if not found
 * @param {string} id - The element ID
 * @returns {HTMLElement | null}
 */
function getElement(id) {
  const el = document.getElementById(id);
  if (!el) {
    console.warn(`Element not found: ${id}`);
  }
  return el;
}

/**
 * Sets disabled state on buttons and form elements
 * @param {HTMLElement | null} element - The element to enable/disable
 * @param {boolean} disabled - Whether to disable the element
 */
function setElementDisabled(element, disabled) {
  if (!element) return;
  element.disabled = disabled;
  if (disabled) {
    element.setAttribute('aria-busy', 'true');
  } else {
    element.removeAttribute('aria-busy');
  }
}

async function loadBudget() {
  try {
    const budgetId = getBudgetIdFromUrl();
    if (!budgetId) {
      throw new Error('Invalid budget ID');
    }

    const payload = await fetchBudget(budgetId);
    const budget = payload?.budget ?? payload;

    const errorEl = getElement(ELEMENT_IDS.BUDGET_ERROR);
    const emptyMsg = getElement(ELEMENT_IDS.EMPTY_MESSAGE);
    const netIncomeDiv = getElement(ELEMENT_IDS.NET_INCOME_DIV);
    const netIncomeEl = getElement(ELEMENT_IDS.NET_INCOME);
    const categoriesContainer = getElement(ELEMENT_IDS.BUDGET_CATEGORIES);

    // Clear any previous errors
    displayError(errorEl);

    // Update header/meta
    const titleEl = getElement(ELEMENT_IDS.BUDGET_TITLE);
    const grossEl = getElement(ELEMENT_IDS.BUDGET_GROSS);
    const durationEl = getElement(ELEMENT_IDS.BUDGET_DURATION);

    if (titleEl) titleEl.textContent = `Budget: "${budget.name}"`;
    if (grossEl) grossEl.textContent = formatFloatToUSD(budget.gross_income);
    if (durationEl) durationEl.textContent = String(budget.month_duration);

    categoriesContainer.innerHTML = '';

    // Handle empty state
    if (!budget.items || budget.items.length === 0) {
      if (emptyMsg)
        ((emptyMsg.style.display = 'block'),
          (netIncomeDiv.style.display = 'none'));
      return;
    }

    if (emptyMsg)
      ((emptyMsg.style.display = 'none'),
        (netIncomeDiv.style.display = 'block'));

    // Calculate and display net income
    const totalExpenses = getTotalExpenses(budget);
    const { netIncome, isInNegative } = calculateNetIncome(
      budget.gross_income,
      totalExpenses,
    );

    if (netIncomeEl) {
      netIncomeEl.textContent = formatFloatToUSD(netIncome);
      netIncomeEl.style.color = isInNegative ? 'red' : 'green';
    }

    // Build category accordions
    const grouped = groupItemsByCategory(budget.items);

    Object.entries(grouped).forEach(([category, data]) => {
      const accordion = buildCategoryAccordion({ category, data });
      categoriesContainer.appendChild(accordion);

      const collapseEl = accordion.querySelector('.accordion-collapse');
      restoreAccordionState({ budgetId, category, collapseEl });
      bindAccordionPersistence({ budgetId, category, collapseEl });
    });

    // Bind item actions (edit/delete)
    bindItemActions({
      container: categoriesContainer,
      budgetId,
      onRefresh: loadBudget,
      onEdit: async (dataset) => {
        await populateCategorySelect(
          ELEMENT_IDS.EDIT_ITEM_CATEGORY,
          dataset.itemCategory,
        );

        getElement(ELEMENT_IDS.EDIT_ITEM_ID).value = dataset.itemId ?? '';
        getElement(ELEMENT_IDS.EDIT_ITEM_NAME).value = dataset.itemName ?? '';
        getElement(ELEMENT_IDS.EDIT_ITEM_TOTAL).value = dataset.itemTotal ?? '';

        const modalEl = getElement(ELEMENT_IDS.EDIT_ITEM_MODAL);
        bootstrap.Modal.getOrCreateInstance(modalEl).show();
      },
    });
  } catch (err) {
    window.location.href = '/not_found';
    console.error('Failed to load budget:', err);
    const errorEl = getElement(ELEMENT_IDS.BUDGET_ERROR);
    displayError(errorEl, err.message || 'Failed to load budget');
  }
}

/* =========================================================
   Budget Actions (Edit/Delete)
========================================================= */

/**
 * Sets up click handler for edit budget button
 */
function setupEditBudgetButton() {
  const editBtn = getElement(ELEMENT_IDS.EDIT_BUDGET_BTN);
  if (!editBtn) return;

  editBtn.addEventListener('click', () => {
    const budgetId = getBudgetIdFromUrl();
    if (!budgetId) {
      alert('Invalid budget.');
      return;
    }
    window.location.href = `/budget/${budgetId}/edit`;
  });
}

/**
 * Sets up click handler for delete budget button with confirmation
 */
function setupDeleteBudgetButton() {
  const deleteBtn = getElement(ELEMENT_IDS.DELETE_BUDGET_BTN);
  if (!deleteBtn) return;

  deleteBtn.addEventListener('click', async () => {
    const budgetId = getBudgetIdFromUrl();

    if (!budgetId) {
      alert('Invalid budget.');
      return;
    }

    const confirmed = window.confirm(
      'Are you sure you want to delete this budget?\n\nThis action cannot be undone.',
    );

    if (!confirmed) return;

    setElementDisabled(deleteBtn, true);
    const originalText = deleteBtn.textContent;
    deleteBtn.textContent = 'Deleting...';

    try {
      const res = await fetch(API_ENDPOINTS.DELETE_BUDGET, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ budget_id: budgetId }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.message || 'Failed to delete budget');
      }

      window.location.href = '/budgets';
    } catch (err) {
      console.error('Delete budget failed:', err);
      displayError(
        ELEMENT_IDS.BUDGET_ERROR,
        err.message || 'Failed to delete budget',
      );
      setElementDisabled(deleteBtn, false);
      deleteBtn.textContent = originalText;
    }
  });
}

/* =========================================================
   Category Management
========================================================= */
/**
 * Fetches available budget categories from the API
 * @returns {Promise<Array<string>>}
 * @throws {Error} if fetch fails
 */
async function fetchCategoriesFromApi() {
  try {
    const res = await fetch(API_ENDPOINTS.CATEGORIES, {
      credentials: 'include',
    });
    if (!res.ok) throw new Error('Failed to load categories');
    const payload = await res.json();
    return Array.isArray(payload) ? payload : payload.categories;
  } catch (err) {
    console.error('Fetch categories failed:', err);
    throw err;
  }
}

/**
 * Populates a category select element with options.
 * @param {string} selectId - The ID of the select element
 * @param {string} selectedCategory - The category to pre-select (optional)
 */
async function populateCategorySelect(selectId, selectedCategory = null) {
  const select = getElement(selectId);
  if (!select) return;

  try {
    const categories = await fetchCategoriesFromApi();

    // Remove old options except placeholder
    select
      .querySelectorAll('option:not(:first-child)')
      .forEach((o) => o.remove());

    categories.forEach((cat) => {
      const opt = document.createElement('option');
      opt.value = cat;
      opt.textContent = formatCategoryLabel(cat);

      if (cat === selectedCategory) {
        opt.selected = true;
      }

      select.appendChild(opt);
    });
  } catch (err) {
    console.error('Failed to populate category select:', err);
  }
}

/* =========================================================
   Modal Loading & Setup
========================================================= */

/**
 * Loads the add item modal HTML partial
 * @returns {Promise<void>}
 */
async function loadAddItemModalPartial() {
  const container = getElement(ELEMENT_IDS.ADD_ITEM_MODAL_CONTAINER);
  if (!container) return;

  try {
    const res = await fetch(PARTIAL_URLS.ADD_ITEM_MODAL);
    if (!res.ok) throw new Error('Failed to load add item modal');
    container.innerHTML = await res.text();
  } catch (err) {
    console.error('Failed to load add item modal:', err);
  }
}

/**
 * Loads the edit item modal HTML partial
 * @returns {Promise<void>}
 */
async function loadEditItemModalPartial() {
  const container = getElement(ELEMENT_IDS.EDIT_ITEM_MODAL_CONTAINER);
  if (!container) return;

  try {
    const res = await fetch(PARTIAL_URLS.EDIT_ITEM_MODAL);
    if (!res.ok) throw new Error('Failed to load edit item modal');
    container.innerHTML = await res.text();
  } catch (err) {
    console.error('Failed to load edit item modal:', err);
  }
}

function setupAddItemModal() {
  const form = getElement(ELEMENT_IDS.ADD_ITEM_FORM);
  const modalEl = getElement(ELEMENT_IDS.ADD_ITEM_MODAL);
  const errorEl = getElement(ELEMENT_IDS.ADD_ITEM_ERROR);
  const submitBtn = form?.querySelector('[type="submit"]');

  if (!form || !modalEl) return;

  modalEl.addEventListener('show.bs.modal', async () => {
    displayError(errorEl);
    await populateCategorySelect(ELEMENT_IDS.ITEM_CATEGORY);
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const budgetId = getBudgetIdFromUrl();
    if (!budgetId) return;

    const payload = {
      budget_id: budgetId,
      category: getElement(ELEMENT_IDS.ITEM_CATEGORY).value,
      name: getElement(ELEMENT_IDS.ITEM_NAME).value.trim(),
      total: Number(getElement(ELEMENT_IDS.ITEM_TOTAL).value),
    };

    // Disable submit and show loading state
    setElementDisabled(submitBtn, true);
    if (submitBtn) submitBtn.textContent = 'Adding...';
    displayError(errorEl);

    try {
      const res = await fetch(API_ENDPOINTS.CREATE_ITEM, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || 'Failed to add item');
      }

      bootstrap.Modal.getInstance(modalEl).hide();
      form.reset();
      await loadBudget();
    } catch (err) {
      console.error('Add item failed:', err);
      displayError(errorEl, err.message || 'Failed to add item');
    } finally {
      setElementDisabled(submitBtn, false);
      if (submitBtn) submitBtn.textContent = 'Add item';
    }
  });
}

/* =========================================================
   Initialization
========================================================= */

/**
 * Initializes all budget page functionality
 * Loads modals, sets up event handlers, and fetches budget data
 */
async function initializeBudgetPage() {
  const budgetId = getBudgetIdFromUrl();
  if (!budgetId) {
    console.error('No budget ID found in URL');
    return;
  }

  try {
    // Load modal partials in parallel
    await Promise.all([loadAddItemModalPartial(), loadEditItemModalPartial()]);

    // Setup all event listeners
    setupEditBudgetButton();
    setupDeleteBudgetButton();
    setupAddItemModal();
    setupEditItemModal({ budgetId, onSuccess: loadBudget });

    // Load initial budget data
    await loadBudget();
  } catch (err) {
    console.error('Failed to initialize budget page:', err);
  }
}

document.addEventListener('DOMContentLoaded', initializeBudgetPage);

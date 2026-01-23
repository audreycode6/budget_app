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

/* =========================================================
   Constants
========================================================= */
const ELEMENT_IDS = {
  BUDGET_TITLE: 'budget-title',
  BUDGET_GROSS: 'budget-gross',
  BUDGET_DURATION: 'budget-duration',
  BUDGET_ERROR: 'budget-error',
  BUDGET_CATEGORIES: 'budget-categories',
  EMPTY_MESSAGE: 'empty-budget-items',
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
  EDIT_ITEM_CATEGORY: 'edit-item-category',
};

const API_ENDPOINTS = {
  BUDGET: '/api/budget',
  CATEGORIES: '/api/budget/item/categories',
  CREATE_ITEM: '/api/budget/item/create',
  DELETE_ITEM: '/api/budget/item/delete',
};

const PARTIAL_URLS = {
  ADD_ITEM_MODAL: '/static/partials/add_item_modal.html',
  EDIT_ITEM_MODAL: '/static/partials/edit_item_modal.html',
};

/* =========================================================
   Utilities
========================================================= */
function formatCategoryLabel(cat) {
  return String(cat)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function getElement(id) {
  const el = document.getElementById(id);
  if (!el) {
    console.warn(`Element not found: ${id}`);
  }
  return el;
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
    const categoriesContainer = getElement(ELEMENT_IDS.BUDGET_CATEGORIES);

    // Clear any previous errors
    if (errorEl) errorEl.style.display = 'none';

    // Update header/meta
    const titleEl = getElement(ELEMENT_IDS.BUDGET_TITLE);
    const grossEl = getElement(ELEMENT_IDS.BUDGET_GROSS);
    const durationEl = getElement(ELEMENT_IDS.BUDGET_DURATION);

    if (titleEl) titleEl.textContent = `Budget: "${budget.name}"`;
    if (grossEl) grossEl.textContent = budget.gross_income;
    if (durationEl) durationEl.textContent = String(budget.month_duration);

    categoriesContainer.innerHTML = '';

    // Handle empty state
    if (!budget.items || budget.items.length === 0) {
      if (emptyMsg) emptyMsg.style.display = 'block';
      return;
    }

    if (emptyMsg) emptyMsg.style.display = 'none';

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
          dataset.itemCategory
        );

        getElement(ELEMENT_IDS.EDIT_ITEM_MODAL).value = dataset.itemId ?? '';
        getElement(ELEMENT_IDS.ITEM_NAME).value = dataset.itemName ?? '';
        getElement(ELEMENT_IDS.ITEM_TOTAL).value = dataset.itemTotal ?? '';

        const modalEl = getElement(ELEMENT_IDS.EDIT_ITEM_MODAL);
        bootstrap.Modal.getOrCreateInstance(modalEl).show();
      },
    });
  } catch (err) {
    console.error('Failed to load budget:', err);
    const errorEl = getElement(ELEMENT_IDS.BUDGET_ERROR);
    if (errorEl) {
      errorEl.textContent = err.message || 'Failed to load budget';
      errorEl.style.display = 'block';
    }
  }
}

/* =========================================================
   Budget Actions (Edit/Delete)
========================================================= */
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
      'Are you sure you want to delete this budget?\n\nThis action cannot be undone.'
    );

    if (!confirmed) return;

    try {
      const res = await fetch(API_ENDPOINTS.DELETE_ITEM, {
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
      alert(err.message || 'Failed to delete budget.');
    }
  });
}

/* =========================================================
   Category Management
========================================================= */
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

  if (!form || !modalEl) return;

  modalEl.addEventListener('show.bs.modal', async () => {
    if (errorEl) errorEl.style.display = 'none';
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
      if (errorEl) {
        errorEl.textContent = err.message || 'Failed to add item';
        errorEl.style.display = 'block';
      }
    }
  });
}

/* =========================================================
   Initialization
========================================================= */
document.addEventListener('DOMContentLoaded', async () => {
  const budgetId = getBudgetIdFromUrl();
  if (!budgetId) {
    console.error('No budget ID found in URL');
    return;
  }

  // Load modal partials in parallel
  await Promise.all([loadAddItemModalPartial(), loadEditItemModalPartial()]);

  // Setup all event listeners
  setupEditBudgetButton();
  setupDeleteBudgetButton();
  setupAddItemModal();
  setupEditItemModal({ budgetId, onSuccess: loadBudget });

  // Load initial budget data
  await loadBudget();
});

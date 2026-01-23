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

function formatCategoryLabel(cat) {
  return String(cat)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

async function loadBudget() {
  const budgetId = getBudgetIdFromUrl();
  const payload = await fetchBudget(budgetId);
  const budget = payload?.budget ?? payload;

  const errorEl = document.getElementById('budget-error');
  const emptyMsg = document.getElementById('empty-budget-items');
  const categoriesContainer = document.getElementById('budget-categories');

  // header/meta
  document.getElementById(
    'budget-title'
  ).textContent = `Budget: "${budget.name}"`;
  document.getElementById('budget-gross').textContent = budget.gross_income;
  document.getElementById('budget-duration').textContent = String(
    budget.month_duration
  );

  categoriesContainer.innerHTML = '';

  if (!budget.items || budget.items.length === 0) {
    emptyMsg.style.display = 'block';
    return;
  }
  emptyMsg.style.display = 'none';

  const container = document.getElementById('budget-categories');
  container.innerHTML = '';

  const grouped = groupItemsByCategory(budget.items);

  Object.entries(grouped).forEach(([category, data]) => {
    const accordion = buildCategoryAccordion({ category, data });
    container.appendChild(accordion);

    const collapseEl = accordion.querySelector('.accordion-collapse');
    restoreAccordionState({ budgetId, category, collapseEl });
    bindAccordionPersistence({ budgetId, category, collapseEl });
  });

  bindItemActions({
    container,
    budgetId,
    onRefresh: loadBudget,
    onEdit: async (dataset) => {
      document.getElementById('edit-item-id').value = dataset.itemId ?? '';
      document.getElementById('edit-item-name').value = dataset.itemName ?? '';
      document.getElementById('edit-item-total').value =
        dataset.itemTotal ?? '';

      await loadEditItemCategories(dataset.itemCategory);

      const modalEl = document.getElementById('editItemModal');
      bootstrap.Modal.getOrCreateInstance(modalEl).show();
    },
  });
}

/* =========================================================
   edit budget
========================================================= */
document.addEventListener('DOMContentLoaded', () => {
  const editBtn = document.getElementById('edit-budget-btn');
  if (!editBtn) return;

  editBtn.addEventListener('click', async () => {
    const budgetId = getBudgetIdFromUrl();

    if (!budgetId) {
      alert('Invalid budget.');
      return;
    }

    window.location.href = `/budget/${budgetId}/edit`;
  });
});

/* =========================================================
   delete budget
========================================================= */
document.addEventListener('DOMContentLoaded', () => {
  const deleteBtn = document.getElementById('delete-budget-btn');
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

    const res = await fetch('/api/budget/delete', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ budget_id: budgetId }),
    });

    if (!res.ok) {
      const data = await res.json();
      alert(data.message || 'Failed to delete budget.');
      return;
    }
    window.location.href = '/budgets';
  });
});

/* =========================================================
   categories
========================================================= */

async function fetchCategoriesFromApi() {
  const res = await fetch('/api/budget/item/categories', {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to load categories');
  const payload = await res.json();
  return Array.isArray(payload) ? payload : payload.categories;
}

async function loadEditItemCategories(selectedCategory) {
  const select = document.getElementById('edit-item-category');
  if (!select) return;

  const categories = await fetchCategoriesFromApi();

  // remove old options except placeholder
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
}

async function loadBudgetItemCategories() {
  const select = document.getElementById('item-category');
  if (!select) return;

  const categories = await fetchCategoriesFromApi();
  select
    .querySelectorAll('option:not(:first-child)')
    .forEach((o) => o.remove());

  categories.forEach((cat) => {
    const opt = document.createElement('option');
    opt.value = cat;
    opt.textContent = formatCategoryLabel(cat);
    select.appendChild(opt);
  });
}

/* =========================================================
   modal logic
========================================================= */

async function loadAddItemModalPartial() {
  const container = document.getElementById('add-item-modal-container');
  if (!container) return;

  const res = await fetch('/static/partials/add_item_modal.html');
  container.innerHTML = await res.text();
}

async function loadEditItemModalPartial() {
  const container = document.getElementById('edit-item-modal-container');
  if (!container) return;

  const res = await fetch('/static/partials/edit_item_modal.html');
  container.innerHTML = await res.text();
}

function setupAddItemModal() {
  const form = document.getElementById('add-item-form');
  const modalEl = document.getElementById('addItemModal');
  const errorEl = document.getElementById('add-item-error');

  if (!form || !modalEl) return;

  modalEl.addEventListener('show.bs.modal', () => {
    if (errorEl) errorEl.style.display = 'none';
    loadBudgetItemCategories();
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const budgetId = getBudgetIdFromUrl();
    if (!budgetId) return;

    const payload = {
      budget_id: budgetId,
      category: document.getElementById('item-category').value,
      name: document.getElementById('item-name').value.trim(),
      total: Number(document.getElementById('item-total').value),
    };

    const res = await fetch('/api/budget/item/create', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      errorEl.textContent = data.message || 'Failed to add item';
      errorEl.style.display = 'block';
      return;
    }

    bootstrap.Modal.getInstance(modalEl).hide();
    form.reset();
    await loadBudget();
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  const budgetId = getBudgetIdFromUrl();

  await Promise.all([loadAddItemModalPartial, loadEditItemModalPartial]);

  setupAddItemModal();
  setupEditItemModal({ budgetId, onSuccess: loadBudget });

  await loadBudget();
});

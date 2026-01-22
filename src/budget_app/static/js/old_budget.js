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
   helpers
========================================================= */

function escapeHtml(str) {
  if (typeof str !== 'string') return str;
  return str.replace(
    /[&<>"']/g,
    (m) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[
        m
      ])
  );
}

function formatCategoryLabel(cat) {
  return String(cat)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/* =========================================================
   budget loader
========================================================= */

// document.addEventListener('DOMContentLoaded', () => {
//   const deleteBtn = document.getElementById('delete-budget-btn');
//   if (!deleteBtn) return;

//   deleteBtn.addEventListener('click', async () => {
//     const budgetId = getBudgetIdFromUrl();

//     if (!budgetId) {
//       alert('Invalid budget.');
//       return;
//     }

//     const confirmed = window.confirm(
//       'Are you sure you want to delete this budget?\n\nThis action cannot be undone.'
//     );

//     if (!confirmed) return;

//     const res = await fetch('/api/budget/delete', {
//       method: 'POST',
//       credentials: 'include',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ budget_id: budgetId }),
//     });

//     if (!res.ok) {
//       const data = await res.json();
//       alert(data.message || 'Failed to delete budget.');
//       return;
//     }
//     window.location.href = '/budgets';
//   });
// });

async function loadBudget() {
  const budgetId = getBudgetIdFromUrl();
  const editLink = document.getElementById('edit-budget-link');
  editLink.href = `/budget/${budgetId}/edit`;
  const errorEl = document.getElementById('budget-error');

  if (!budgetId) {
    errorEl.textContent = 'No budget id provided.';
    return;
  }

  try {
    const res = await fetch(`/api/budget/${encodeURIComponent(budgetId)}`, {
      credentials: 'include',
    });

    if (res.status === 401) {
      window.location.href = '/login';
      return;
    }

    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Failed to load budget');

    const budget = data.budget;

    // header/meta
    document.getElementById(
      'budget-title'
    ).textContent = `Budget: "${escapeHtml(budget.name)}"`;
    document.getElementById('budget-gross').textContent = escapeHtml(
      budget.gross_income
    );
    document.getElementById('budget-duration').textContent = String(
      budget.month_duration
    );

    // items OLD
    // const ul = document.getElementById('budget-items');
    // const emptyMsg = document.getElementById('empty-budget-items');
    // ul.innerHTML = '';

    // if (!budget.items || budget.items.length === 0) {
    //   emptyMsg.style.display = 'block';
    //   return;
    // }

    // emptyMsg.style.display = 'none';

    // budget.items.forEach((item) => {
    //   const li = document.createElement('li');
    //   li.className = 'list-group-item';
    //   li.textContent = `${escapeHtml(item.name)} — ${escapeHtml(
    //     String(item.total)
    //   )}`;
    //   ul.appendChild(li);
    // });

    const emptyMsg = document.getElementById('empty-budget-items');

    const categoriesContainer = document.getElementById('budget-categories');
    categoriesContainer.innerHTML = '';

    if (!budget.items || budget.items.length === 0) {
      emptyMsg.style.display = 'block';
      return;
    }

    emptyMsg.style.display = 'none';

    // group + render accordion
    const grouped = groupItemsByCategory(budget.items);

    Object.entries(grouped).forEach(([category, data]) => {
      if (!data.items.length) return;

      const accordionItem = buildCategoryAccordion({
        category,
        data,
      });

      categoriesContainer.appendChild(accordionItem);
    });
  } catch (err) {
    console.error(err);
    if (errorEl) errorEl.textContent = err.message;
  }
}

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

/* =========================================================
   init
========================================================= */

document.addEventListener('DOMContentLoaded', async () => {
  await loadAddItemModalPartial();
  setupAddItemModal();
  await loadBudget();
});

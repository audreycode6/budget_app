import { editBudgetItem } from '../services/budget_api.js';

const ELEMENT_IDS = {
  EDIT_ITEM_MODAL: 'editItemModal',
  EDIT_ITEM_FORM: 'edit-item-form',
  EDIT_ITEM_ID: 'edit-item-id',
  ITEM_NAME: 'edit-item-name',
  ITEM_CATEGORY: 'edit-item-category',
  ITEM_TOTAL: 'edit-item-total',
};

const API_ENDPOINTS = {
  BUDGET: '/api/budget',
};

async function loadItemForEdit(itemId, budgetId) {
  const res = await fetch(
    `${API_ENDPOINTS.BUDGET}/${budgetId}/item/${itemId}`,
    {
      credentials: 'include',
    }
  );

  if (!res.ok) {
    console.error('Failed to load item');
    return;
  }

  const { item } = await res.json();

  document.getElementById(ELEMENT_IDS.ITEM_NAME).value = item.name;
  document.getElementById(ELEMENT_IDS.ITEM_CATEGORY).value = item.category;
  document.getElementById(ELEMENT_IDS.ITEM_TOTAL).value = item.total_raw;
}

export function setupEditItemModal({ budgetId, onSuccess }) {
  const modalEl = document.getElementById(ELEMENT_IDS.EDIT_ITEM_MODAL);
  const form = document.getElementById(ELEMENT_IDS.EDIT_ITEM_FORM);
  if (!modalEl || !form) return;

  modalEl.addEventListener('show.bs.modal', async (e) => {
    const itemId = Number(
      document.getElementById(ELEMENT_IDS.EDIT_ITEM_ID).value
    );
    if (itemId) {
      await loadItemForEdit(itemId, budgetId);
    }
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const itemId = Number(
      document.getElementById(ELEMENT_IDS.EDIT_ITEM_ID).value
    );
    const name = document.getElementById(ELEMENT_IDS.ITEM_NAME).value.trim();
    const category = document.getElementById(ELEMENT_IDS.ITEM_CATEGORY).value;
    const total = Number(document.getElementById(ELEMENT_IDS.ITEM_TOTAL).value);
    const payload = {
      budget_id: budgetId,
      item_id: itemId,
      name,
      category,
      total,
    };

    try {
      const res = await editBudgetItem(payload);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        alert(data.message || 'Failed to edit item');
        return;
      }

      bootstrap.Modal.getInstance(modalEl).hide();
      if (typeof onSuccess === 'function') onSuccess();
    } catch (err) {
      console.error('Edit item failed', err);
      alert('Failed to edit item.');
    }
  });
}

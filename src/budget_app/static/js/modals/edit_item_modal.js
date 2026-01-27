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

/**
 * Loads item data for editing
 * @param {number} itemId - The item ID to load
 * @param {number} budgetId - The budget ID
 * @returns {Promise<void>}
 */
async function loadItemForEdit(itemId, budgetId) {
  try {
    const res = await fetch(
      `${API_ENDPOINTS.BUDGET}/${budgetId}/item/${itemId}`,
      {
        credentials: 'include',
      },
    );

    if (!res.ok) {
      console.error('Failed to load item');
      return;
    }

    const { item } = await res.json();

    document.getElementById(ELEMENT_IDS.ITEM_NAME).value = item.name;
    document.getElementById(ELEMENT_IDS.ITEM_CATEGORY).value = item.category;
    document.getElementById(ELEMENT_IDS.ITEM_TOTAL).value = item.total;
  } catch (err) {
    console.error('Error loading item for edit:', err);
  }
}

/**
 * Sets up event handlers for the edit item modal
 * @param {Object} options - Configuration object
 * @param {number} options.budgetId - The current budget ID
 * @param {Function} options.onSuccess - Callback function on successful edit
 */
export function setupEditItemModal({ budgetId, onSuccess }) {
  const modalEl = document.getElementById(ELEMENT_IDS.EDIT_ITEM_MODAL);
  const form = document.getElementById(ELEMENT_IDS.EDIT_ITEM_FORM);
  const submitBtn = form?.querySelector('[type="submit"]');

  if (!modalEl || !form) return;

  modalEl.addEventListener('show.bs.modal', async (e) => {
    const itemId = Number(
      document.getElementById(ELEMENT_IDS.EDIT_ITEM_ID).value,
    );
    if (itemId) {
      await loadItemForEdit(itemId, budgetId);
    }
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const itemId = Number(
      document.getElementById(ELEMENT_IDS.EDIT_ITEM_ID).value,
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

    // Show loading state
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.setAttribute('aria-busy', 'true');
      submitBtn.textContent = 'Saving...';
    }

    try {
      const res = await editBudgetItem(payload);

      bootstrap.Modal.getInstance(modalEl).hide();
      if (typeof onSuccess === 'function') {
        await onSuccess();
      }
    } catch (err) {
      console.error('Edit item failed', err);
      alert(err.message || 'Failed to edit item.');
    } finally {
      // Restore button state
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.removeAttribute('aria-busy');
        submitBtn.textContent = 'Save Item';
      }
    }
  });
}

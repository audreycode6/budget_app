// static/js/modals/edit_item_modal.js
import { editBudgetItem } from '../services/budget_api.js';

export function setupEditItemModal({ budgetId, onSuccess }) {
  const modalEl = document.getElementById('editItemModal');
  const form = document.getElementById('edit-item-form');
  if (!modalEl || !form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const itemId = Number(document.getElementById('edit-item-id').value);
    const name = document.getElementById('edit-item-name').value.trim();
    const category = document.getElementById('edit-item-category').value;
    const total = Number(document.getElementById('edit-item-total').value);

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

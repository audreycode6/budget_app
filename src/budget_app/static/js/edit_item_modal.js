export function setupEditItemModal({ budgetId, onSuccess }) {
  const form = document.getElementById('edit-item-form');
  const errorEl = document.getElementById('edit-item-error');

  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
      item_id: document.getElementById('edit-item-id').value,
      name: document.getElementById('edit-item-name').value.trim(),
      category: document.getElementById('edit-item-category').value,
      total: Number(document.getElementById('edit-item-total').value),
    };

    const res = await fetch('/api/budget/item/update', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      errorEl.textContent = data.message || 'Failed to update item';
      errorEl.style.display = 'block';
      return;
    }

    bootstrap.Modal.getInstance(
      document.getElementById('editItemModal')
    ).hide();

    form.reset();
    await onSuccess();
  });
}

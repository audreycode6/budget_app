import { deleteBudgetItem } from '../services/budget_api.js';

export function bindItemActions({ container, budgetId, onRefresh, onEdit }) {
  if (!container) return;

  if (container.dataset.itemActionsBound === 'true') return;
  container.dataset.itemActionsBound = 'true';

  container.addEventListener('click', async (e) => {
    const editBtn = e.target.closest('.item-edit');
    if (editBtn) {
      onEdit({
        itemId: editBtn.dataset.itemId,
        itemName: editBtn.dataset.itemName,
        itemTotal: editBtn.dataset.itemTotal,
        itemCategory: editBtn.dataset.itemCategory,
      });
      return;
    }

    const deleteBtn = e.target.closest('.item-delete');
    if (!deleteBtn) return;

    const confirmed = window.confirm(
      'Delete this item?\n\nThis cannot be undone.',
    );
    if (!confirmed) return;

    const itemId = Number(deleteBtn.dataset.itemId);

    deleteBtn.disabled = true;
    deleteBtn.setAttribute('aria-busy', 'true');
    const originalText = deleteBtn.textContent;
    deleteBtn.textContent = 'Deleting...';

    try {
      await deleteBudgetItem({ budgetId, itemId });

      // Refresh the budget view
      await onRefresh();
    } catch (err) {
      console.error('Delete failed', err);
      alert('Failed to delete item.');

      // Restore button state on error
      deleteBtn.disabled = false;
      deleteBtn.removeAttribute('aria-busy');
      deleteBtn.textContent = originalText;
    }
  });
}

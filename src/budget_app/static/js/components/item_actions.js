// import { deleteBudgetItem } from '../services/budget_api.js';

// export function bindItemActions({ container, budgetId, onRefresh, onEdit }) {
//   if (!container) return;

//   if (container.dataset.itemActionsBound === 'true') return;
//   container.dataset.itemActionsBound = 'true';

//   container.addEventListener('click', async (e) => {
//     const editBtn = e.target.closest('.item-edit');
//     if (editBtn) {
//       onEdit({
//         itemId: editBtn.dataset.itemId,
//         itemName: editBtn.dataset.itemName,
//         itemTotal: editBtn.dataset.itemTotal,
//         itemCategory: editBtn.dataset.itemCategory,
//       });
//       return;
//     }

//     const deleteBtn = e.target.closest('.item-delete');
//     if (!deleteBtn) return;

//     if (!confirm('Delete this item? This cannot be undone.')) return;

//     const itemId = Number(deleteBtn.dataset.itemId);
//     try {
//       const res = await deleteBudgetItem({ budgetId, itemId });
//       if (!res.ok) {
//         const data = await res.json().catch(() => ({}));
//         alert(data.message || 'Failed to delete item');
//         return;
//       }
//       onRefresh();
//     } catch (err) {
//       console.error('Delete failed', err);
//       alert('Failed to delete item.');
//     }
//   });
// }

import { deleteBudgetItem } from '../services/budget_api.js';

export function bindItemActions({ container, budgetId, onRefresh, onEdit }) {
  if (!container) return;

  // ✅ PREVENT MULTIPLE BINDINGS
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
      'Delete this item?\n\nThis cannot be undone.'
    );
    if (!confirmed) return;

    const itemId = Number(deleteBtn.dataset.itemId);

    try {
      const res = await deleteBudgetItem({ budgetId, itemId });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        alert(data.message || 'Failed to delete item');
        return;
      }

      await onRefresh();
    } catch (err) {
      console.error('Delete failed', err);
      alert('Failed to delete item.');
    }
  });
}

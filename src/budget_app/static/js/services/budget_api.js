export async function fetchBudget(budgetId) {
  const res = await fetch(`/api/budget/${encodeURIComponent(budgetId)}`, {
    credentials: 'include',
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.message || 'Failed to load budget');
  }
  return res.json();
}

export async function deleteBudgetItem({ budgetId, itemId }) {
  return fetch('/api/budget/item/delete', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ budget_id: budgetId, item_id: itemId }),
  });
}

export async function editBudgetItem(payload) {
  return fetch('/api/budget/item/edit', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

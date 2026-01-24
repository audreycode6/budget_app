const API_ENDPOINTS = {
  BUDGET: '/api/budget',
  ITEM_DELETE: '/api/budget/item/delete',
  ITEM_EDIT: '/api/budget/item/edit',
};

/**
 * Fetch a single budget with all its items
 * @param {string|number} budgetId - The budget ID to fetch
 * @returns {Promise<object>} Budget object with items
 * @throws {Error} If the request fails
 */
export async function fetchBudget(budgetId) {
  const res = await fetch(
    `${API_ENDPOINTS.BUDGET}/${encodeURIComponent(budgetId)}`,
    {
      credentials: 'include',
    }
  );

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.message || 'Failed to load budget');
  }

  return res.json();
}

/**
 * Delete a budget item
 * @param {object} params - { budgetId: string|number, itemId: string|number }
 * @returns {Promise<object>} Response data from server
 * @throws {Error} If the request fails
 */
export async function deleteBudgetItem({ budgetId, itemId }) {
  const res = await fetch(API_ENDPOINTS.ITEM_DELETE, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ budget_id: budgetId, item_id: itemId }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.message || 'Failed to delete item');
  }

  return res.json();
}

/**
 * Edit an existing budget item
 * @param {object} payload - Item data to update (must include item_id and budget_id)
 * @returns {Promise<object>} Updated item from server
 * @throws {Error} If the request fails
 */
export async function editBudgetItem(payload) {
  const res = await fetch(API_ENDPOINTS.ITEM_EDIT, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.message || 'Failed to edit item');
  }

  return res.json();
}

import { getBudgetIdFromUrl } from './utils/url.js';

async function loadBudgetForEdit() {
  const budgetId = getBudgetIdFromUrl();

  if (!budgetId) {
    document.getElementById('error').textContent = 'Invalid budget URL';
    return;
  }

  const res = await fetch(`/api/budget/${budgetId}`, {
    credentials: 'include',
  });

  if (!res.ok) {
    document.getElementById('error').textContent = 'Failed to load budget';
    return;
  }

  const { budget } = await res.json();

  document.getElementById('name').value = budget.name;
  document.getElementById('gross_income_raw').value = budget.gross_income_raw;
  document.getElementById('month_duration').value = budget.month_duration;

  document.getElementById('cancel-link').href = `/budget/${budgetId}`;
}

async function submitEdit(e) {
  e.preventDefault();

  const budgetId = getBudgetIdFromUrl();

  const body = {
    budget_id: budgetId,
    name: document.getElementById('name').value,
    gross_income: parseFloat(document.getElementById('gross_income_raw').value),
    month_duration: document.getElementById('month_duration').value,
  };

  const res = await fetch('/api/budget/edit', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const data = await res.json();
    document.getElementById('error').textContent =
      data.message || 'Edit failed';
    return;
  }
  window.location.href = `/budget/${budgetId}`;
}

document.addEventListener('DOMContentLoaded', () => {
  loadBudgetForEdit();
  document
    .getElementById('edit-budget-form')
    .addEventListener('submit', submitEdit);
});
